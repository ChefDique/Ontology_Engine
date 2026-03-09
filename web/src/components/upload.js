/**
 * TASK_L2 — PDF Upload Component
 * Dual drag-and-drop upload for adjuster + contractor estimates.
 */

import { createElement, formatFileSize } from '../utils/format.js';
import { getState, setFile, setView, setState, updateNode } from '../utils/state.js';

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

  const zone = createElement('div', {
    className: `upload-zone ${file ? 'has-file' : ''}`,
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

  zone.addEventListener('click', () => input.click());

  // Content
  const icon = createElement('div', { className: 'upload-icon' }, file ? '✅' : '📄');
  const labelEl = createElement('div', { className: 'upload-label' }, label);
  const descEl = createElement('div', { className: 'upload-sublabel' }, description);

  zone.append(input, icon, labelEl, descEl);

  if (file) {
    const fileInfo = createElement('div', { className: 'upload-file-info' },
      `${file.name} (${formatFileSize(file.size)})`
    );
    zone.appendChild(fileInfo);
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
}

/**
 * Simulate a pipeline run (for UI demo purposes).
 * In production this would POST to the backend API.
 */
async function simulatePipelineRun() {
  const state = getState();
  if (!state.files.adjuster || !state.files.contractor) return;

  setState({ pipelineRunning: true });
  setView('pipeline');

  const nodes = state.pipelineNodes;
  for (const node of nodes) {
    updateNode(node.id, { status: 'running', progress: 0 });
    // Simulate progress
    for (let p = 0; p <= 100; p += 20) {
      await new Promise((r) => setTimeout(r, 150));
      updateNode(node.id, { progress: p });
    }
    updateNode(node.id, { status: 'completed', progress: 100 });
  }

  // Load demo report after pipeline completes
  setState({
    pipelineRunning: false,
    supplementReport: getDemoReport(),
    hitlQueue: getDemoHitlQueue(),
  });
}

/**
 * Render the upload view.
 * @returns {HTMLElement}
 */
export function renderUploadView() {
  const state = getState();
  const container = createElement('div', { className: 'fade-in' });

  const heading = createElement('h1', {
    className: 'card-title',
  }, '📤 Upload Estimates');
  heading.style.cssText = 'font-size: 1.3rem; margin-bottom: var(--space-lg);';

  const desc = createElement('p', {
    className: 'card-subtitle',
  }, 'Upload both the insurance adjuster\'s estimate and the contractor\'s estimate to generate a supplement analysis report.');
  desc.style.marginBottom = 'var(--space-xl)';

  const uploadSection = createElement('div', { className: 'upload-section' },
    createUploadZone('adjuster', 'Adjuster Estimate', 'Insurance company\'s Xactimate PDF'),
    createUploadZone('contractor', 'Contractor Estimate', 'Contractor\'s Xactimate PDF'),
  );

  const actions = createElement('div', { className: 'upload-actions' });

  const canRun = state.files.adjuster && state.files.contractor;
  const runBtn = createElement('button', {
    className: 'btn btn-primary',
    id: 'btn-run-pipeline',
    onClick: () => simulatePipelineRun(),
  }, '🚀 Run Analysis Pipeline');

  if (!canRun) {
    runBtn.setAttribute('disabled', 'true');
  }

  const clearBtn = createElement('button', {
    className: 'btn btn-ghost',
    id: 'btn-clear-files',
    onClick: () => {
      setFile('adjuster', null);
      setFile('contractor', null);
    },
  }, 'Clear Files');

  actions.append(runBtn, clearBtn);
  container.append(heading, desc, uploadSection, actions);

  return container;
}

/** Demo supplement report matching Node 5→6 contract */
function getDemoReport() {
  return {
    summary: {
      adjuster_rcv: 18245.67,
      contractor_rcv: 24890.12,
      total_delta: 6644.45,
      gap_count: 7,
      adjuster_line_count: 23,
      contractor_line_count: 31,
    },
    line_item_gaps: [
      { gap_type: 'missing_item', category: 'Roofing', description: 'Ice & water shield — eaves (3 courses)', contractor_total: 1245.00, adjuster_total: null, trade: 'Roofing' },
      { gap_type: 'missing_item', category: 'Roofing', description: 'Drip edge — aluminum', contractor_total: 487.50, adjuster_total: null, trade: 'Roofing' },
      { gap_type: 'quantity_delta', category: 'Roofing', description: 'Architectural shingles — 30yr', contractor_qty: 28, adjuster_qty: 24, quantity_delta: 4, quantity_delta_pct: 0.167, contractor_total: 3920.00, adjuster_total: 3360.00, pricing_delta: 560.00, trade: 'Roofing' },
      { gap_type: 'pricing_delta', category: 'Gutters', description: 'Seamless aluminum gutter — 5"', contractor_qty: 120, adjuster_qty: 120, quantity_delta: 0, contractor_total: 1800.00, adjuster_total: 1440.00, pricing_delta: 360.00, trade: 'Gutters' },
      { gap_type: 'missing_item', category: 'Interior', description: 'Drywall repair — water damage ceiling', contractor_total: 890.00, adjuster_total: null, trade: 'Drywall' },
      { gap_type: 'quantity_delta', category: 'Roofing', description: 'Synthetic underlayment', contractor_qty: 28, adjuster_qty: 24, quantity_delta: 4, quantity_delta_pct: 0.167, contractor_total: 1120.00, adjuster_total: 960.00, pricing_delta: 160.00, trade: 'Roofing' },
      { gap_type: 'pricing_delta', category: 'Siding', description: 'Vinyl siding — remove & replace', contractor_qty: 4, adjuster_qty: 4, quantity_delta: 0, contractor_total: 2200.00, adjuster_total: 1800.00, pricing_delta: 400.00, trade: 'Siding' },
    ],
    op_analysis: {
      trade_count: 4,
      op_warranted: true,
      adjuster_op_applied: { overhead: 1824.57, profit: 1824.57 },
      contractor_op_applied: { overhead: 2489.01, profit: 2489.01 },
      op_recovery_amount: 1329.88,
      trades_detected: ['Roofing', 'Gutters', 'Drywall', 'Siding'],
    },
    depreciation_findings: [
      { category: 'Roofing', description: 'Architectural shingles — 30yr', depreciation_pct: 0.45, flagged: true, flag_reason: 'Exceeds 35% threshold for roofing materials', recoverable_amount: 1764.00 },
      { category: 'Siding', description: 'Vinyl siding — remove & replace', depreciation_pct: 0.25, flagged: false, flag_reason: '', recoverable_amount: null },
    ],
  };
}

/** Demo HITL queue items */
function getDemoHitlQueue() {
  return [
    { type: 'f9_override', title: 'F9 Note Override — Shingle unit price', description: 'Adjuster F9 note changes unit price from $140 to $128/SQ. Manual review required.', severity: 'warning', nodeId: 2, lineItem: 'Architectural shingles — 30yr' },
    { type: 'low_confidence', title: 'Low Confidence — Interior line item match', description: 'LLM extraction confidence 62% on drywall repair entry. Verify mapping.', severity: 'warning', nodeId: 2, lineItem: 'Drywall repair — water damage ceiling' },
    { type: 'threshold_breach', title: 'Depreciation Threshold — Shingles at 45%', description: 'Depreciation rate exceeds 35% threshold. May be excessive and recoverable.', severity: 'danger', nodeId: 5, lineItem: 'Architectural shingles — 30yr' },
  ];
}
