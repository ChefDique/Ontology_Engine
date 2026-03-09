/**
 * TASK_L3 / N3 — Pipeline Status Dashboard
 * Real-time node progress display with contract validation indicators.
 * Now includes error display when pipeline fails.
 */

import { createElement } from '../utils/format.js';
import { getState, setView } from '../utils/state.js';

/**
 * Get the status icon for a pipeline node.
 * @param {string} status
 * @returns {string}
 */
function statusIcon(status) {
  switch (status) {
    case 'completed': return '✅';
    case 'running': return '⏳';
    case 'failed': return '❌';
    default: return '⬜';
  }
}

/**
 * Render a single pipeline node card.
 * @param {Object} node
 * @returns {HTMLElement}
 */
function renderNodeCard(node) {
  const card = createElement('div', {
    className: `pipeline-node ${node.status}`,
    id: `pipeline-node-${node.id}`,
  });

  const header = createElement('div', { className: 'node-header' },
    createElement('span', { className: 'node-number' }, `N${node.id}`),
    createElement('span', {}, statusIcon(node.status)),
  );

  const name = createElement('div', { className: 'node-name' }, node.name);
  const desc = createElement('div', { className: 'node-description' }, node.description);

  const progress = createElement('div', { className: 'node-progress' });
  const bar = createElement('div', { className: 'node-progress-bar' });
  bar.style.width = `${node.progress}%`;
  progress.appendChild(bar);

  // Status badge
  let badge = null;
  if (node.status === 'running') {
    badge = createElement('div', { className: 'badge badge-info' },
      createElement('span', { className: 'pulse-dot blue' }),
      'Processing',
    );
  } else if (node.status === 'completed') {
    badge = createElement('div', { className: 'badge badge-success' }, '✓ Contract Valid');
  } else if (node.status === 'failed') {
    badge = createElement('div', { className: 'badge badge-danger' }, '✗ Failed');
  }

  card.append(header, name, desc, progress);
  if (badge) {
    badge.style.marginTop = 'var(--space-sm)';
    card.appendChild(badge);
  }

  return card;
}

/**
 * Render a connector arrow between pipeline nodes.
 * @param {boolean} active
 * @returns {HTMLElement}
 */
function renderConnector(active) {
  return createElement('div', {
    className: `pipeline-connector ${active ? 'active' : ''}`,
  }, '→');
}

/**
 * Render the pipeline status dashboard.
 * @returns {HTMLElement}
 */
