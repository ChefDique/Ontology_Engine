/**
 * TASK_L4 — Supplement Report Viewer
 * Renders Node 6 output: gap table, O&P analysis, dollar-impact summary.
 */

import { createElement, formatCurrency, formatPercent, moneyClass, gapTypeBadge, gapTypeLabel } from '../utils/format.js';
import { getState } from '../utils/state.js';

/**
 * Render the dollar-impact summary stats.
 * @param {Object} summary
 * @returns {HTMLElement}
 */
function renderSummaryStats(summary) {
  return createElement('div', { className: 'stats-row' },
    createElement('div', { className: 'stat-card' },
      createElement('div', { className: 'stat-label' }, 'Adjuster RCV'),
      createElement('div', { className: 'stat-value' }, formatCurrency(summary.adjuster_rcv)),
    ),
    createElement('div', { className: 'stat-card' },
      createElement('div', { className: 'stat-label' }, 'Contractor RCV'),
      createElement('div', { className: 'stat-value' }, formatCurrency(summary.contractor_rcv)),
    ),
    createElement('div', { className: 'stat-card' },
      createElement('div', { className: 'stat-label' }, 'Total Delta'),
      createElement('div', { className: 'stat-value positive' }, `+${formatCurrency(summary.total_delta)}`),
      createElement('div', { className: 'stat-subtext' }, `${summary.gap_count} gaps identified`),
    ),
    createElement('div', { className: 'stat-card' },
      createElement('div', { className: 'stat-label' }, 'Line Items'),
      createElement('div', { className: 'stat-value' }, `${summary.adjuster_line_count} → ${summary.contractor_line_count}`),
      createElement('div', { className: 'stat-subtext' }, 'Adjuster → Contractor'),
    ),
  );
}

/**
 * Render the gap table (line-item discrepancies).
 * @param {Array<Object>} gaps
 * @returns {HTMLElement}
 */
function renderGapTable(gaps) {
  const section = createElement('div', { className: 'report-section' });

  const title = createElement('div', { className: 'report-section-title' },
    '📋 Line Item Gaps',
  );

  const card = createElement('div', { className: 'card' });
  card.style.padding = '0';
  card.style.overflow = 'auto';

  const table = createElement('table', { className: 'gap-table', id: 'gap-table' });

  const thead = createElement('thead', {},
    createElement('tr', {},
      createElement('th', {}, 'Type'),
      createElement('th', {}, 'Category'),
      createElement('th', {}, 'Description'),
      createElement('th', {}, 'Trade'),
      createElement('th', {}, 'Adjuster'),
      createElement('th', {}, 'Contractor'),
      createElement('th', {}, 'Delta'),
    ),
  );

  const tbody = createElement('tbody', {});

  for (const gap of gaps) {
    const delta = (gap.contractor_total || 0) - (gap.adjuster_total || 0);

    const row = createElement('tr', {},
      createElement('td', {},
        createElement('span', { className: `badge ${gapTypeBadge(gap.gap_type)}` }, gapTypeLabel(gap.gap_type)),
      ),
      createElement('td', {}, gap.category || '—'),
      createElement('td', {}, gap.description),
      createElement('td', {}, gap.trade || '—'),
      createElement('td', { className: 'money' }, gap.adjuster_total != null ? formatCurrency(gap.adjuster_total) : '—'),
      createElement('td', { className: 'money' }, gap.contractor_total != null ? formatCurrency(gap.contractor_total) : '—'),
      createElement('td', { className: moneyClass(delta) }, `+${formatCurrency(delta)}`),
    );

    tbody.appendChild(row);
  }

  table.append(thead, tbody);
  card.appendChild(table);
  section.append(title, card);

  return section;
}

/**
 * Render O&P analysis section.
 * @param {Object} op
 * @returns {HTMLElement}
 */
