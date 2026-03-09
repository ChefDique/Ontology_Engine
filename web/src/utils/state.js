/**
 * Ontology Engine — Application State
 * Simple observable state store for the UI.
 */

/**
 * @typedef {Object} AppState
 * @property {'upload'|'pipeline'|'report'|'review'|'history'} activeView
 * @property {{ adjuster: File|null, contractor: File|null }} files
 * @property {Array<Object>} pipelineNodes
 * @property {Object|null} supplementReport
 * @property {Array<Object>} hitlQueue
 * @property {boolean} pipelineRunning
 * @property {string|null} pipelineError
 * @property {string|null} lastAnalysisId
 * @property {Object|null} lastMetadata
 * @property {number|null} rateLimitRemaining
 * @property {Array<Object>} historyList
 * @property {boolean} historyLoading
 * @property {string|null} historyError
 * @property {Object|null} historyDetail
 * @property {boolean} historyDetailLoading
 */

/** @type {AppState} */
const state = {
  activeView: 'upload',
  files: { adjuster: null, contractor: null },
  pipelineNodes: [
    { id: 1, name: 'Ingestion', description: 'PDF parse, OCR, PII redaction', status: 'idle', progress: 0 },
    { id: 2, name: 'Extraction', description: 'LLM line-item extraction', status: 'idle', progress: 0 },
    { id: 3, name: 'Calculus', description: 'Roofer math, O&P, trade mapping', status: 'idle', progress: 0 },
    { id: 4, name: 'Output', description: 'CRM-ready CSV/JSON routing', status: 'idle', progress: 0 },
    { id: 5, name: 'Comparator', description: 'Line-item diff, O&P audit', status: 'idle', progress: 0 },
    { id: 6, name: 'Supplement', description: 'Gap report generation', status: 'idle', progress: 0 },
  ],
  supplementReport: null,
  hitlQueue: [],
  pipelineRunning: false,
  pipelineError: null,
  lastAnalysisId: null,
  lastMetadata: null,
  rateLimitRemaining: null,
  historyList: [],
  historyLoading: false,
  historyError: null,
  historyDetail: null,
  historyDetailLoading: false,
};

/** @type {Set<Function>} */
const listeners = new Set();

/**
 * Subscribe to state changes.
 * @param {Function} fn
 * @returns {Function} unsubscribe
 */
export function subscribe(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

/**
 * Get the current state (read-only copy).
 * @returns {AppState}
 */
export function getState() {
  return state;
}

/**
 * Update state and notify listeners.
 * @param {Partial<AppState>} patch
 */
export function setState(patch) {
  Object.assign(state, patch);
  listeners.forEach((fn) => fn(state));
}

/**
 * Set the active view tab.
 * @param {'upload'|'pipeline'|'report'|'review'|'history'} view
 */
export function setView(view) {
  setState({ activeView: view });
}

/**
 * Set a file in the upload state.
 * @param {'adjuster'|'contractor'} role
 * @param {File|null} file
 */
export function setFile(role, file) {
  setState({
    files: { ...state.files, [role]: file },
  });
}

/**
 * Update a specific pipeline node's state.
 * @param {number} nodeId
 * @param {Object} patch
 */
export function updateNode(nodeId, patch) {
  setState({
    pipelineNodes: state.pipelineNodes.map((n) =>
      n.id === nodeId ? { ...n, ...patch } : n
    ),
  });
}

/**
 * Set the supplement report data (Node 6 output).
 * @param {Object} report
 */
export function setReport(report) {
  setState({ supplementReport: report });
}

/**
 * Set the HITL review queue.
 * @param {Array<Object>} queue
 */
export function setHitlQueue(queue) {
  setState({ hitlQueue: queue });
}

/**
 * Remove an item from the HITL queue by index.
 * @param {number} index
 */
export function resolveHitlItem(index) {
  setState({
    hitlQueue: state.hitlQueue.filter((_, i) => i !== index),
  });
}
