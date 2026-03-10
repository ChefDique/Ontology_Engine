/**
 * N1 — PDF Upload Component (wired to real API)
 * Dual drag-and-drop upload for adjuster + contractor estimates.
 * Calls POST /api/analyze with JWT auth via apiFetch().
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

  const uploadSection = createElement('div', { className: 'upload-section' },
    createUploadZone('adjuster', 'Adjuster Estimate', 'Insurance company\'s Xactimate PDF'),
    createUploadZone('contractor', 'Contractor Estimate', 'Contractor\'s Xactimate PDF'),
  );

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

  container.append(heading, desc, formatNotice, uploadSection, actions);

  return container;
}