function renderOPAnalysis(op) {
  const section = createElement('div', { className: 'report-section' });

  const title = createElement('div', { className: 'report-section-title' },
    '💰 Overhead & Profit Analysis',
  );

  const card = createElement('div', { className: 'card' });

  // Warranted badge
  const warrantedBadge = op.op_warranted
    ? createElement('span', { className: 'badge badge-success' }, `✓ O&P Warranted (${op.trade_count} trades)`)
    : createElement('span', { className: 'badge badge-warning' }, `O&P Not Warranted (< 3 trades)`);

  const tradesEl = createElement('div', {},
    createElement('strong', {}, 'Trades Detected: '),
    op.trades_detected.join(', '),
  );
  tradesEl.style.cssText = 'color: var(--text-secondary); font-size: 0.85rem; margin: var(--space-md) 0;';

  const opTable = createElement('table', { className: 'gap-table' });
  const opThead = createElement('thead', {},
    createElement('tr', {},
      createElement('th', {}, ''),
      createElement('th', {}, 'Overhead'),
      createElement('th', {}, 'Profit'),
      createElement('th', {}, 'Total O&P'),
    ),
  );
  const opTbody = createElement('tbody', {},
    createElement('tr', {},
      createElement('td', {}, 'Adjuster'),
      createElement('td', { className: 'money' }, formatCurrency(op.adjuster_op_applied.overhead)),
      createElement('td', { className: 'money' }, formatCurrency(op.adjuster_op_applied.profit)),
      createElement('td', { className: 'money' }, formatCurrency(op.adjuster_op_applied.overhead + op.adjuster_op_applied.profit)),
    ),
    createElement('tr', {},
      createElement('td', {}, 'Contractor'),
      createElement('td', { className: 'money' }, formatCurrency(op.contractor_op_applied.overhead)),
      createElement('td', { className: 'money' }, formatCurrency(op.contractor_op_applied.profit)),
      createElement('td', { className: 'money' }, formatCurrency(op.contractor_op_applied.overhead + op.contractor_op_applied.profit)),
    ),
    createElement('tr', {},
      createElement('td', {}, createElement('strong', {}, 'Recovery')),
      createElement('td', { className: 'money positive' }),
      createElement('td', { className: 'money positive' }),
      createElement('td', { className: 'money positive' }, `+${formatCurrency(op.op_recovery_amount)}`),
    ),
  );

  opTable.append(opThead, opTbody);
  card.append(warrantedBadge, tradesEl, opTable);
  section.append(title, card);

  return section;
}

/**
 * Render depreciation findings section.
 * @param {Array<Object>} findings
 * @returns {HTMLElement}
 */
function renderDepreciationFindings(findings) {
  if (!findings.length) return createElement('div');

  const section = createElement('div', { className: 'report-section' });

  const title = createElement('div', { className: 'report-section-title' },
    '📉 Depreciation Audit',
  );

  const card = createElement('div', { className: 'card' });
  card.style.padding = '0';
  card.style.overflow = 'auto';

  const table = createElement('table', { className: 'gap-table' });
  const thead = createElement('thead', {},
    createElement('tr', {},
      createElement('th', {}, 'Category'),
      createElement('th', {}, 'Description'),
      createElement('th', {}, 'Depr. %'),
      createElement('th', {}, 'Status'),
      createElement('th', {}, 'Recoverable'),
    ),
  );

  const tbody = createElement('tbody', {});
  for (const f of findings) {
    const statusBadge = f.flagged
      ? createElement('span', { className: 'badge badge-danger' }, '⚠ Excessive')
      : createElement('span', { className: 'badge badge-success' }, '✓ Normal');

    tbody.appendChild(
      createElement('tr', {},
        createElement('td', {}, f.category || '—'),
        createElement('td', {}, f.description),
        createElement('td', { className: 'money' }, formatPercent(f.depreciation_pct, 0)),
        createElement('td', {}, statusBadge),
        createElement('td', { className: f.recoverable_amount ? 'money positive' : 'money' },
          f.recoverable_amount ? `+${formatCurrency(f.recoverable_amount)}` : '—'),
      ),
    );
  }

  table.append(thead, tbody);
  card.appendChild(table);
  section.append(title, card);

  return section;
}

/**
 * Render the full supplement report view.
 * @returns {HTMLElement}
 */
export function renderReportView() {
  const state = getState();
  const container = createElement('div', { className: 'fade-in' });

  const heading = createElement('h1', { className: 'card-title' }, '📊 Supplement Report');
  heading.style.cssText = 'font-size: 1.3rem; margin-bottom: var(--space-lg);';

  if (!state.supplementReport) {
    const empty = createElement('div', { className: 'empty-state' },
      createElement('div', { className: 'empty-state-icon' }, '📊'),
      createElement('div', { className: 'empty-state-title' }, 'No Report Available'),
      createElement('div', { className: 'empty-state-description' },
        'Upload both estimates and run the pipeline to generate a supplement analysis report.'),
    );
    container.append(heading, empty);
    return container;
  }

  const report = state.supplementReport;

  container.append(
    heading,
    renderSummaryStats(report.summary),
    renderGapTable(report.line_item_gaps),
    renderOPAnalysis(report.op_analysis),
    renderDepreciationFindings(report.depreciation_findings),
  );

  return container;
}
