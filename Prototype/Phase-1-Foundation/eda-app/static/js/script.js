const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const errorAlert = document.getElementById('error-alert');
const downloadBtn = document.getElementById('download-report');
const analyzeRedirectBtn = document.getElementById('analyze-redirect');

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
  // Use robust fetch with timeout / retries
  fetchWithTimeoutAndRetries('/upload', { method: 'POST', body: formData }, 30000, 2)
    .then(data => {
      loading.classList.add('d-none');
      if (data && data.success) {
        currentSummary = data.summary;
        currentFilename = file.name;
        displayResults(data.summary);
        results.classList.remove('d-none');
      } else if (typeof data === 'string') {
        // server returned non-JSON text
        try {
          const parsed = JSON.parse(data);
          if (parsed && parsed.success) {
            currentSummary = parsed.summary;
            currentFilename = file.name;
            displayResults(parsed.summary);
            results.classList.remove('d-none');
            return;
          }
          showError(parsed.error || parsed.message || data || 'Unexpected server response');
        } catch (e) {
          showError(data || 'Unexpected server response');
        }
      } else {
        showError((data && data.error) || 'Unexpected server response');
      }
    })
    .catch(err => {
      loading.classList.add('d-none');
      console.error('Upload error:', err);
      if (!navigator.onLine) {
        showError('No network connection. Please check your internet and try again.');
      } else {
        showError(err.message || 'Network error. Please try again.');
      }
    });
}

function displayResults(summary) {
  // populate top summary cards if present
  try {
    const colsEl = document.getElementById('card-columns');
    const rowsEl = document.getElementById('card-rows');
    const missEl = document.getElementById('card-missing');
    const sizeEl = document.getElementById('card-size');
    if (colsEl) colsEl.textContent = summary.shape ? summary.shape[1] : (summary.columns ? summary.columns.length : '-');
    if (rowsEl) rowsEl.textContent = summary.shape ? summary.shape[0].toLocaleString() : '-';
    if (missEl) {
      const totalMissing = Object.values(summary.missing_values || {}).reduce((s,v)=>s+(Number(v)||0),0);
      missEl.textContent = totalMissing.toLocaleString();
    }
    if (sizeEl) sizeEl.textContent = summary.file_info ? summary.file_info.size_readable : '-';
  } catch (e) {
    console.warn('Could not populate top cards:', e);
  }

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
      const val = row[col];
      const isMissing = val === null || val === undefined || (typeof val === 'number' && isNaN(val));
      sampleHtml += `<td>${isMissing ? '<em>null</em>' : escapeHtml(String(val))}</td>`;
    });
    sampleHtml += `</tr>`;
  });
  sampleHtml += `</tbody>`;
  document.getElementById('sample-table').innerHTML = sampleHtml;

// basic escape to avoid HTML injection from CSV content
function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

  // Download Report
  downloadBtn.onclick = () => {
    const payload = { summary: currentSummary, filename: currentFilename };
    fetchBlobWithTimeoutAndRetries('/report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }, 30000, 1)
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `EDA_Report_${new Date().toISOString().slice(0,19).replace(/:/g,'')}.html`;
        a.click();
      })
      .catch(err => {
        console.error('Report download error:', err);
        if (!navigator.onLine) {
          showError('No network connection. Please check your internet and try again.');
        } else {
          showError(err.message || 'Failed to generate report. Please try again.');
        }
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

/*
  Helper: fetch with timeout and simple retry + safer response parsing.
  - timeout: ms
  - retries: number of retry attempts (0 = no retry)
*/
async function fetchWithTimeoutAndRetries(url, options = {}, timeout = 30000, retries = 0) {
  let lastErr;
  for (let attempt = 0; attempt <= retries; attempt++) {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    // clone options so we don't mutate caller's object across retries
    const reqOptions = Object.assign({}, options, { signal: controller.signal });
    try {
      const res = await fetch(url, reqOptions);
      clearTimeout(id);

      // read body as text first so we can attempt JSON parse but still get useful text on failure
      const text = await res.text();
      try {
        const json = text ? JSON.parse(text) : null;
        if (!res.ok) {
          throw new Error((json && (json.error || json.message)) || `Server error ${res.status} ${res.statusText}`);
        }
        return json;
      } catch (parseErr) {
        if (!res.ok) {
          const trimmed = (text || '').trim();
          throw new Error(trimmed ? trimmed : `Server error ${res.status} ${res.statusText}`);
        }
        return text;
      }
    } catch (err) {
      clearTimeout(id);
      lastErr = err;
      if ((err.name === 'AbortError' || (err.message && err.message.toLowerCase().includes('timeout'))) && attempt < retries) continue;
      if (attempt < retries) continue;
      throw err;
    }
  }
  throw lastErr || new Error('Unknown network error');
}

async function fetchBlobWithTimeoutAndRetries(url, options = {}, timeout = 30000, retries = 0) {
  let lastErr;
  for (let attempt = 0; attempt <= retries; attempt++) {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    const reqOptions = Object.assign({}, options, { signal: controller.signal });
    try {
      const res = await fetch(url, reqOptions);
      clearTimeout(id);
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Server error ${res.status} ${res.statusText}`);
      }
      const blob = await res.blob();
      return blob;
    } catch (err) {
      clearTimeout(id);
      lastErr = err;
      if ((err.name === 'AbortError' || (err.message && err.message.toLowerCase().includes('timeout'))) && attempt < retries) continue;
      if (attempt < retries) continue;
      throw err;
    }
  }
  throw lastErr || new Error('Unknown network error');
}

// Analyze button: if already uploaded -> go to summary view, else upload then redirect
if (analyzeRedirectBtn) {
  analyzeRedirectBtn.addEventListener('click', async () => {
    // if we already have a summary (upload done), just redirect
    if (currentSummary && currentFilename) {
      window.location.href = '/summary-view';
      return;
    }

    // otherwise, upload selected file (if any) and then redirect
    const inputFile = fileInput.files && fileInput.files[0];
    if (!inputFile) {
      showError('Please select a file before viewing the full summary.');
      return;
    }

    hideError();
    loading.classList.remove('d-none');
    try {
      const formData = new FormData();
      formData.append('file', inputFile);
      const data = await fetchWithTimeoutAndRetries('/upload', { method: 'POST', body: formData }, 30000, 2);
      loading.classList.add('d-none');
      if (data && data.success) {
        currentSummary = data.summary;
        currentFilename = inputFile.name;
        // redirect to summary page which will fetch the saved server summary
        window.location.href = '/summary-view';
      } else {
        showError((data && data.error) || 'Unexpected server response');
      }
    } catch (err) {
      loading.classList.add('d-none');
      console.error('Analyze upload error:', err);
      showError(err.message || 'Upload failed. Please try again.');
    }
  });
}