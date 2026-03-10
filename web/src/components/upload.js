/**
 * N1 — PDF Upload Component (wired to real API)
 * Dual drag-and-drop upload for adjuster + contractor estimates.
 * Calls POST /api/analyze with JWT auth via apiFetch().
 *
 * UI improvements:
 *   - Upload arrow icon over PDF document for clear affordance
 *   - Color-coded zones: amber (adjuster) vs cyan (contractor)
 *   - "Click or drag to upload" CTA text
 *   - Collapsible mock Xactimate preview tables
 *   - Rich file success state with name, size, and remove button
 *   - Toast notifications for pipeline success
 *   - Keyboard shortcut: Ctrl+Enter to run pipeline
 */

import { createElement, formatFileSize } from '../utils/format.js';
import { getState, setFile, setView, setState, updateNode } from '../utils/state.js';
import { apiFetch, isSupabaseConfigured } from '../utils/supabase.js';

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50 MB

/**
 * Validate a file for upload.
 * @param {File} file
 * @returns {{ valid: boolean, error?: string }}
 */
export function validateFile(file) {
  if (!file) return { valid: false, error: 'No file selected' };
  if (file.type !== 'application/pdf') {
    return { valid: false, error: 'Only PDF files are accepted' };
  }
  if (file.size > MAX_FILE_SIZE) {
    return { valid: false, error: `File exceeds ${formatFileSize(MAX_FILE_SIZE)} limit` };
  }
  if (file.size === 0) {
    return { valid: false, error: 'File is empty' };
  }
  return { valid: true };
}

/* ── SVG Icons ── */

/**
 * Create an SVG upload icon: PDF document with upload arrow overlay.
 * @param {string} accentColor - CSS color for the arrow accent
 * @returns {HTMLElement}
 */
function createUploadIcon(accentColor) {
  const wrapper = createElement('div', { className: 'upload-icon-wrapper' });
  wrapper.innerHTML = `
    <svg width="64" height="72" viewBox="0 0 64 72" fill="none" xmlns="http://www.w3.org/2000/svg">
      <!-- Document body -->
      <rect x="4" y="8" width="48" height="60" rx="4" fill="rgba(255,255,255,0.06)" stroke="rgba(255,255,255,0.12)" stroke-width="1.5"/>
      <!-- Folded corner -->
      <path d="M36 8L52 24H40C37.7909 24 36 22.2091 36 20V8Z" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.12)" stroke-width="1.5"/>
      <!-- PDF text -->
      <text x="28" y="50" text-anchor="middle" fill="rgba(255,255,255,0.3)" font-family="var(--font-mono)" font-size="10" font-weight="600">PDF</text>
      <!-- Upload arrow circle -->
      <circle cx="48" cy="56" r="14" fill="${accentColor}" opacity="0.9"/>
      <!-- Arrow up -->
      <path d="M48 62V50M48 50L43 55M48 50L53 55" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `;
  return wrapper;
}

/**
 * Create a file icon showing successful upload.
 * @returns {HTMLElement}
 */
function createSuccessIcon() {
  const wrapper = createElement('div', { className: 'upload-icon-wrapper' });
  wrapper.innerHTML = `
    <svg width="64" height="72" viewBox="0 0 64 72" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="4" y="8" width="48" height="60" rx="4" fill="rgba(16,185,129,0.08)" stroke="rgba(16,185,129,0.3)" stroke-width="1.5"/>
      <path d="M36 8L52 24H40C37.7909 24 36 22.2091 36 20V8Z" fill="rgba(16,185,129,0.12)" stroke="rgba(16,185,129,0.3)" stroke-width="1.5"/>
      <text x="28" y="46" text-anchor="middle" fill="rgba(16,185,129,0.5)" font-family="var(--font-mono)" font-size="10" font-weight="600">PDF</text>
      <circle cx="48" cy="56" r="14" fill="#10b981" opacity="0.9"/>
      <path d="M42 56L46 60L54 52" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `;
  return wrapper;
}

/**
 * Create a single upload zone for a role.
 * @param {'adjuster'|'contractor'} role
 * @param {string} label
 * @param {string} description
 * @returns {HTMLElement}
 */
