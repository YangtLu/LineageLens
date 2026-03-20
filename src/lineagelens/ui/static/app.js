const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const processBtn = document.getElementById('processBtn');
const graphSummary = document.getElementById('graphSummary');
const stats = document.getElementById('stats');
const queryInput = document.getElementById('queryInput');
const queryBtn = document.getElementById('queryBtn');
const queryResults = document.getElementById('queryResults');
const loadSampleBtn = document.getElementById('loadSampleBtn');

let selectedFiles = [];

fileInput.addEventListener('change', async (event) => {
  selectedFiles = await Promise.all(Array.from(event.target.files || []).map(async (file) => ({
    name: file.name,
    type: file.name.endsWith('.sql') ? 'sql' : 'python',
    content: await file.text(),
  })));
  renderFileList();
});

loadSampleBtn.addEventListener('click', () => {
  selectedFiles = [
    {
      name: 'daily_revenue.sql',
      type: 'sql',
      content: 'insert into finance.daily_revenue select * from raw.orders join raw.refunds on raw.orders.id = raw.refunds.order_id;',
    },
    {
      name: 'backfill.py',
      type: 'python',
      content: 'sql = """create table mart.customer_health as select * from finance.daily_revenue join crm.accounts on finance.daily_revenue.account_id = crm.accounts.id"""',
    },
  ];
  renderFileList();
});

processBtn.addEventListener('click', async () => {
  if (!selectedFiles.length) {
    fileList.innerHTML = '<p class="empty-state">Upload at least one SQL or Python script to continue.</p>';
    return;
  }
  const response = await fetch('/api/upload', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ files: selectedFiles }),
  });
  const graph = await response.json();
  renderStats(graph.stats);
  renderGraph(graph);
});

queryBtn.addEventListener('click', async () => {
  const term = queryInput.value.trim();
  if (!term) {
    queryResults.textContent = 'Enter a search term to query the lineage graph.';
    return;
  }
  const response = await fetch(`/api/query?q=${encodeURIComponent(term)}`);
  const result = await response.json();
  renderQuery(result);
});

function renderFileList() {
  if (!selectedFiles.length) {
    fileList.className = 'file-list empty-state';
    fileList.textContent = 'No files uploaded yet.';
    return;
  }
  fileList.className = 'file-list';
  fileList.innerHTML = selectedFiles.map((file) => `
    <div class="entity-card">
      <span class="badge">${file.type}</span>
      <strong>${file.name}</strong>
      <p>${file.content.slice(0, 140)}${file.content.length > 140 ? '…' : ''}</p>
    </div>
  `).join('');
}

function renderStats(summary) {
  stats.innerHTML = [
    ['Entities', summary.entities],
    ['Tables', summary.tables],
    ['Jobs', summary.jobs],
    ['Edges', summary.edges],
  ].map(([label, value]) => `<div class="stat-card"><span>${label}</span><strong>${value}</strong></div>`).join('');
}

function renderGraph(graph) {
  if (!graph.nodes.length) {
    graphSummary.className = 'graph-summary empty-state';
    graphSummary.textContent = 'No lineage extracted from the uploaded files.';
    return;
  }
  const nodes = graph.nodes.slice().sort((a, b) => a.entity_type.localeCompare(b.entity_type));
  graphSummary.className = 'graph-summary';
  graphSummary.innerHTML = `
    <p class="success">Processed ${graph.stats.jobs} ETL job(s) and ${graph.stats.tables} table(s).</p>
    ${nodes.map((node) => `
      <div class="entity-card">
        <span class="badge">${node.entity_type}</span>
        <strong>${node.display_name}</strong>
        <p>${node.qualified_name}</p>
        <p>${node.description || 'No description available.'}</p>
      </div>
    `).join('')}
    <div class="entity-card">
      <strong>Lineage edges</strong>
      <ul class="edge-list">
        ${graph.edges.map((edge) => `<li>${edge.edge_type}: ${edge.source_id} → ${edge.target_id}</li>`).join('')}
      </ul>
    </div>
  `;
}

function renderQuery(result) {
  if (!result.matches.length) {
    queryResults.className = 'query-results empty-state';
    queryResults.textContent = 'No lineage matches found for that query.';
    return;
  }
  queryResults.className = 'query-results';
  queryResults.innerHTML = `
    ${result.matches.map((match) => `
      <div class="query-card">
        <span class="badge">${match.entity_type}</span>
        <strong>${match.display_name}</strong>
        <p>${match.qualified_name}</p>
      </div>
    `).join('')}
    <div class="query-card">
      <strong>Connected lineage edges</strong>
      <ul class="edge-list">
        ${result.subgraph.edges.map((edge) => `<li>${edge.edge_type}: ${edge.source_id} → ${edge.target_id}</li>`).join('')}
      </ul>
    </div>
  `;
}
