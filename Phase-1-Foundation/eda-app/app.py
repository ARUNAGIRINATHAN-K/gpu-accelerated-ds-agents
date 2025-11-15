from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
from werkzeug.utils import secure_filename
import json
from datetime import datetime
import numpy as np
import math

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Keep the last analyzed summary in memory for the UI page
LAST_SUMMARY = None

ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_dataset(file_path):
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    # Basic Info
    total_rows, total_cols = df.shape
    column_names = df.columns.tolist()
    data_types = df.dtypes.astype(str).to_dict()
    missing_values = df.isnull().sum().to_dict()
    unique_counts = df.nunique().to_dict()
    sample_data = df.head(5).to_dict(orient='records')

    summary = {
        "shape": [total_rows, total_cols],
        "columns": column_names,
        "data_types": data_types,
        "missing_values": missing_values,
        "unique_counts": unique_counts,
        "sample_data": sample_data,
        "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB"
    }
    # Convert summary to JSON-serializable types (numpy/pandas -> native Python)
    def make_serializable(obj):
        if obj is None:
            return None
        if isinstance(obj, dict):
            return {str(k): make_serializable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [make_serializable(v) for v in obj]
        # pandas / numpy NA
        try:
            if pd.isna(obj):
                return None
        except Exception:
            pass
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            # Convert NaN to None
            if math.isnan(obj):
                return None
            return float(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, (int, float, str, bool)):
            return obj
        # fallback to string
        return str(obj)

    serial_summary = make_serializable(summary)
    return serial_summary, df

def generate_html_report(summary, df):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>EDA Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>body {{ margin: 40px; }}</style>
    </head>
    <body>
        <div class="container">
            <h1 class="text-center mb-4">Exploratory Data Analysis Report</h1>
            <p class="text-muted text-center">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

            <div class="card mb-3">
                <div class="card-body">
                    <h5>Dataset Overview</h5>
                    <p><strong>Rows:</strong> {summary['shape'][0]} | <strong>Columns:</strong> {summary['shape'][1]}</p>
                    <p><strong>Memory Usage:</strong> {summary['memory_usage']}</p>
                </div>
            </div>

            <h5>Column Details</h5>
            <table class="table table-bordered table-striped">
                <thead class="table-dark">
                    <tr>
                        <th>Column</th>
                        <th>Type</th>
                        <th>Missing</th>
                        <th>Unique</th>
                    </tr>
                </thead>
                <tbody>
    """
    for col in summary['columns']:
        html += f"""
                    <tr>
                        <td>{col}</td>
                        <td>{summary['data_types'][col]}</td>
                        <td>{summary['missing_values'][col]}</td>
                        <td>{summary['unique_counts'][col]}</td>
                    </tr>
        """
    html += """
                </tbody>
            </table>

            <h5 class="mt-4">Sample Data (First 5 Rows)</h5>
            <table class="table table-sm table-bordered">
                <thead class="table-light">
                    <tr>
    """
    for col in summary['columns']:
        html += f"<th>{col}</th>"
    html += """
                    </tr>
                </thead>
                <tbody>
    """
    for row in summary['sample_data']:
        html += "<tr>"
        for val in row.values():
            html += f"<td>{val}</td>"
        html += "</tr>"
    html += """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/')
def index():
    # Serve the summary UI as the main app page
    return render_template('summary.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            summary, df = analyze_dataset(filepath)
            # add some file info
            try:
                size_bytes = os.path.getsize(filepath)
                # human readable
                for unit in ['B','KB','MB','GB']:
                    if size_bytes < 1024.0:
                        size_readable = f"{size_bytes:.2f} {unit}"
                        break
                    size_bytes /= 1024.0
                else:
                    size_readable = f"{size_bytes:.2f} TB"
            except Exception:
                size_readable = 'Unknown'
            summary['file_info'] = { 'filename': filename, 'size_readable': size_readable }

            # store last summary for the summary-view page
            global LAST_SUMMARY
            LAST_SUMMARY = summary
            return jsonify({
                "success": True,
                "summary": summary
            })
        except Exception as e:
            return jsonify({"error": f"Error processing file: {str(e)}"}), 500
    else:
        return jsonify({"error": "Invalid file type. Only .csv and .xlsx allowed."}), 400

@app.route('/report', methods=['POST'])
def generate_report():
    data = request.json
    summary = data['summary']
    # Re-read file to generate full report
    filename = data['filename']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    
    _, df = analyze_dataset(filepath)
    html_report = generate_html_report(summary, df)
    
    report_path = os.path.join(app.config['UPLOAD_FOLDER'], 'EDA_Report.html')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    return send_file(report_path, as_attachment=True, download_name=f"EDA_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")


@app.route('/summary-view')
def summary_view():
    return render_template('summary.html')


@app.route('/summary-data')
def summary_data():
    if LAST_SUMMARY is None:
        return jsonify({"error": "No summary available. Upload a file first."}), 404
    return jsonify({"success": True, "summary": LAST_SUMMARY})

if __name__ == '__main__':
    app.run(debug=True)