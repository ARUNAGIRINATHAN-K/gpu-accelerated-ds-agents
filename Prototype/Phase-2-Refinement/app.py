import base64
import io
import math
import os
from datetime import datetime

import matplotlib
# Use a non-GUI backend for server-side rendering
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB max

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Keep the last analyzed summary in memory for the UI page
LAST_SUMMARY = None

ALLOWED_EXTENSIONS = {"csv", "xlsx"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def analyze_dataset(file_path):
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    # Basic Info
    total_rows, total_cols = df.shape
    column_names = df.columns.tolist()
    data_types = df.dtypes.astype(str).to_dict()
    missing_values = df.isnull().sum().to_dict()
    unique_counts = df.nunique().to_dict()
    sample_data = df.head(5).to_dict(orient="records")

    # Descriptive Statistics for numerical columns
    descriptive_stats = {}
    for col in df.select_dtypes(include=np.number).columns:
        descriptive_stats[col] = {
            "mean": df[col].mean(),
            "median": df[col].median(),
            "mode": df[col].mode().iloc[0]
            if not df[col].mode().empty
            else "N/A",
            "std_dev": df[col].std(),
        }

    summary = {
        "shape": [total_rows, total_cols],
        "columns": column_names,
        "data_types": data_types,
        "missing_values": missing_values,
        "unique_counts": unique_counts,
        "sample_data": sample_data,
        "descriptive_stats": descriptive_stats,
        "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB",
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


@app.route("/charts", methods=["POST"])
def generate_charts():
    data = request.json
    filename = data["filename"]
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404

    _, df = analyze_dataset(filepath)

    charts = {}

    # Generate varied charts for each column
    for col in df.columns:
        charts[col] = {}
        try:
            if pd.api.types.is_numeric_dtype(df[col]):
                series = df[col].dropna()
                # Histogram
                plt.figure(figsize=(10, 6))
                if not series.empty:
                    series.plot(kind="hist", bins=20, title=f"Histogram of {col}")
                else:
                    plt.text(0.5, 0.5, f"No numeric data in {col}", ha='center')
                img = io.BytesIO(); plt.tight_layout(); plt.savefig(img, format="png"); img.seek(0)
                charts[col]["histogram"] = base64.b64encode(img.getvalue()).decode(); plt.close()

                # Boxplot
                plt.figure(figsize=(6, 6))
                if not series.empty:
                    plt.boxplot(series, vert=True)
                    plt.title(f"Boxplot of {col}")
                else:
                    plt.text(0.5, 0.5, f"No numeric data in {col}", ha='center')
                img = io.BytesIO(); plt.tight_layout(); plt.savefig(img, format="png"); img.seek(0)
                charts[col]["boxplot"] = base64.b64encode(img.getvalue()).decode(); plt.close()
            else:
                # Categorical charts
                vc = df[col].fillna('NaN').astype(str).value_counts()
                if not vc.empty:
                    # Horizontal bar (top 20)
                    plt.figure(figsize=(10, 6))
                    vc.head(20)[::-1].plot(kind="barh", title=f"Top 20 of {col}")
                    img = io.BytesIO(); plt.tight_layout(); plt.savefig(img, format="png"); img.seek(0)
                    charts[col]["barh"] = base64.b64encode(img.getvalue()).decode(); plt.close()

                    # Pie chart when categories are small
                    if len(vc) <= 8:
                        plt.figure(figsize=(7, 7))
                        vc.plot(kind="pie", autopct='%1.1f%%', title=f"Distribution of {col}")
                        plt.ylabel("")
                        img = io.BytesIO(); plt.tight_layout(); plt.savefig(img, format="png"); img.seek(0)
                        charts[col]["pie"] = base64.b64encode(img.getvalue()).decode(); plt.close()
        except Exception:
            # Skip problematic columns quietly
            plt.close('all')

    # Generate correlation heatmap
    numerical_cols = df.select_dtypes(include=np.number).columns
    if len(numerical_cols) > 1:
        plt.figure(figsize=(12, 10))
        correlation = df[numerical_cols].corr()
        plt.matshow(correlation, fignum=1)
        plt.xticks(range(len(numerical_cols)), numerical_cols, rotation=90)
        plt.yticks(range(len(numerical_cols)), numerical_cols)
        plt.colorbar()
        plt.title("Correlation Heatmap", pad=20)

        img = io.BytesIO()
        plt.tight_layout()
        plt.savefig(img, format="png")
        img.seek(0)
        charts["correlation_heatmap"] = base64.b64encode(img.getvalue()).decode()
        plt.close()

        # Scatter plots for top correlated pairs (up to 3)
        try:
            corr_abs = correlation.abs()
            # Get upper triangle without diagonal
            pairs = []
            cols = list(numerical_cols)
            for i in range(len(cols)):
                for j in range(i+1, len(cols)):
                    pairs.append((cols[i], cols[j], corr_abs.iloc[i, j]))
            pairs.sort(key=lambda x: x[2], reverse=True)
            for c1, c2, _ in pairs[:3]:
                plt.figure(figsize=(8, 6))
                sub = df[[c1, c2]].dropna()
                if not sub.empty:
                    plt.scatter(sub[c1], sub[c2], alpha=0.6)
                    plt.xlabel(c1); plt.ylabel(c2); plt.title(f"Scatter: {c1} vs {c2}")
                else:
                    plt.text(0.5, 0.5, f"No data for {c1} and {c2}", ha='center')
                img = io.BytesIO(); plt.tight_layout(); plt.savefig(img, format="png"); img.seek(0)
                charts[f"scatter__{c1}__{c2}"] = base64.b64encode(img.getvalue()).decode(); plt.close()
        except Exception:
            plt.close('all')

    return jsonify({"success": True, "charts": charts})


@app.route("/")
def index():
    # Serve the summary UI as the main app page
    return render_template("summary.html")


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




@app.route('/summary-view')
def summary_view():
    return render_template('summary.html')


@app.route('/summary-data')
def summary_data():
    if LAST_SUMMARY is None:
        return jsonify({"error": "No summary available. Upload a file first."}), 404
    return jsonify({"success": True, "summary": LAST_SUMMARY})


@app.route("/favicon.ico")
def favicon():
    # Serve the logo in templates/icon as the site favicon so we don't need to move files
    favicon_path = os.path.join(app.root_path, "templates", "icon", "logo.png")
    if os.path.exists(favicon_path):
        return send_file(favicon_path, mimetype="image/png")
    # fallback: empty response
    return ("", 404)


if __name__ == '__main__':
    app.run(debug=True)