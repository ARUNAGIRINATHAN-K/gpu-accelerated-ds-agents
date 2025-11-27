async function fetchSummary() {
  try {
    const res = await fetch('/summary-data');
    if (!res.ok) throw new Error(`Server returned ${res.status}`);
    const payload = await res.json();
    if (!payload.success) throw new Error(payload.error || 'No summary');
    return payload.summary;
  } catch (err) {
    console.error('Failed to fetch summary:', err);
    return null;
  }
}

function humanNumber(n) {
  return n.toLocaleString();
}

function populateCards(summary) {
  document.getElementById('card-columns').textContent = summary.shape[1];
  document.getElementById('card-rows').textContent = humanNumber(summary.shape[0]);
  const totalMissing = Object.values(summary.missing_values || {}).reduce((s,v)=>s+(Number(v)||0),0);
  document.getElementById('card-missing').textContent = humanNumber(totalMissing);
  document.getElementById('card-size').textContent = summary.file_info ? summary.file_info.size_readable : '-';
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function buildTable(summary) {
  const cols = summary.columns || [];
  const rows = cols.map((col) => {
    const dtype = summary.data_types ? summary.data_types[col] || "" : "";
    const missing = summary.missing_values
      ? summary.missing_values[col] || 0
      : 0;
    const unique = summary.unique_counts
      ? summary.unique_counts[col] || 0
      : 0;
    const stats = summary.descriptive_stats
      ? summary.descriptive_stats[col] || {}
      : {};
    return [
      col,
      String(dtype),
      String(missing),
      String(unique),
      stats.mean ? stats.mean.toFixed(2) : "N/A",
      stats.median ? stats.median.toFixed(2) : "N/A",
      stats.std_dev ? stats.std_dev.toFixed(2) : "N/A",
    ];
  });

  // If DataTable is already initialized, update via API for reliability
  try {
    if (
      dataTableInstance &&
      $.fn.dataTable &&
      $.fn.dataTable.isDataTable("#columns-table")
    ) {
      dataTableInstance.clear();
      dataTableInstance.rows.add(rows);
      dataTableInstance.draw(false);
      return;
    }
  } catch (e) {
    console.warn("DataTable update failed, falling back to DOM rebuild", e);
  }

  // Fallback: build plain tbody
  const tbody = document.querySelector("#columns-table tbody");
  tbody.innerHTML = "";
  rows.forEach((r) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${escapeHtml(r[0])}</td>
      <td>${escapeHtml(r[1])}</td>
      <td>${escapeHtml(r[2])}</td>
      <td>${escapeHtml(r[3])}</td>
      <td>${escapeHtml(r[4])}</td>
      <td>${escapeHtml(r[5])}</td>
      <td>${escapeHtml(r[6])}</td>
    `;
    tbody.appendChild(tr);
  });
}

function summaryToRows(summary) {
  const cols = summary.columns || [];
  return cols.map((col) => {
    const dtype = summary.data_types ? summary.data_types[col] || "" : "";
    const missing = summary.missing_values ? summary.missing_values[col] || 0 : 0;
    const unique = summary.unique_counts ? summary.unique_counts[col] || 0 : 0;
    const stats = summary.descriptive_stats ? summary.descriptive_stats[col] || {} : {};
    return [
      col,
      String(dtype),
      String(missing),
      String(unique),
      stats.mean ? Number(stats.mean).toFixed(2) : "N/A",
      stats.median ? Number(stats.median).toFixed(2) : "N/A",
      stats.std_dev ? Number(stats.std_dev).toFixed(2) : "N/A",
    ];
  });
}


async function displayCharts(filename) {
  const chartsContainer = document.getElementById("charts-container");
  const chartsSection = document.getElementById("charts-section");
  const MAX_CHARTS = 4; // display at most 4 charts (2x2)

  try {
    const res = await fetch("/charts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filename, limit: MAX_CHARTS }),
    });
    if (!res.ok) throw new Error(`Server returned ${res.status}`);
    const payload = await res.json();
    if (!payload.success) throw new Error(payload.error || "Chart generation failed");

    chartsSection.style.display = "block";
    let chartsHtml = "";
    const charts = payload.charts || {};
    let count = 0;
    const usedKeys = new Set();

    // 1) Correlation heatmap first (if present)
    if (charts.correlation_heatmap && count < MAX_CHARTS) {
      chartsHtml += `
        <div class="col-12 col-md-6 mb-4">
          <div class="card shadow-sm h-100">
            <div class="card-body d-flex flex-column">
              <h5 class="card-title">Correlation Heatmap</h5>
              <img src="data:image/png;base64,${charts.correlation_heatmap}" class="img-fluid rounded mt-auto">
            </div>
          </div>
        </div>`;
      count += 1;
      usedKeys.add('correlation_heatmap');
    }

    // 2) One scatter plot for strongest pair (if available)
    if (count < MAX_CHARTS) {
      const scatterKey = Object.keys(charts).find(k => k.startsWith('scatter__'));
      if (scatterKey) {
        const title = scatterKey.replace('scatter__','').replace(/__/g, ' vs ');
        chartsHtml += `
          <div class="col-12 col-md-6 mb-4">
            <div class="card shadow-sm h-100">
              <div class="card-body d-flex flex-column">
                <h5 class="card-title">${title}</h5>
                <img src="data:image/png;base64,${charts[scatterKey]}" class="img-fluid rounded mt-auto">
              </div>
            </div>
          </div>`;
        count += 1;
        usedKeys.add(scatterKey);
      }
    }

    // 3) One numeric chart (histogram preferred, else boxplot)
    if (count < MAX_CHARTS) {
      const candidates = Object.keys(charts).filter(k => !k.startsWith('scatter__') && k !== 'correlation_heatmap');
      const numericEntry = candidates.map(k => [k, charts[k]]).find(([_, v]) => v && typeof v === 'object' && (v.histogram || v.boxplot));
      if (numericEntry) {
        const [key, v] = numericEntry;
        const title = key.replace(/_/g, ' ');
        const type = v.histogram ? 'histogram' : 'boxplot';
        chartsHtml += `
          <div class="col-12 col-md-6 mb-4">
            <div class="card shadow-sm h-100">
              <div class="card-body d-flex flex-column">
                <h5 class="card-title">${title} (${type})</h5>
                <img src="data:image/png;base64,${v[type]}" class="img-fluid rounded mt-auto">
              </div>
            </div>
          </div>`;
        count += 1;
        usedKeys.add(key);
      }
    }

    // 4) One categorical chart (barh preferred, else pie)
    if (count < MAX_CHARTS) {
      const candidates = Object.keys(charts).filter(k => !k.startsWith('scatter__') && k !== 'correlation_heatmap');
      const catEntry = candidates.map(k => [k, charts[k]]).find(([_, v]) => v && typeof v === 'object' && (v.barh || v.pie));
      if (catEntry) {
        const [key, v] = catEntry;
        const title = key.replace(/_/g, ' ');
        const type = v.barh ? 'barh' : 'pie';
        chartsHtml += `
          <div class="col-12 col-md-6 mb-4">
            <div class="card shadow-sm h-100">
              <div class="card-body d-flex flex-column">
                <h5 class="card-title">${title} (${type})</h5>
                <img src="data:image/png;base64,${v[type]}" class="img-fluid rounded mt-auto">
              </div>
            </div>
          </div>`;
        count += 1;
        usedKeys.add(key);
      }
    }

    // Fallback: fill remaining slots with any charts left until 2x2 is full
    if (count < MAX_CHARTS) {
      const keys = Object.keys(charts).filter(k => !usedKeys.has(k));
      for (const key of keys) {
        if (count >= MAX_CHARTS) break;
        const value = charts[key];
        let img = null;
        let label = key.replace(/_/g, ' ');
        if (typeof value === 'string') {
          img = value;
        } else if (value && typeof value === 'object') {
          // pick any available type deterministically
          const pref = ['histogram','boxplot','barh','pie'];
          const t = pref.find(p => value[p]);
          if (t) {
            img = value[t];
            label = `${label} (${t})`;
          }
        }
        if (img) {
          chartsHtml += `
            <div class="col-12 col-md-6 mb-4">
              <div class="card shadow-sm h-100">
                <div class="card-body d-flex flex-column">
                  <h5 class="card-title">${label}</h5>
                  <img src="data:image/png;base64,${img}" class="img-fluid rounded mt-auto">
                </div>
              </div>
            </div>`;
          count += 1;
        }
      }
    }

    if (!chartsHtml) {
      chartsHtml = `<div class="col-12"><div class="alert alert-info">No charts could be generated for this dataset.</div></div>`;
    }

    chartsContainer.innerHTML = chartsHtml;
  } catch (err) {
    console.error("Failed to fetch charts:", err);
    chartsSection.style.display = "none";
  }
}

async function uploadFileAndRefresh(file) {
  const status = document.getElementById('upload-status');
  status.textContent = 'Uploading... please wait, this may take a moment...';
  const form = new FormData();
  form.append('file', file);
  try {
    const res = await fetch('/upload', { method: 'POST', body: form });
    const text = await res.text();
    let payload;
    try {
      payload = text ? JSON.parse(text) : null;
    } catch (e) {
      payload = text;
    }
    if (!res.ok) {
      const msg =
        payload && payload.error ? payload.error : `Server error ${res.status}`;
      status.textContent = msg;
      status.classList.add('text-danger');
      return null;
    }
    if (payload && payload.success) {
      status.textContent = 'Analysis complete';
      status.classList.remove('text-danger');

      // Populate UI with new summary
      populateCards(payload.summary);
      buildTable(payload.summary);
      populateTypeFilter(payload.summary);
      // Outliers feature removed; charts will be rendered below
      await displayCharts(payload.summary.file_info.filename);

      // Show the download button
      document.getElementById('download-cleaned-btn').style.display = 'block';

      return payload.summary;
    }
    status.textContent = 'Unexpected server response';
    status.classList.add('text-danger');
    return null;
  } catch (err) {
    console.error('Upload error:', err);
    status.textContent = err.message || 'Upload failed';
    status.classList.add('text-danger');
    return null;
  }
}

function populateTypeFilter(summary) {
  const types = new Set(Object.values(summary.data_types || {}));
  const sel = document.getElementById('filter-type');
  // clear except first
  sel.querySelectorAll('option:not(:first-child)').forEach(o=>o.remove());
  types.forEach(t => {
    const o = document.createElement('option'); o.value = t; o.textContent = t; sel.appendChild(o);
  });
}

async function init() {
  const summary = await fetchSummary();
  if (!summary) {
    // No summary yet; keep upload UI available and show empty cards
    document.getElementById('card-columns').textContent = '-';
    document.getElementById('card-rows').textContent = '-';
    document.getElementById('card-missing').textContent = '-';
    document.getElementById('card-size').textContent = '-';
  } else {
    populateCards(summary);
    buildTable(summary);
    populateTypeFilter(summary);
    // Also render charts on initial load if a summary exists
    try {
      if (summary.file_info && summary.file_info.filename) {
        await displayCharts(summary.file_info.filename);
      }
    } catch (e) {
      console.warn('Chart rendering failed on init:', e);
    }
  }

  // Ensure DataTables is loaded
  if (typeof $.fn.dataTable === 'undefined') {
    document.querySelector('main').insertAdjacentHTML('afterbegin', '<div class="alert alert-danger">DataTables JS not loaded. Table features disabled.</div>');
    return;
  }

  // init DataTable (works with empty tbody too)
  dataTableInstance = $('#columns-table').DataTable({
    paging: true,
    pageLength: 10,
    lengthChange: false,
    info: false,
    searching: false,
    order: [[2, 'desc']],
  });

  // ensure ext.search exists
  $.fn.dataTable.ext = $.fn.dataTable.ext || {};
  $.fn.dataTable.ext.search = $.fn.dataTable.ext.search || [];

  // connect search box
  const searchInput = document.getElementById('table-search');
  if (searchInput) {
    searchInput.addEventListener('input', (e)=>{
      dataTableInstance.search(e.target.value).draw();
    });
  }

  // filter by type
  document.getElementById('filter-type').addEventListener('change', (e)=>{
    const v = e.target.value;
    if (!v) dataTableInstance.column(1).search('').draw();
    else dataTableInstance.column(1).search('^'+v+'$', true, false).draw();
  });

  // filter by missing values (max)
  document.getElementById('filter-missing').addEventListener('input', (e)=>{
    const max = e.target.value;
    if (!max) {
      $.fn.dataTable.ext.search = $.fn.dataTable.ext.search.filter(f=>f.name!=='missingFilter');
      dataTableInstance.draw();
      return;
    }
    // remove existing filter
    $.fn.dataTable.ext.search = $.fn.dataTable.ext.search.filter(f=>f.name!=='missingFilter');
    const missingFilter = function(settings, data, dataIndex) {
      const missingVal = Number(data[2]) || 0;
      return missingVal <= Number(max);
    };
    // tag the filter so we can remove it later
    missingFilter.name = 'missingFilter';
    $.fn.dataTable.ext.search.push(missingFilter);
    dataTableInstance.draw();
  });

  // wire upload button
  const uploadBtn = document.getElementById('upload-btn');
  const fileInput = document.getElementById('summary-file');
  uploadBtn.addEventListener('click', async () => {
    const f = fileInput.files && fileInput.files[0];
    if (!f) {
      const s = document.getElementById('upload-status'); s.textContent = 'Please select a file'; s.classList.add('text-danger');
      return;
    }
    uploadBtn.disabled = true;
    const newSummary = await uploadFileAndRefresh(f);
    uploadBtn.disabled = false;
    if (newSummary) {
      populateCards(newSummary);
      populateTypeFilter(newSummary);
      // prefer updating the DataTable via its API when available to avoid reinitialization issues
      const rows = summaryToRows(newSummary);
      try {
        if (dataTableInstance && $.fn.dataTable && $.fn.dataTable.isDataTable('#columns-table')) {
          dataTableInstance.clear();
          dataTableInstance.rows.add(rows);
          dataTableInstance.draw(false);
        } else {
          // not initialized: render tbody and initialize DataTable
          const tbody = document.querySelector('#columns-table tbody');
          tbody.innerHTML = '';
          rows.forEach(r => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
              <td>${escapeHtml(r[0])}</td>
              <td>${escapeHtml(r[1])}</td>
              <td>${escapeHtml(r[2])}</td>
              <td>${escapeHtml(r[3])}</td>
            `;
            tbody.appendChild(tr);
          });
          dataTableInstance = $('#columns-table').DataTable({ paging: true, pageLength: 10, lengthChange: false, info: false, searching: false, order: [[2, 'desc']] });
          try { dataTableInstance.draw(false); } catch (e) { /* ignore */ }
        }
      } catch (e) {
        console.warn('Error updating DataTable after upload', e);
        // fallback to rebuild DOM table
        buildTable(newSummary);
      }
    }
  });

  // wire download cleaned button
  const downloadBtn = document.getElementById("download-cleaned-btn");
  downloadBtn.addEventListener("click", async () => {
    const summary = await fetchSummary();
    if (!summary) {
      alert("No summary available. Please analyze a file first.");
      return;
    }
    const filename = summary.file_info.filename;
    try {
      const res = await fetch("/download-cleaned", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename }),
      });
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.style.display = "none";
      a.href = url;
      a.download = `cleaned_${filename}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Download error:", err);
      alert("Failed to download cleaned file.");
    }
  });


  // (customization panel removed) default styles applied via HTML/CSS
}

// initialize on page load
document.addEventListener('DOMContentLoaded', init);
