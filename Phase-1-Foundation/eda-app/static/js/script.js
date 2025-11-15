const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const errorAlert = document.getElementById('error-alert');
const downloadBtn = document.getElementById('download-report');

let currentSummary = null;
let currentFilename = null;

// Drag & Drop
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
  dropzone.addEventListener(eventName, preventDefaults, false);
});
function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}
['dragenter', 'dragover'].forEach(eventName => {
  dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'), false);
});
['dragleave', 'drop'].forEach(eventName => {
  dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'), false);
});
dropzone.addEventListener('drop', handleDrop, false);
dropzone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', () => handleFiles(fileInput.files));

function handleDrop(e) {
  const dt = e.dataTransfer;
  const files = dt.files;
  handleFiles(files);
}

function handleFiles(files) {
  if (files.length === 0) return;
  const file = files[0];
  if (!file.name.match(/\.(csv|xlsx)$/i)) {
    showError("Please upload a .csv or .xlsx file.");
    return;
  }
  if (file.size > 10 * 1024 * 1024) {
    showError("File size must be under 10MB.");
    return;
  }
  uploadFile(file);
}

function uploadFile(file) {
  hideError();
  loading.classList.remove('d-none');
  results.classList.add('d-none');

  const formData = new FormData();
  formData.append('file', file);

  fetch('/upload', {
    method: 'POST',
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    loading.classList.add('d-none');
    if (data.success) {
      currentSummary = data.summary;
      currentFilename = file.name;
      displayResults(data.summary);
      results.classList.remove('d-none');
    } else {
      showError(data.error || "Unknown error");
    }
  })
  .catch(err => {
    loading.classList.add('d-none');
    showError("Network error. Please try again.");
  });
}

function displayResults(summary) {
  // Summary Info
  document.getElementById('summary-info').innerHTML = `
    <p><strong>Rows:</strong> ${summary.shape[0]} | <strong>Columns:</strong> ${summary.shape[1]}</p>
    <p><strong>Memory:</strong> ${summary.memory_usage}</p>
  `;

  // Columns Table
  const cols = summary.columns;
  let colHtml = `
    <thead class="table-light">
      <tr><th>Column</th><th>Type</th><th>Missing</th><th>Unique</th></tr>
    </thead><tbody>
  `;
  cols.forEach(col => {
    colHtml += `
      <tr>
        <td>${col}</td>
        <td><code>${summary.data_types[col]}</code></td>
        <td><span class="badge bg-warning">${summary.missing_values[col]}</span></td>
        <td>${summary.unique_counts[col]}</td>
      </tr>
    `;
  });
  colHtml += `</tbody>`;
  document.getElementById('columns-table').innerHTML = colHtml;

  // Sample Data
  let sampleHtml = `<thead class="table-light"><tr>`;
  cols.forEach(col => sampleHtml += `<th>${col}</th>`);
  sampleHtml += `</tr></thead><tbody>`;
  summary.sample_data.forEach(row => {
    sampleHtml += `<tr>`;
    cols.forEach(col => {
      sampleHtml += `<td>${row[col] !== null ? row[col] : '<em>null</em>'}</td>`;
    });
    sampleHtml += `</tr>`;
  });
  sampleHtml += `</tbody>`;
  document.getElementById('sample-table').innerHTML = sampleHtml;

  // Download Report
  downloadBtn.onclick = () => {
    fetch('/report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ summary: currentSummary, filename: currentFilename })
    })
    .then(res => res.blob())
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `EDA_Report_${new Date().toISOString().slice(0,19).replace(/:/g,'')}.html`;
      a.click();
    });
  };
}

function showError(msg) {
  errorAlert.textContent = msg;
  errorAlert.classList.remove('d-none');
}
function hideError() {
  errorAlert.classList.add('d-none');
}