function createUploadZone(role, label, description) {
  const state = getState();
  const file = state.files[role];
  const isAdjuster = role === 'adjuster';
  const accentColor = isAdjuster ? '#f59e0b' : '#06b6d4';
  const roleClass = isAdjuster ? 'upload-zone--adjuster' : 'upload-zone--contractor';

  const zone = createElement('div', {
    className: `upload-zone ${roleClass} ${file ? 'has-file' : ''}`,
    id: `upload-zone-${role}`,
  });

  // Hidden file input
  const input = createElement('input', {
    type: 'file',
    accept: '.pdf,application/pdf',
    className: 'sr-only',
    id: `file-input-${role}`,
  });
  input.style.display = 'none';

  input.addEventListener('change', (e) => {
    const selected = e.target.files[0];
    if (selected) handleFile(role, selected, zone);
  });

  // Drag & drop handlers
  zone.addEventListener('dragover', (e) => {
    e.preventDefault();
    zone.classList.add('drag-over');
  });

  zone.addEventListener('dragleave', () => {
    zone.classList.remove('drag-over');
  });

  zone.addEventListener('drop', (e) => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    const dropped = e.dataTransfer.files[0];
    if (dropped) handleFile(role, dropped, zone);
  });

  zone.addEventListener('click', (e) => {
    // Don't trigger file picker when clicking remove button or collapsible toggle
    if (e.target.closest('.upload-file-remove') || e.target.closest('.upload-preview-toggle')) return;
    input.click();
  });

  // Content: either file-selected state or upload prompt
  if (file) {
    // ── File selected state ──
    const icon = createSuccessIcon();

    const fileCard = createElement('div', { className: 'upload-file-card' });
    const fileName = createElement('div', { className: 'upload-file-name' }, file.name);
    const fileSize = createElement('div', { className: 'upload-file-size' }, formatFileSize(file.size));
    const removeBtn = createElement('button', {
      className: 'upload-file-remove',
      id: `remove-file-${role}`,
    }, '✕');
    removeBtn.title = 'Remove file';
    removeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      setFile(role, null);
    });

    fileCard.append(fileName, fileSize, removeBtn);
    zone.append(input, icon, createElement('div', { className: 'upload-label' }, label), fileCard);
  } else {
    // ── Upload prompt state ──
    const icon = createUploadIcon(accentColor);
    const labelEl = createElement('div', { className: 'upload-label' }, label);
    const descEl = createElement('div', { className: 'upload-sublabel' }, description);
    const ctaEl = createElement('div', { className: 'upload-cta' }, '📎 Click or drag PDF to upload');

    zone.append(input, icon, labelEl, descEl, ctaEl);
  }

  return zone;
}

/**
 * Handle a file being selected/dropped.
 * @param {'adjuster'|'contractor'} role
 * @param {File} file
 * @param {HTMLElement} zone
 */
function handleFile(role, file, zone) {
  const validation = validateFile(file);
  if (!validation.valid) {
    // Flash error
    const existing = zone.querySelector('.upload-error');
    if (existing) existing.remove();
    const errorEl = createElement('div', {
      className: 'upload-error',
    }, `⚠️ ${validation.error}`);
    errorEl.style.cssText = 'color: var(--color-danger-light); font-size: 0.8rem; margin-top: var(--space-sm);';
    zone.appendChild(errorEl);
    setTimeout(() => errorEl.remove(), 3000);
    return;
  }
  setFile(role, file);
  showToast(`✅ ${file.name} ready`, 'success');
}

/**
 * Map backend pipeline stage names to frontend node IDs.
 * Used to update progress when the API returns nodes_completed.
 */
const STAGE_NODE_MAP = {
  'adjuster_nodes_1-3': [1, 2, 3],
  'contractor_nodes_1-3': [1, 2, 3],
  'node5_comparator': [5],
  'node6_supplement': [6],
};

/**
 * Run the real analysis pipeline via POST /api/analyze.
 * Sends both PDFs as multipart/form-data with JWT auth.
 */
