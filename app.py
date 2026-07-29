from flask import Flask, render_template_string
import pandas as pd
import json
from datetime import date

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Breach Autopsy Engine</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/tabler-icons/2.44.0/iconfont/tabler-icons.min.css">
<style>
  :root {
    --bg: #0b0e13; --panel: #12161d; --panel-2: #171c24;
    --border: #232a35; --border-strong: #2f3847;
    --text: #e7ebf1; --text-dim: #8b95a5; --text-faint: #5c6577;
    --amber: #e3a138; --amber-dim: #4a3a1c;
    --red: #d9564f; --red-dim: #3d201e;
    --blue: #5b8dd6; --blue-dim: #1e2a3d;
    --purple: #9b7fd4; --purple-dim: #2a2440;
    --green: #5cb87a; --green-dim: #1e3626;
    --mono: 'SF Mono', 'Cascadia Code', Consolas, monospace;
    --sans: -apple-system, 'Segoe UI', Inter, Arial, sans-serif;
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--text); font-family: var(--sans); }
  .wrap { max-width: 1180px; margin: 0 auto; padding: 40px 32px 80px; }
  .header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 32px; padding-bottom: 24px; border-bottom: 1px solid var(--border); }
  .header-left .eyebrow { font-family: var(--mono); font-size: 12px; letter-spacing: 0.08em; color: var(--amber); text-transform: uppercase; margin: 0 0 8px; }
  .header-left h1 { font-size: 26px; font-weight: 600; margin: 0 0 6px; letter-spacing: -0.01em; }
  .header-left p { font-size: 14px; color: var(--text-dim); margin: 0; max-width: 520px; line-height: 1.5; }
  .header-right { text-align: right; font-family: var(--mono); font-size: 12px; color: var(--text-faint); }
  .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: var(--border); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; margin-bottom: 28px; }
  .stat { background: var(--panel); padding: 18px 20px; }
  .stat .label { font-size: 11px; color: var(--text-faint); text-transform: uppercase; letter-spacing: 0.06em; margin: 0 0 8px; font-family: var(--mono); }
  .stat .value { font-size: 28px; font-weight: 600; font-family: var(--mono); letter-spacing: -0.02em; }
  .stat .sub { font-size: 12px; color: var(--text-dim); margin-top: 4px; }
  .stat.accent .value { color: var(--amber); }
  .grid-2 { display: grid; grid-template-columns: 1.3fr 1fr; gap: 16px; margin-bottom: 28px; }
  .panel { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 20px 22px; }
  .panel h2 { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-dim); margin: 0 0 16px; }
  .bar-row { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; font-size: 13px; }
  .bar-row:last-child { margin-bottom: 0; }
  .bar-label { width: 150px; flex-shrink: 0; color: var(--text-dim); font-family: var(--mono); font-size: 12px; }
  .bar-track { flex: 1; height: 18px; background: var(--panel-2); border-radius: 3px; overflow: hidden; }
  .bar-fill { height: 100%; border-radius: 3px; }
  .bar-count { width: 32px; text-align: right; font-family: var(--mono); font-size: 12px; color: var(--text-dim); }
  .conf-list { display: flex; flex-direction: column; gap: 14px; }
  .conf-item { display: flex; justify-content: space-between; align-items: center; padding-bottom: 14px; border-bottom: 1px solid var(--border); }
  .conf-item:last-child { border: none; padding-bottom: 0; }
  .conf-item .dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 10px; }
  .conf-item .name { font-size: 13px; color: var(--text); display: flex; align-items: center; }
  .conf-item .pct { font-family: var(--mono); font-size: 13px; color: var(--text-dim); }
  .table-panel { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }
  .table-toolbar { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid var(--border); gap: 16px; }
  .table-toolbar h2 { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-dim); margin: 0; white-space: nowrap; }
  .search-box { position: relative; flex: 1; max-width: 340px; }
  .search-box i { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--text-faint); font-size: 15px; }
  .search-box input { width: 100%; background: var(--panel-2); border: 1px solid var(--border); border-radius: 6px; padding: 8px 12px 8px 34px; color: var(--text); font-size: 13px; font-family: var(--sans); }
  .search-box input:focus { outline: none; border-color: var(--border-strong); }
  .search-box input::placeholder { color: var(--text-faint); }
  table { width: 100%; border-collapse: collapse; }
  thead th { text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-faint); font-weight: 500; padding: 10px 20px; background: var(--panel-2); border-bottom: 1px solid var(--border); cursor: pointer; white-space: nowrap; }
  thead th:hover { color: var(--text-dim); }
  tbody td { padding: 12px 20px; font-size: 13px; border-bottom: 1px solid var(--border); color: var(--text); }
  tbody tr:last-child td { border-bottom: none; }
  tbody tr:hover td { background: rgba(255,255,255,0.015); }
  .company-cell { font-weight: 500; }
  .date-cell { font-family: var(--mono); color: var(--text-dim); font-size: 12px; }
  .tech-cell { font-family: var(--mono); color: var(--text-dim); font-size: 12px; }
  .vec-badge { display: inline-flex; align-items: center; gap: 5px; padding: 3px 9px; border-radius: 4px; font-size: 11.5px; font-weight: 500; font-family: var(--mono); }
  .vec-badge .dot { width: 6px; height: 6px; border-radius: 50%; }
  .vec-ransomware { background: var(--red-dim); color: #f0938d; } .vec-ransomware .dot { background: var(--red); }
  .vec-third_party_vendor { background: var(--amber-dim); color: #f0c179; } .vec-third_party_vendor .dot { background: var(--amber); }
  .vec-credential_compromise { background: var(--blue-dim); color: #9dbde8; } .vec-credential_compromise .dot { background: var(--blue); }
  .vec-unknown_unauthorized_access { background: var(--purple-dim); color: #c3b0e8; } .vec-unknown_unauthorized_access .dot { background: var(--purple); }
  .vec-insider { background: var(--green-dim); color: #97d4ac; } .vec-insider .dot { background: var(--green); }
  .vec-insufficient_data, .vec-other { background: var(--panel-2); color: var(--text-faint); } .vec-insufficient_data .dot, .vec-other .dot { background: var(--text-faint); }
  .conf-tag { font-size: 12px; font-family: var(--mono); }
  .conf-tag.high { color: var(--green); } .conf-tag.medium { color: var(--amber); } .conf-tag.low { color: var(--text-faint); }
  .footer-note { margin-top: 24px; font-size: 12px; color: var(--text-faint); text-align: center; font-family: var(--mono); }
</style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <div class="header-left">
      <p class="eyebrow">Threat intelligence / public disclosures</p>
      <h1>Breach autopsy engine</h1>
      <p>Structured, ATT&CK-mapped extraction from real SEC Form 8-K cyber-incident disclosures (Item 1.05 and 8.01).</p>
    </div>
    <div class="header-right">
      <div>source: sec.gov/edgar</div>
      <div>updated: {{ today }}</div>
    </div>
  </div>
  <div class="stats" id="stats"></div>
  <div class="grid-2">
    <div class="panel"><h2>Attack vector breakdown</h2><div id="vector-bars"></div></div>
    <div class="panel"><h2>Disclosure confidence</h2><div class="conf-list" id="conf-list"></div></div>
  </div>
  <div class="table-panel">
    <div class="table-toolbar">
      <h2>Filing register</h2>
      <div class="search-box"><i class="ti ti-search"></i><input type="text" id="search" placeholder="Search company, vector, technique, date..."></div>
    </div>
    <table id="dataTable">
      <thead><tr>
        <th data-key="company">Company</th>
        <th data-key="attack_vector">Attack vector</th>
        <th data-key="mitre_attack_technique">ATT&CK ID</th>
        <th data-key="confidence">Confidence</th>
        <th data-key="filed_date">Filed</th>
      </tr></thead>
      <tbody id="tableBody"></tbody>
    </table>
  </div>
  <p class="footer-note">All records sourced from public SEC EDGAR filings · extraction assisted by LLM, flagged low-confidence where disclosure language was vague</p>
</div>
<script>
const DATA = {{ data_json | safe }};

function renderStats(data) {
  const total = data.length;
  const companies = new Set(data.map(d => d.company)).size;
  const highConf = data.filter(d => d.confidence === 'high').length;
  const ransomware = data.filter(d => d.attack_vector === 'ransomware').length;
  const stats = [
    { label: 'Total disclosures', value: total, sub: 'unique 8-K filings' },
    { label: 'Distinct companies', value: companies, sub: 'public registrants' },
    { label: 'Ransomware-attributed', value: ransomware, sub: total ? Math.round(ransomware/total*100)+'% of filings' : '', accent: true },
    { label: 'High-confidence extraction', value: highConf, sub: total ? Math.round(highConf/total*100)+'% clearly disclosed' : '' },
  ];
  document.getElementById('stats').innerHTML = stats.map(s => `
    <div class="stat ${s.accent ? 'accent' : ''}"><p class="label">${s.label}</p><div class="value">${s.value}</div><p class="sub">${s.sub}</p></div>
  `).join('');
}

function renderVectorBars(data) {
  const counts = {};
  data.forEach(d => { counts[d.attack_vector] = (counts[d.attack_vector] || 0) + 1; });
  const colors = { ransomware:'#d9564f', third_party_vendor:'#e3a138', credential_compromise:'#5b8dd6', unknown_unauthorized_access:'#9b7fd4', insider:'#5cb87a', insufficient_data:'#5c6577', other:'#5c6577' };
  const vals = Object.values(counts);
  const max = vals.length ? Math.max(...vals) : 1;
  const sorted = Object.entries(counts).sort((a,b) => b[1]-a[1]);
  document.getElementById('vector-bars').innerHTML = sorted.map(([key, count]) => `
    <div class="bar-row"><div class="bar-label">${(key||'unknown').replace(/_/g,' ')}</div>
    <div class="bar-track"><div class="bar-fill" style="width:${(count/max*100)}%; background:${colors[key] || '#5c6577'}"></div></div>
    <div class="bar-count">${count}</div></div>
  `).join('');
}

function renderConfidence(data) {
  const counts = { high: 0, medium: 0, low: 0 };
  data.forEach(d => { if (counts[d.confidence] !== undefined) counts[d.confidence]++; });
  const total = data.length || 1;
  const colors = { high: '#5cb87a', medium: '#e3a138', low: '#5c6577' };
  const labels = { high: 'High — specifics disclosed', medium: 'Medium — partial detail', low: 'Low — boilerplate language' };
  document.getElementById('conf-list').innerHTML = Object.entries(counts).map(([key, count]) => `
    <div class="conf-item"><span class="name"><span class="dot" style="background:${colors[key]}"></span>${labels[key]}</span>
    <span class="pct">${count} · ${Math.round(count/total*100)}%</span></div>
  `).join('');
}

function vectorBadge(vec) {
  const label = (vec || 'unknown').replace(/_/g, ' ');
  return `<span class="vec-badge vec-${vec}"><span class="dot"></span>${label}</span>`;
}

function renderTable(data) {
  document.getElementById('tableBody').innerHTML = data.map(d => `
    <tr><td class="company-cell">${d.company || '—'}</td><td>${vectorBadge(d.attack_vector)}</td>
    <td class="tech-cell">${d.mitre_attack_technique || '—'}</td><td><span class="conf-tag ${d.confidence}">${d.confidence || '—'}</span></td>
    <td class="date-cell">${d.filed_date || '—'}</td></tr>
  `).join('');
}

let sortState = { key: null, asc: true };
function init() {
  renderStats(DATA); renderVectorBars(DATA); renderConfidence(DATA); renderTable(DATA);
  document.getElementById('search').addEventListener('keyup', (e) => {
    const q = e.target.value.toLowerCase();
    renderTable(DATA.filter(d => JSON.stringify(d).toLowerCase().includes(q)));
  });
  document.querySelectorAll('#dataTable thead th').forEach(th => {
    th.addEventListener('click', () => {
      const key = th.dataset.key;
      sortState.asc = sortState.key === key ? !sortState.asc : true;
      sortState.key = key;
      const sorted = [...DATA].sort((a, b) => {
        const x = (a[key] || '').toString(), y = (b[key] || '').toString();
        return sortState.asc ? x.localeCompare(y) : y.localeCompare(x);
      });
      renderTable(sorted);
    });
  });
}
init();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    df = pd.read_csv("breach_dataset.csv")
    df = df.where(pd.notnull(df), None)
    records = df.to_dict(orient="records")
    return render_template_string(
        TEMPLATE,
        data_json=json.dumps(records),
        today=date.today().isoformat()
    )

if __name__ == "__main__":
    app.run(debug=True)