/**
 * Ontology Engine — Main Application Entry Point
 * Wires the app shell, navigation, view rendering, and auth gate.
 */

import './styles/design-system.css';
import { subscribe, getState, setView } from './utils/state.js';
import { renderUploadView } from './components/upload.js';
import { renderPipelineView } from './components/pipeline.js';
import { renderReportView } from './components/report.js';
import { renderReviewView } from './components/review.js';
import { renderLoginView } from './components/login.js';
import { isSupabaseConfigured, getSession, signOut, onAuthStateChange } from './utils/supabase.js';

/** @type {Object<string, { label: string, icon: string, render: Function }>} */
const VIEWS = {
  upload: { label: 'Upload', icon: '📤', render: renderUploadView },
  pipeline: { label: 'Pipeline', icon: '⚡', render: renderPipelineView },
  report: { label: 'Report', icon: '📊', render: renderReportView },
  review: { label: 'Review', icon: '🔍', render: renderReviewView },
};

/** @type {{ user: object|null, loading: boolean }} */
let authState = { user: null, loading: true };

/**
 * Render the full application into #app.
 */
function renderApp() {
  const app = document.getElementById('app');
  if (!app) return;

  const state = getState();
  app.innerHTML = '';

  // ── Auth loading state ──
  if (authState.loading) {
    const loader = document.createElement('div');
    loader.className = 'app-loading';
    loader.innerHTML = `
      <div class="app-logo-icon" style="font-size: 3rem;">⚙️</div>
      <p>Loading...</p>
    `;
    app.appendChild(loader);
    return;
  }

  // ── Auth gate: show login if Supabase is configured and user is not authenticated ──
  if (isSupabaseConfigured() && !authState.user) {
    app.appendChild(renderLoginView());
    return;
  }

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

  // ── User menu (sign out) ──
  if (isSupabaseConfigured() && authState.user) {
    const userMenu = document.createElement('div');
    userMenu.className = 'user-menu';
    userMenu.innerHTML = `
      <span class="user-email">${authState.user.email || ''}</span>
      <button id="sign-out-btn" class="btn-link">Sign out</button>
    `;
    userMenu.querySelector('#sign-out-btn').addEventListener('click', async () => {
      await signOut();
    });
    header.append(logo, nav, userMenu);
  } else {
    header.append(logo, nav);
  }

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

// ── Auth initialization ──
async function initAuth() {
  if (!isSupabaseConfigured()) {
    // No Supabase → skip auth, render immediately
    authState = { user: null, loading: false };
    renderApp();
    return;
  }

  try {
    const { user } = await getSession();
    authState = { user, loading: false };
  } catch {
    authState = { user: null, loading: false };
  }

  renderApp();

  // Listen for auth changes (login, logout, token refresh)
  onAuthStateChange((_event, session) => {
    authState = { user: session?.user || null, loading: false };
    renderApp();
  });
}

// Subscribe to state changes → re-render
subscribe(renderApp);

// Boot
initAuth();