export function renderPipelineView() {
  const state = getState();
  const container = createElement('div', { className: 'pipeline-container fade-in' });

  const heading = createElement('h1', { className: 'card-title' }, '⚡ Pipeline Status');
  heading.style.cssText = 'font-size: 1.3rem; margin-bottom: var(--space-lg);';

  // Running indicator
  let runIndicator = null;
  if (state.pipelineRunning) {
    runIndicator = createElement('div', {
      className: 'badge badge-info',
    },
      createElement('span', { className: 'pulse-dot blue' }),
      'Pipeline Running — this may take 30–60 seconds',
    );
    runIndicator.style.marginBottom = 'var(--space-lg)';
  }

  // Error banner
  let errorBanner = null;
  if (state.pipelineError && !state.pipelineRunning) {
    errorBanner = createElement('div', { className: 'pipeline-error-banner', id: 'pipeline-error' });
    errorBanner.style.cssText = `
      background: var(--color-danger-bg, rgba(239, 68, 68, 0.1));
      border: 1px solid var(--color-danger, #ef4444);
      border-radius: var(--radius-md, 8px);
      padding: var(--space-md, 12px) var(--space-lg, 16px);
      margin-bottom: var(--space-lg, 16px);
      color: var(--color-danger-light, #fca5a5);
    `;

    const errTitle = createElement('div', {}, '❌ Pipeline Failed');
    errTitle.style.cssText = 'font-weight: 600; margin-bottom: 4px;';
    const errDetail = createElement('div', {}, state.pipelineError);
    errDetail.style.cssText = 'font-size: 0.85rem; opacity: 0.9;';

    const retryBtn = createElement('button', {
      className: 'btn btn-ghost',
      onClick: () => setView('upload'),
    }, '← Back to Upload');
    retryBtn.style.cssText = 'margin-top: var(--space-sm, 8px); font-size: 0.85rem;';

    errorBanner.append(errTitle, errDetail, retryBtn);
  }

  // Pipeline visualization
  const pipelineRow = createElement('div', { className: 'pipeline-nodes' });

  state.pipelineNodes.forEach((node, index) => {
    pipelineRow.appendChild(renderNodeCard(node));
    if (index < state.pipelineNodes.length - 1) {
      const prevCompleted = node.status === 'completed';
      pipelineRow.appendChild(renderConnector(prevCompleted));
    }
  });

  // Summary stats
  const allDone = state.pipelineNodes.every((n) => n.status === 'completed');
  let statsSection = null;

  if (allDone) {
    const completedCount = state.pipelineNodes.filter((n) => n.status === 'completed').length;
    const failedCount = state.pipelineNodes.filter((n) => n.status === 'failed').length;

    statsSection = createElement('div', { className: 'stats-row' },
      createElement('div', { className: 'stat-card' },
        createElement('div', { className: 'stat-label' }, 'Nodes Completed'),
        createElement('div', { className: 'stat-value positive' }, String(completedCount)),
      ),
      createElement('div', { className: 'stat-card' },
        createElement('div', { className: 'stat-label' }, 'Nodes Failed'),
        createElement('div', { className: `stat-value ${failedCount > 0 ? 'negative' : ''}` }, String(failedCount)),
      ),
      createElement('div', { className: 'stat-card' },
        createElement('div', { className: 'stat-label' }, 'Contract Validations'),
        createElement('div', { className: 'stat-value positive' }, `${completedCount}/${state.pipelineNodes.length}`),
      ),
      createElement('div', { className: 'stat-card' },
        createElement('div', { className: 'stat-label' }, 'HITL Flags'),
        createElement('div', { className: `stat-value ${state.hitlQueue.length > 0 ? 'negative' : ''}` },
          String(state.hitlQueue.length)),
      ),
    );
    statsSection.style.marginTop = 'var(--space-xl)';

    // Metadata from the real pipeline
    if (state.lastMetadata) {
      const meta = state.lastMetadata;
      const metaEl = createElement('div', { className: 'pipeline-metadata' });
      metaEl.style.cssText = `
        margin-top: var(--space-md, 12px);
        color: var(--text-tertiary, #888);
        font-size: 0.8rem;
        text-align: center;
      `;
      metaEl.textContent = `Completed in ${meta.duration_seconds || '?'}s`;
      if (state.lastAnalysisId) {
        metaEl.textContent += ` · Analysis ID: ${state.lastAnalysisId.substring(0, 8)}…`;
      }
      statsSection.appendChild(metaEl);
    }

    // Action buttons to view results
    const resultActions = createElement('div', { className: 'pipeline-result-actions' });
    resultActions.style.cssText = `
      display: flex;
      gap: var(--space-md, 12px);
      justify-content: center;
      margin-top: var(--space-lg, 16px);
    `;

    const viewReportBtn = createElement('button', {
      className: 'btn btn-primary',
      onClick: () => setView('report'),
    }, '📊 View Report');

    const viewReviewBtn = createElement('button', {
      className: 'btn btn-ghost',
      onClick: () => setView('review'),
    }, '🔍 Review Queue');

    resultActions.append(viewReportBtn, viewReviewBtn);
    statsSection.appendChild(resultActions);
  }

  container.append(heading);
  if (runIndicator) container.appendChild(runIndicator);
  if (errorBanner) container.appendChild(errorBanner);
  container.appendChild(pipelineRow);
  if (statsSection) container.appendChild(statsSection);

  return container;
}