async function runPipeline() {
  const state = getState();
  if (!state.files.adjuster || !state.files.contractor) return;

  // Reset nodes and switch to pipeline view
  setState({
    pipelineRunning: true,
    pipelineError: null,
    supplementReport: null,
    hitlQueue: [],
  });

  // Reset all nodes to idle
  for (const node of state.pipelineNodes) {
    updateNode(node.id, { status: 'idle', progress: 0 });
  }

  setView('pipeline');

  // Show progressive status: mark first batch as running
  updateNode(1, { status: 'running', progress: 30 });
  updateNode(2, { status: 'running', progress: 0 });

  try {
    // Build multipart form data matching backend field names
    const formData = new FormData();
    formData.append('adjuster_pdf', state.files.adjuster);
    formData.append('contractor_pdf', state.files.contractor);

    const response = await apiFetch('/api/analyze', {
      method: 'POST',
      body: formData,
      // Do NOT set Content-Type; fetch sets it with boundary for multipart
    });

    if (!response.ok) {
      let errDetail;
      try {
        const errBody = await response.json();
        errDetail = errBody.detail || errBody.error || errBody.message || `Server error ${response.status}`;
        if (typeof errDetail === 'object') {
          errDetail = errDetail.error || errDetail.message || JSON.stringify(errDetail);
        }
      } catch {
        errDetail = `Server error: ${response.status} ${response.statusText}`;
      }

      // Mark all running nodes as failed
      for (const node of getState().pipelineNodes) {
        if (node.status === 'running') {
          updateNode(node.id, { status: 'failed', progress: 0 });
        }
      }

      setState({
        pipelineRunning: false,
        pipelineError: errDetail,
      });
      return;
    }

    const data = await response.json();

    // Mark all nodes as completed
    for (const node of getState().pipelineNodes) {
      updateNode(node.id, { status: 'completed', progress: 100 });
    }

    // Store the real report and gap report
    const gapReport = data.gap_report || {};
    const report = data.report || {};

    // The report view expects the Node 5 gap report shape (summary, line_item_gaps, etc.)
    // Map from the API response which may have nested structure
    const supplementReport = {
      summary: gapReport.summary || report.executive_summary || {},
      line_item_gaps: gapReport.line_item_gaps || [],
      op_analysis: gapReport.op_analysis || {},
      depreciation_findings: gapReport.depreciation_findings || [],
    };

    // Build HITL queue from hitl_flags if present
    const hitlQueue = (gapReport.hitl_flags || report.hitl_flags || []).map((flag, i) => ({
      type: flag.type || flag.flag_type || 'low_confidence',
      title: flag.title || flag.description || `Flag #${i + 1}`,
      description: flag.description || flag.reason || '',
      severity: flag.severity || 'warning',
      nodeId: flag.nodeId || flag.node_id || 0,
      lineItem: flag.lineItem || flag.line_item || '',
    }));

    setState({
      pipelineRunning: false,
      pipelineError: null,
      supplementReport,
      hitlQueue,
      lastAnalysisId: data.analysis_id || null,
      lastMetadata: data.metadata || null,
      rateLimitRemaining: data.rate_limit?.remaining_today ?? null,
    });

    showToast('🎉 Analysis complete! View your supplement report.', 'success');

  } catch (err) {
    // Network error or unexpected failure
    for (const node of getState().pipelineNodes) {
      if (node.status === 'running' || node.status === 'idle') {
        updateNode(node.id, { status: 'failed', progress: 0 });
      }
    }

    setState({
      pipelineRunning: false,
      pipelineError: err.message || 'Network error — could not reach the analysis server.',
    });
  }
}

/* ── Toast Notification System ── */

/**
 * Show a toast notification at the top of the viewport.
 * @param {string} message
 * @param {'success'|'error'|'info'} type
 */
