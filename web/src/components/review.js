/**
 * TASK_L5 — HITL Review Interface
 * Lists flagged items, provides approve/reject actions, shows queue status.
 */

import { createElement } from '../utils/format.js';
import { getState, resolveHitlItem } from '../utils/state.js';

/**
 * Get the severity badge class.
 * @param {string} severity
 * @returns {string}
 */
function severityBadge(severity) {
  switch (severity) {
    case 'danger': return 'badge-danger';
    case 'warning': return 'badge-warning';
    case 'info': return 'badge-info';
    default: return 'badge-neutral';
  }
}

/**
 * Get a human-readable type label.
 * @param {string} type
 * @returns {string}
 */
function typeLabel(type) {
  switch (type) {
    case 'f9_override': return '📝 F9 Override';
    case 'low_confidence': return '🔍 Low Confidence';
    case 'threshold_breach': return '⚠️ Threshold Breach';
    default: return type;
  }
}

/**
 * Render a single HITL queue item.
 * @param {Object} item
 * @param {number} index
 * @returns {HTMLElement}
 */
function renderHitlItem(item, index) {
  const el = createElement('div', {
    className: 'hitl-item',
    id: `hitl-item-${index}`,
  });

  const severityEl = createElement('span', { className: `badge ${severityBadge(item.severity)}` },
    typeLabel(item.type),
  );

  const info = createElement('div', { className: 'hitl-item-info' },
    createElement('div', { className: 'hitl-item-title' }, item.title),
    createElement('div', { className: 'hitl-item-meta' },
      `Node ${item.nodeId} · ${item.lineItem} · ${item.description}`,
    ),
  );

  const actions = createElement('div', { className: 'hitl-item-actions' },
    createElement('button', {
      className: 'btn btn-success btn-sm',
      id: `hitl-approve-${index}`,
      onClick: () => resolveHitlItem(index),
    }, '✓ Approve'),
    createElement('button', {
      className: 'btn btn-danger btn-sm',
      id: `hitl-reject-${index}`,
      onClick: () => resolveHitlItem(index),
    }, '✗ Reject'),
  );

  el.append(severityEl, info, actions);
  return el;
}

/**
 * Render the HITL review interface.
 * @returns {HTMLElement}
 */
export function renderReviewView() {
  const state = getState();
  const container = createElement('div', { className: 'fade-in' });

  const heading = createElement('h1', { className: 'card-title' }, '🔍 HITL Review Queue');
  heading.style.cssText = 'font-size: 1.3rem; margin-bottom: var(--space-sm);';

  const subtitle = createElement('p', { className: 'card-subtitle' },
    'Items flagged by the pipeline requiring human review before final output.',
  );
  subtitle.style.marginBottom = 'var(--space-lg)';

  // Queue status bar
  const statusBar = createElement('div', { className: 'stats-row' },
    createElement('div', { className: 'stat-card' },
      createElement('div', { className: 'stat-label' }, 'Pending Review'),
      createElement('div', { className: `stat-value ${state.hitlQueue.length > 0 ? 'negative' : 'positive'}` },
        String(state.hitlQueue.length)),
    ),
    createElement('div', { className: 'stat-card' },
      createElement('div', { className: 'stat-label' }, 'Queue Status'),
      state.hitlQueue.length > 0
        ? createElement('div', { className: 'badge badge-warning' },
            createElement('span', { className: 'pulse-dot yellow' }),
            'Action Required',
          )
        : createElement('div', { className: 'badge badge-success' }, '✓ All Clear'),
    ),
  );

  container.append(heading, subtitle, statusBar);

  if (state.hitlQueue.length === 0) {
    const empty = createElement('div', { className: 'hitl-empty' },
      createElement('div', { className: 'hitl-empty-icon' }, '✅'),
      createElement('div', { className: 'empty-state-title' }, 'Queue Empty'),
      createElement('div', { className: 'empty-state-description' },
        'No items pending review. All pipeline outputs have been validated.'),
    );
    container.appendChild(empty);
  } else {
    const queue = createElement('div', { className: 'hitl-queue' });
    state.hitlQueue.forEach((item, i) => {
      queue.appendChild(renderHitlItem(item, i));
    });
    container.appendChild(queue);
  }

  return container;
}
