/**
 * Ontology Engine — Main Application Entry Point
 * Wires the app shell, navigation, and view rendering.
 */

import './styles/design-system.css';
import { subscribe, getState, setView } from './utils/state.js';
import { renderUploadView } from './components/upload.js';
import { renderPipelineView } from './components/pipeline.js';
import { renderReportView } from './components/report.js';
import { renderReviewView } from './components/review.js';

/** @type {Object<string, { label: string, icon: string, render: Function }>} */
const VIEWS = {
  upload: { label: 'Upload', icon: '📤', render: renderUploadView },
  pipeline: { label: 'Pipeline', icon: '⚡', render: renderPipelineView },
  report: { label: 'Report', icon: '📊', render: renderReportView },
  review: { label: 'Review', icon: '🔍', render: renderReviewView },
};

/**
 * Render the full application into #app.
 */
function renderApp() {
  const app = document.getElementById('app');
  if (!app) return;

  const state = getState();

  app.innerHTML = '';

  // ── Header ──
  const header = document.createElement('header');
  header.className = 'app-header';

  const logo = document.createElement('div');
  logo.className = 'app-logo';
  logo.innerHTML = `
    <div class="app-logo-icon">⚙️</div>
    <span class="app-logo-text">Ontology Engine</span>
  `;

  const nav = document.createElement('nav');
  nav.className = 'app-nav';
  nav.setAttribute('role', 'navigation');
  nav.setAttribute('aria-label', 'Main navigation');

  for (const [key, view] of Object.entries(VIEWS)) {
    const btn = document.createElement('button');
    btn.className = `nav-tab ${state.activeView === key ? 'active' : ''}`;
    btn.textContent = `${view.icon} ${view.label}`;
    btn.id = `nav-${key}`;
    btn.setAttribute('role', 'tab');
    btn.setAttribute('aria-selected', state.activeView === key);
    btn.addEventListener('click', () => setView(key));
    nav.appendChild(btn);
  }

  header.append(logo, nav);

  // ── Main Content ──
  const main = document.createElement('main');
  main.className = 'app-main';
  main.setAttribute('role', 'main');

  const viewConfig = VIEWS[state.activeView];
  if (viewConfig) {
    main.appendChild(viewConfig.render());
  }

  app.append(header, main);
}

// Subscribe to state changes → re-render
subscribe(renderApp);

// Initial render
renderApp();