function showToast(message, type = 'info') {
  const existing = document.getElementById('oe-toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.id = 'oe-toast';
  toast.className = `oe-toast oe-toast--${type}`;
  toast.textContent = message;

  document.body.appendChild(toast);

  // Trigger entrance
  requestAnimationFrame(() => toast.classList.add('oe-toast--visible'));

  // Auto-dismiss
  setTimeout(() => {
    toast.classList.remove('oe-toast--visible');
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

/* ── Onboarding: How It Works ── */

/**
 * Build a styled mini-table resembling an Xactimate estimate.
 * @param {Array<{sel: string, desc: string, qty: string, unit: string, price: string, total: string}>} rows
 * @returns {HTMLElement}
 */
function buildMockTable(rows) {
  const table = document.createElement('table');
  table.style.cssText = `
    width: 100%;
    border-collapse: collapse;
    font-size: 0.68rem;
    font-family: var(--font-mono, monospace);
    color: var(--text-secondary, #94a3b8);
  `;

  const thead = document.createElement('thead');
  const headerRow = document.createElement('tr');
  ['Selector', 'Description', 'Qty', 'Unit', 'Price', 'Total'].forEach(h => {
    const th = document.createElement('th');
    th.textContent = h;
    th.style.cssText = `
      padding: 3px 6px;
      text-align: left;
      font-weight: 600;
      font-size: 0.6rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-muted, #64748b);
      border-bottom: 1px solid var(--surface-border, rgba(255,255,255,0.08));
    `;
    if (['Qty', 'Price', 'Total'].includes(h)) th.style.textAlign = 'right';
    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);

  const tbody = document.createElement('tbody');
  rows.forEach(r => {
    const tr = document.createElement('tr');
    [r.sel, r.desc, r.qty, r.unit, r.price, r.total].forEach((val, i) => {
      const td = document.createElement('td');
      td.textContent = val;
      td.style.cssText = `
        padding: 3px 6px;
        border-bottom: 1px solid rgba(255,255,255,0.04);
        white-space: nowrap;
      `;
      if (i >= 2 && i !== 3) td.style.textAlign = 'right';
      if (i === 0) td.style.color = 'var(--brand-accent, #06b6d4)';
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });

  table.append(thead, tbody);
  return table;
}

/**
 * Render the "How It Works" stepper with animated beam connectors.
 * @returns {HTMLElement}
 */
function renderHowItWorks() {
  const section = createElement('div', { className: 'how-it-works', id: 'how-it-works' });
  section.style.cssText = `margin-bottom: var(--space-xl, 2rem);`;

  const title = createElement('div', { className: 'report-section-title' }, '⚡ How It Works');
  title.style.cssText = 'font-size: 1rem; font-weight: 600; margin-bottom: var(--space-lg);';

  // Inject keyframes for beam animation (only once)
  if (!document.getElementById('stepper-beam-keyframes')) {
    const style = document.createElement('style');
    style.id = 'stepper-beam-keyframes';
    style.textContent = `
      @keyframes beamTravel {
        0% { left: -8px; opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { left: calc(100% - 4px); opacity: 0; }
      }
      @keyframes beamGlow {
        0%, 100% { box-shadow: 0 0 6px 2px rgba(34, 211, 238, 0.5), 0 0 12px 4px rgba(34, 211, 238, 0.2); }
        50% { box-shadow: 0 0 10px 3px rgba(34, 211, 238, 0.7), 0 0 20px 6px rgba(34, 211, 238, 0.3); }
      }
      @keyframes beamTrail {
        0% { left: -40px; opacity: 0; }
        10% { opacity: 0.4; }
        90% { opacity: 0.4; }
        100% { left: calc(100% - 40px); opacity: 0; }
      }
    `;
    document.head.appendChild(style);
  }

  // Stepper container — horizontal flow
  const stepper = createElement('div', {});
  stepper.style.cssText = `
    display: flex;
    align-items: flex-start;
    justify-content: center;
    gap: 0;
    position: relative;
  `;

  const stepData = [
    { num: '1', icon: '📄', title: 'Upload Two PDFs', desc: 'Drop the adjuster\'s and contractor\'s Xactimate estimates' },
    { num: '2', icon: '🔬', title: 'AI Analyzes & Diffs', desc: '6-node pipeline: extract, calculate, compare' },
    { num: '3', icon: '📊', title: 'Supplement Report', desc: 'Missing items, O&P recovery, dollar impact' },
  ];

  stepData.forEach(({ num, icon, title: stepTitle, desc: stepDesc }, i) => {
    // Step node
    const stepNode = createElement('div', {});
    stepNode.style.cssText = `
      display: flex;
      flex-direction: column;
      align-items: center;
      flex: 0 0 auto;
      width: 160px;
      text-align: center;
    `;

    // Numbered circle
    const circle = createElement('div', {});
    circle.style.cssText = `
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: var(--surface-card, #12121a);
      border: 2px solid var(--brand-primary, #6366f1);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.3rem;
      position: relative;
      z-index: 2;
      box-shadow: 0 0 12px rgba(99, 102, 241, 0.2);
      transition: all 250ms ease;
    `;
    circle.textContent = icon;

    // Step number (small, top-right of circle)
    const numLabel = createElement('div', {});
    numLabel.style.cssText = `
      position: absolute;
      top: -4px;
      right: -4px;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: linear-gradient(135deg, var(--brand-primary, #6366f1), var(--brand-accent, #06b6d4));
      color: white;
      font-size: 0.6rem;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 3;
    `;
    numLabel.textContent = num;
    circle.appendChild(numLabel);

    // Title
    const titleEl = createElement('div', {});
    titleEl.style.cssText = `
      font-weight: 600;
      font-size: 0.82rem;
      color: var(--text-primary, #f1f5f9);
      margin-top: var(--space-sm, 0.5rem);
      line-height: 1.3;
    `;
    titleEl.textContent = stepTitle;

    // Description
    const descEl = createElement('div', {});
    descEl.style.cssText = `
      font-size: 0.7rem;
      color: var(--text-muted, #64748b);
      margin-top: 4px;
      line-height: 1.4;
    `;
    descEl.textContent = stepDesc;

    stepNode.append(circle, titleEl, descEl);

    // Add connector beam BEFORE step (except first)
    if (i > 0) {
      const beam = createElement('div', {});
      beam.style.cssText = `
        flex: 1;
        height: 2px;
        background: rgba(99, 102, 241, 0.15);
        position: relative;
        align-self: center;
        margin-top: -60px;
        min-width: 60px;
        overflow: hidden;
        border-radius: 1px;
      `;

      // Animated trailing glow
      const trail = createElement('div', {});
      trail.style.cssText = `
        position: absolute;
        top: -1px;
        width: 40px;
        height: 4px;
        border-radius: 2px;
        background: linear-gradient(90deg, transparent, rgba(34, 211, 238, 0.3), transparent);
        animation: beamTrail 2.5s ease-in-out infinite;
        animation-delay: ${i * 0.3}s;
      `;

      // Animated leading dot with glow
      const dot = createElement('div', {});
      dot.style.cssText = `
        position: absolute;
        top: -3px;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--brand-accent-light, #22d3ee);
        animation: beamTravel 2.5s ease-in-out infinite, beamGlow 1.2s ease-in-out infinite;
        animation-delay: ${i * 0.3}s;
        z-index: 1;
      `;

      beam.append(trail, dot);
      stepper.appendChild(beam);
    }

    stepper.appendChild(stepNode);
  });

  section.append(title, stepper);
  return section;
}

/**
 * Render a collapsible mock Xactimate estimate preview.
 * @param {'adjuster'|'contractor'} role
 * @returns {HTMLElement}
 */
function renderMockEstimatePreview(role) {
  const wrapper = createElement('div', { className: 'upload-preview-wrapper' });

  const toggle = createElement('button', { className: 'upload-preview-toggle' });
  toggle.innerHTML = `<span class="upload-preview-arrow">▶</span> Preview sample format`;
  toggle.addEventListener('click', (e) => {
    e.stopPropagation();
    const content = wrapper.querySelector('.upload-preview-content');
    const arrow = wrapper.querySelector('.upload-preview-arrow');
    const isOpen = content.style.display !== 'none';
    content.style.display = isOpen ? 'none' : 'block';
    arrow.textContent = isOpen ? '▶' : '▼';
  });

  const preview = createElement('div', { className: 'upload-preview-content mock-estimate-preview' });
  preview.style.display = 'none'; // collapsed by default

  const label = createElement('div', {});
  label.style.cssText = `
    font-size: 0.6rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-muted, #64748b);
    margin-bottom: var(--space-xs, 4px);
  `;
  label.textContent = 'Sample Xactimate format:';

  const rows = role === 'adjuster'
    ? [
        { sel: 'RFG 250', desc: 'Remove Comp. shingles', qty: '24.00', unit: 'SQ', price: '$68.57', total: '$1,645.68' },
        { sel: 'RFG 260', desc: 'Shingles - 30yr laminate', qty: '24.00', unit: 'SQ', price: '$135.42', total: '$3,250.08' },
        { sel: 'RFG 120', desc: 'Felt - #30', qty: '24.00', unit: 'SQ', price: '$18.25', total: '$438.00' },
        { sel: 'RFG 400', desc: 'Drip edge', qty: '220.00', unit: 'LF', price: '$3.10', total: '$682.00' },
      ]
    : [
        { sel: 'RFG 250', desc: 'Remove Comp. shingles', qty: '26.50', unit: 'SQ', price: '$68.57', total: '$1,817.11' },
        { sel: 'RFG 260', desc: 'Shingles - 30yr laminate', qty: '26.50', unit: 'SQ', price: '$135.42', total: '$3,588.63' },
        { sel: 'RFG 120', desc: 'Felt - #30', qty: '26.50', unit: 'SQ', price: '$18.25', total: '$483.63' },
        { sel: 'RFG 400', desc: 'Drip edge', qty: '232.00', unit: 'LF', price: '$3.10', total: '$719.20' },
        { sel: 'RFG 525', desc: 'Ice & water shield', qty: '4.50', unit: 'SQ', price: '$94.18', total: '$423.81' },
      ];

  preview.append(label, buildMockTable(rows));
  wrapper.append(toggle, preview);
  return wrapper;
}

/**
 * Render a sample output teaser showing what the gap report looks like.
 * @returns {HTMLElement}
 */
function renderSampleOutput() {
  const section = createElement('div', { id: 'sample-output' });
  section.style.cssText = `
    margin-top: var(--space-xl, 2rem);
    margin-bottom: var(--space-lg, 1.5rem);
  `;

  const title = createElement('div', { className: 'report-section-title' }, '🎯 What You\'ll Get');
  title.style.cssText = 'font-size: 1rem; font-weight: 600; margin-bottom: var(--space-md);';

  const card = createElement('div', {});
  card.style.cssText = `
    background: var(--surface-card, #12121a);
    border: 1px solid var(--surface-border, rgba(255,255,255,0.08));
    border-radius: var(--radius-lg, 16px);
    padding: var(--space-lg, 1.5rem);
    overflow: hidden;
  `;

  // Mock summary stats row
  const statsRow = createElement('div', {});
  statsRow.style.cssText = `
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-sm, 0.5rem);
    margin-bottom: var(--space-md, 1rem);
  `;

  const mockStats = [
    { label: 'Adjuster RCV', value: '$8,415.76', cls: '' },
    { label: 'Contractor RCV', value: '$10,032.38', cls: '' },
    { label: 'Recovery Opportunity', value: '+$1,616.62', cls: 'positive' },
  ];

  mockStats.forEach(({ label, value, cls }) => {
    const stat = createElement('div', {});
    stat.style.cssText = `
      background: var(--surface-glass, rgba(255,255,255,0.04));
      border-radius: var(--radius-sm, 6px);
      padding: var(--space-sm, 0.5rem) var(--space-md, 1rem);
      text-align: center;
    `;
    const labelEl = createElement('div', {});
    labelEl.style.cssText = 'font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); margin-bottom: 2px;';
    labelEl.textContent = label;
    const valueEl = createElement('div', {});
    valueEl.style.cssText = `font-size: 1.1rem; font-weight: 700; font-family: var(--font-mono); ${cls === 'positive' ? 'color: var(--color-success-light, #34d399);' : 'color: var(--text-primary);'}`;
    valueEl.textContent = value;
    stat.append(labelEl, valueEl);
    statsRow.appendChild(stat);
  });

  // Mock gap table
  const tableLabel = createElement('div', {});
  tableLabel.style.cssText = 'font-size: 0.75rem; font-weight: 600; color: var(--text-secondary); margin-bottom: var(--space-sm);';
  tableLabel.textContent = '📋 Sample Gap Analysis';

  const gapTable = document.createElement('table');
  gapTable.style.cssText = `
    width: 100%;
    border-collapse: collapse;
    font-size: 0.72rem;
  `;

  const thead = document.createElement('thead');
  const headerRow = document.createElement('tr');
  ['Type', 'Description', 'Adjuster', 'Contractor', 'Delta'].forEach((h, i) => {
    const th = document.createElement('th');
    th.textContent = h;
    th.style.cssText = `
      padding: 4px 8px;
      text-align: left;
      font-weight: 600;
      font-size: 0.62rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-muted, #64748b);
      border-bottom: 1px solid var(--surface-border, rgba(255,255,255,0.08));
      background: var(--surface-glass, rgba(255,255,255,0.04));
    `;
    if (i >= 2) th.style.textAlign = 'right';
    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);

  const gapData = [
    { type: 'MISSING',  typeCls: '#f87171', desc: 'Ice & water shield (RFG 525)', adj: '—', con: '$423.81', delta: '+$423.81', deltaCls: '#34d399' },
    { type: 'QTY Δ',    typeCls: '#fbbf24', desc: 'Remove Comp. shingles (RFG 250)', adj: '24.00 SQ', con: '26.50 SQ', delta: '+$171.43', deltaCls: '#34d399' },
    { type: 'QTY Δ',    typeCls: '#fbbf24', desc: 'Shingles - 30yr laminate (RFG 260)', adj: '24.00 SQ', con: '26.50 SQ', delta: '+$338.55', deltaCls: '#34d399' },
  ];

  const tbody = document.createElement('tbody');
  gapData.forEach(row => {
    const tr = document.createElement('tr');
    tr.style.cssText = 'transition: background 150ms;';

    // Type badge
    const tdType = document.createElement('td');
    tdType.style.cssText = 'padding: 4px 8px; border-bottom: 1px solid rgba(255,255,255,0.04);';
    const badge = document.createElement('span');
    badge.textContent = row.type;
    badge.style.cssText = `
      display: inline-block;
      padding: 1px 6px;
      border-radius: 100px;
      font-size: 0.58rem;
      font-weight: 700;
      letter-spacing: 0.3px;
      background: ${row.typeCls}20;
      color: ${row.typeCls};
    `;
    tdType.appendChild(badge);

    // Other cells
    const tdDesc = document.createElement('td');
    tdDesc.textContent = row.desc;
    tdDesc.style.cssText = 'padding: 4px 8px; border-bottom: 1px solid rgba(255,255,255,0.04); color: var(--text-secondary);';

    const tdAdj = document.createElement('td');
    tdAdj.textContent = row.adj;
    tdAdj.style.cssText = 'padding: 4px 8px; border-bottom: 1px solid rgba(255,255,255,0.04); text-align: right; font-family: var(--font-mono); color: var(--text-muted);';

    const tdCon = document.createElement('td');
    tdCon.textContent = row.con;
    tdCon.style.cssText = 'padding: 4px 8px; border-bottom: 1px solid rgba(255,255,255,0.04); text-align: right; font-family: var(--font-mono); color: var(--text-secondary);';

    const tdDelta = document.createElement('td');
    tdDelta.textContent = row.delta;
    tdDelta.style.cssText = `padding: 4px 8px; border-bottom: 1px solid rgba(255,255,255,0.04); text-align: right; font-family: var(--font-mono); font-weight: 600; color: ${row.deltaCls};`;

    tr.append(tdType, tdDesc, tdAdj, tdCon, tdDelta);
    tbody.appendChild(tr);
  });

  gapTable.append(thead, tbody);

  // Fade-out overlay at bottom to suggest "there's more"
  const fadeHint = createElement('div', {});
  fadeHint.style.cssText = `
    text-align: center;
    padding: var(--space-sm) 0;
    font-size: 0.7rem;
    color: var(--text-muted);
    font-style: italic;
  `;
  fadeHint.textContent = '… and more — O&P audit, depreciation findings, HITL review flags';

  card.append(statsRow, tableLabel, gapTable, fadeHint);
  section.append(title, card);
  return section;
}

/* ── Keyboard Shortcuts ── */

/** Set up global keyboard shortcut for Ctrl+Enter to run pipeline */
let keyboardBound = false;
function bindKeyboardShortcuts() {
  if (keyboardBound) return;
  keyboardBound = true;
  document.addEventListener('keydown', (e) => {
    // Ctrl+Enter or Cmd+Enter to run pipeline
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      const state = getState();
      if (state.activeView === 'upload' && state.files.adjuster && state.files.contractor && !state.pipelineRunning) {
        e.preventDefault();
        runPipeline();
      }
    }
  });
}

/**
 * Render the upload view.
 * @returns {HTMLElement}
 */
export function renderUploadView() {
  const state = getState();
  const container = createElement('div', { className: 'fade-in' });

  // Bind keyboard shortcuts on first render
  bindKeyboardShortcuts();

  const heading = createElement('h1', {
    className: 'card-title',
  }, '📤 Upload Estimates');
  heading.style.cssText = 'font-size: 1.3rem; margin-bottom: var(--space-lg);';

  const desc = createElement('p', {
    className: 'card-subtitle',
  }, 'Upload both the insurance adjuster\'s estimate and the contractor\'s estimate to generate a supplement analysis report.');
  desc.style.marginBottom = 'var(--space-md)';

  const formatNotice = createElement('div', {
    className: 'upload-format-notice',
    id: 'format-notice',
  });
  formatNotice.style.cssText = `
    background: rgba(245, 158, 11, 0.08);
    border: 1px solid rgba(245, 158, 11, 0.25);
    border-radius: var(--radius-md, 10px);
    padding: var(--space-sm, 8px) var(--space-md, 12px);
    margin-bottom: var(--space-xl, 2rem);
    font-size: 0.82rem;
    color: var(--color-warning-light, #fbbf24);
    display: flex;
    align-items: center;
    gap: var(--space-sm, 8px);
  `;
  formatNotice.textContent = '⚠️ Currently supports Xactimate estimate PDFs only. Other estimate formats are not yet supported.';

  // How It Works section
  const howItWorks = renderHowItWorks();

  // Upload zones with role-specific colors
  const uploadSection = createElement('div', { className: 'upload-section' },
    createUploadZone('adjuster', 'Adjuster Estimate', 'Insurance company\'s Xactimate PDF'),
    createUploadZone('contractor', 'Contractor Estimate', 'Contractor\'s Xactimate PDF'),
  );

  // Add collapsible mock previews inside each upload zone (only when no file is selected)
  if (!state.files.adjuster) {
    const adjZone = uploadSection.querySelector('#upload-zone-adjuster');
    if (adjZone) adjZone.appendChild(renderMockEstimatePreview('adjuster'));
  }
  if (!state.files.contractor) {
    const conZone = uploadSection.querySelector('#upload-zone-contractor');
    if (conZone) conZone.appendChild(renderMockEstimatePreview('contractor'));
  }

  const actions = createElement('div', { className: 'upload-actions' });

  const canRun = state.files.adjuster && state.files.contractor && !state.pipelineRunning;
  const runBtn = createElement('button', {
    className: 'btn btn-primary',
    id: 'btn-run-pipeline',
    onClick: () => runPipeline(),
  }, state.pipelineRunning ? '⏳ Analyzing...' : '🚀 Run Analysis Pipeline');

  if (!canRun) {
    runBtn.setAttribute('disabled', 'true');
  }

  // Keyboard shortcut hint
  const shortcutHint = createElement('span', { className: 'shortcut-hint' });
  shortcutHint.textContent = navigator.platform.includes('Mac') ? '⌘↵' : 'Ctrl+↵';

  if (canRun) {
    runBtn.appendChild(shortcutHint);
  }

  const clearBtn = createElement('button', {
    className: 'btn btn-ghost',
    id: 'btn-clear-files',
    onClick: () => {
      setFile('adjuster', null);
      setFile('contractor', null);
      setState({ pipelineError: null });
    },
  }, 'Clear Files');

  if (state.pipelineRunning) {
    clearBtn.setAttribute('disabled', 'true');
  }

  actions.append(runBtn, clearBtn);

  // Error display
  if (state.pipelineError) {
    const errorBanner = createElement('div', {
      className: 'pipeline-error-banner',
      id: 'pipeline-error',
    });
    errorBanner.style.cssText = `
      background: var(--color-danger-bg, rgba(239, 68, 68, 0.1));
      border: 1px solid var(--color-danger, #ef4444);
      border-radius: var(--radius-md, 8px);
      padding: var(--space-md, 12px) var(--space-lg, 16px);
      margin-top: var(--space-lg, 16px);
      color: var(--color-danger-light, #fca5a5);
      font-size: 0.9rem;
    `;
    errorBanner.textContent = `❌ ${state.pipelineError}`;
    actions.appendChild(errorBanner);
  }

  // Rate limit info
  if (state.rateLimitRemaining != null) {
    const rateInfo = createElement('div', {
      className: 'rate-limit-info',
    });
    rateInfo.style.cssText = `
      color: var(--text-tertiary, #888);
      font-size: 0.75rem;
      margin-top: var(--space-sm, 8px);
      text-align: right;
    `;
    rateInfo.textContent = `${state.rateLimitRemaining} analyses remaining today`;
    actions.appendChild(rateInfo);
  }

  // Sample output teaser
  const sampleOutput = renderSampleOutput();

  container.append(heading, desc, formatNotice, howItWorks, uploadSection, actions, sampleOutput);

  return container;
}
