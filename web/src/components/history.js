/**
 * N2 — History View
 * Lists past analyses from /api/history, allows clicking into detail.
 */

import { createElement, formatCurrency } from '../utils/format.js';
import { getState, setState, setView } from '../utils/state.js';
import { apiFetch, isSupabaseConfigured } from '../utils/supabase.js';

/**
 * Fetch the analysis history list.
 */
async function fetchHistory() {
  setState({ historyLoading: true, historyError: null });

  try {
    const response = await apiFetch('/api/history');

    if (!response.ok) {
      let errMsg;
      try {
        const body = await response.json();
        errMsg = body.detail || body.error || `Error ${response.status}`;
        if (typeof errMsg === 'object') errMsg = errMsg.error || JSON.stringify(errMsg);
      } catch {
        errMsg = `Error ${response.status}`;
      }
      setState({ historyLoading: false, historyError: errMsg });
      return;
    }

    const data = await response.json();
    setState({
      historyLoading: false,
      historyError: null,
      historyList: data.analyses || [],
    });
  } catch (err) {
    setState({
      historyLoading: false,
      historyError: err.message || 'Network error fetching history.',
    });
  }
}

/**
 * Fetch a specific analysis by ID and populate the report view.
 * @param {string} id
 */
async function loadAnalysisDetail(id) {
  setState({ historyDetailLoading: true });

  try {
    const response = await apiFetch(`/api/history/${id}`);

    if (!response.ok) {
      setState({ historyDetailLoading: false });
      return;
    }

    const data = await response.json();

    // Parse JSON strings from the DB if necessary
    const report = typeof data.report === 'string' ? JSON.parse(data.report) : (data.report || {});
    const gapReport = typeof data.gap_report === 'string' ? JSON.parse(data.gap_report) : (data.gap_report || {});

    const supplementReport = {
      summary: gapReport.summary || report.executive_summary || {},
      line_item_gaps: gapReport.line_item_gaps || [],
      op_analysis: gapReport.op_analysis || {},
      depreciation_findings: gapReport.depreciation_findings || [],
    };

    setState({
      historyDetailLoading: false,
      supplementReport,
      hitlQueue: [],
      lastAnalysisId: data.id,
    });

    setView('report');
  } catch (err) {
    setState({ historyDetailLoading: false });
  }
}

/**
 * Format a date string for display.
 * @param {string} dateStr
 * @returns {string}
 */
function formatDate(dateStr) {
  if (!dateStr) return '—';
  try {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateStr;
  }
}

/**
 * Render the history list view.
 * @returns {HTMLElement}
 */
export function renderHistoryView() {
  const state = getState();
  const container = createElement('div', { className: 'fade-in' });

  const heading = createElement('h1', { className: 'card-title' }, '📋 Analysis History');
  heading.style.cssText = 'font-size: 1.3rem; margin-bottom: var(--space-sm);';

  const subtitle = createElement('p', { className: 'card-subtitle' },
    'Your past supplement analysis reports.',
  );
  subtitle.style.marginBottom = 'var(--space-lg)';

  // Refresh button
  const refreshBtn = createElement('button', {
    className: 'btn btn-ghost',
    id: 'btn-refresh-history',
    onClick: () => fetchHistory(),
  }, '🔄 Refresh');
  refreshBtn.style.cssText = 'margin-bottom: var(--space-lg); font-size: 0.85rem;';

  container.append(heading, subtitle, refreshBtn);

  // Supabase not configured
  if (!isSupabaseConfigured()) {
    const notice = createElement('div', { className: 'empty-state' },
      createElement('div', { className: 'empty-state-icon' }, '🔒'),
      createElement('div', { className: 'empty-state-title' }, 'Authentication Required'),
      createElement('div', { className: 'empty-state-description' },
        'Analysis history requires authentication. Configure Supabase to enable.'),
    );
    container.appendChild(notice);
    return container;
  }

  // Loading
  if (state.historyLoading) {
    const loader = createElement('div', { className: 'empty-state' },
      createElement('div', { className: 'empty-state-icon' }, '⏳'),
      createElement('div', { className: 'empty-state-title' }, 'Loading history...'),
    );
    container.appendChild(loader);
    return container;
  }

  // Error
  if (state.historyError) {
    const errEl = createElement('div', { className: 'empty-state' },
      createElement('div', { className: 'empty-state-icon' }, '❌'),
      createElement('div', { className: 'empty-state-title' }, 'Error loading history'),
      createElement('div', { className: 'empty-state-description' }, state.historyError),
    );
    container.appendChild(errEl);
    return container;
  }

  // Empty
  if (state.historyList.length === 0) {
    const empty = createElement('div', { className: 'empty-state' },
      createElement('div', { className: 'empty-state-icon' }, '📋'),
      createElement('div', { className: 'empty-state-title' }, 'No Analyses Yet'),
      createElement('div', { className: 'empty-state-description' },
        'Upload estimates and run the pipeline to see your history here.'),
    );
    container.appendChild(empty);
    return container;
  }

  // Detail loading overlay
  if (state.historyDetailLoading) {
    const overlay = createElement('div', { className: 'empty-state' },
      createElement('div', { className: 'empty-state-icon' }, '⏳'),
      createElement('div', { className: 'empty-state-title' }, 'Loading analysis...'),
    );
    container.appendChild(overlay);
    return container;
  }

  // History table
  const card = createElement('div', { className: 'card' });
  card.style.padding = '0';
  card.style.overflow = 'auto';

  const table = createElement('table', { className: 'gap-table', id: 'history-table' });

  const thead = createElement('thead', {},
    createElement('tr', {},
      createElement('th', {}, 'Date'),
      createElement('th', {}, 'Adjuster File'),
      createElement('th', {}, 'Contractor File'),
      createElement('th', {}, 'Gaps'),
      createElement('th', {}, 'Delta'),
      createElement('th', {}, 'Recovery'),
      createElement('th', {}, 'Duration'),
      createElement('th', {}, ''),
    ),
  );

  const tbody = createElement('tbody', {});

  for (const analysis of state.historyList) {
    const row = createElement('tr', { className: 'history-row' });
    row.style.cursor = 'pointer';

    row.addEventListener('click', () => loadAnalysisDetail(analysis.id));

    row.append(
      createElement('td', {}, formatDate(analysis.created_at)),
      createElement('td', {}, analysis.adjuster_filename || '—'),
      createElement('td', {}, analysis.contractor_filename || '—'),
      createElement('td', {}, String(analysis.gap_count ?? '—')),
      createElement('td', { className: analysis.total_delta > 0 ? 'money positive' : 'money' },
        analysis.total_delta != null ? `+${formatCurrency(analysis.total_delta)}` : '—'),
      createElement('td', { className: analysis.total_recovery > 0 ? 'money positive' : 'money' },
        analysis.total_recovery != null ? formatCurrency(analysis.total_recovery) : '—'),
      createElement('td', {},
        analysis.duration_seconds != null ? `${analysis.duration_seconds}s` : '—'),
      createElement('td', {},
        createElement('button', {
          className: 'btn btn-ghost btn-sm',
          onClick: (e) => { e.stopPropagation(); loadAnalysisDetail(analysis.id); },
        }, 'View →'),
      ),
    );

    tbody.appendChild(row);
  }

  table.append(thead, tbody);
  card.appendChild(table);
  container.appendChild(card);

  return container;
}

/**
 * Trigger initial history load when the view is activated.
 */
export function initHistoryView() {
  const state = getState();
  if (state.historyList.length === 0 && !state.historyLoading) {
    fetchHistory();
  }
}
