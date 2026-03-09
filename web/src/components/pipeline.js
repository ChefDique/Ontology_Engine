/**
 * TASK_L3 — Pipeline Status Dashboard
 * Real-time node progress display with contract validation indicators.
 */

import { createElement } from '../utils/format.js';
import { getState } from '../utils/state.js';

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
      'Pipeline Running',
    );
    runIndicator.style.marginBottom = 'var(--space-lg)';
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
  }

  container.append(heading);
  if (runIndicator) container.appendChild(runIndicator);
  container.appendChild(pipelineRow);
  if (statsSection) container.appendChild(statsSection);

  return container;
}
