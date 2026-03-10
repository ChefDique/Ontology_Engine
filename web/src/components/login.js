/**
 * Login View — Email/password + magic link authentication.
 *
 * Renders a login form with:
 *   - Email + password sign-in
 *   - Magic link option
 *   - Create account toggle
 *   - Error/success messaging
 */

import { signIn, signUp, sendMagicLink } from '../utils/supabase.js';

/**
 * Render the login view.
 * @returns {HTMLElement}
 */
export function renderLoginView() {
  const container = document.createElement('div');
  container.className = 'login-view';
  container.id = 'login-view';

  container.innerHTML = `
    <div class="login-card">
      <div class="login-header">
        <div class="login-logo">⚙️</div>
        <h1 class="login-title">Ontology Engine</h1>
        <p class="login-subtitle">Insurance estimate analysis platform</p>
      </div>

      <form id="login-form" class="login-form">
        <div class="form-group">
          <label for="login-email">Email</label>
          <input
            type="email"
            id="login-email"
            name="email"
            placeholder="you@company.com"
            required
            autocomplete="email"
          />
        </div>

        <div class="form-group" id="password-group">
          <label for="login-password">Password</label>
          <input
            type="password"
            id="login-password"
            name="password"
            placeholder="••••••••"
            minlength="6"
            autocomplete="current-password"
          />
        </div>

        <div id="login-error" class="login-error" hidden></div>
        <div id="login-success" class="login-success" hidden></div>

        <button type="submit" id="login-submit" class="btn-primary">
          Sign In
        </button>
      </form>

      <div class="login-divider">
        <span>or</span>
      </div>

      <button id="magic-link-btn" class="btn-secondary">
        ✉️ Send Magic Link
      </button>

      <div class="login-toggle">
        <span id="toggle-text">Don't have an account?</span>
        <button id="toggle-mode" class="btn-link">Create one</button>
      </div>
    </div>
  `;

  // State
  let isSignUp = false;

  // Elements
  const form = container.querySelector('#login-form');
  const emailInput = container.querySelector('#login-email');
  const passwordInput = container.querySelector('#login-password');
  const passwordGroup = container.querySelector('#password-group');
  const submitBtn = container.querySelector('#login-submit');
  const magicLinkBtn = container.querySelector('#magic-link-btn');
  const toggleBtn = container.querySelector('#toggle-mode');
  const toggleText = container.querySelector('#toggle-text');
  const errorDiv = container.querySelector('#login-error');
  const successDiv = container.querySelector('#login-success');

  function showError(msg) {
    errorDiv.textContent = msg;
    errorDiv.hidden = false;
    successDiv.hidden = true;
  }

  function showSuccess(msg) {
    successDiv.textContent = msg;
    successDiv.hidden = false;
    errorDiv.hidden = true;
  }

  function clearMessages() {
    errorDiv.hidden = true;
    successDiv.hidden = true;
  }

  function setLoading(loading) {
    submitBtn.disabled = loading;
    magicLinkBtn.disabled = loading;
    submitBtn.textContent = loading
      ? 'Please wait...'
      : (isSignUp ? 'Create Account' : 'Sign In');
  }

  // Toggle sign-in / sign-up mode
  toggleBtn.addEventListener('click', () => {
    isSignUp = !isSignUp;
    clearMessages();
    submitBtn.textContent = isSignUp ? 'Create Account' : 'Sign In';
    toggleText.textContent = isSignUp
      ? 'Already have an account?'
      : "Don't have an account?";
    toggleBtn.textContent = isSignUp ? 'Sign in' : 'Create one';
    if (isSignUp) {
      passwordInput.setAttribute('autocomplete', 'new-password');
    } else {
      passwordInput.setAttribute('autocomplete', 'current-password');
    }
  });

  // Form submit (email + password)
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearMessages();
    setLoading(true);

    const email = emailInput.value.trim();
    const password = passwordInput.value;

    if (!email) {
      showError('Please enter your email address.');
      setLoading(false);
      return;
    }

    try {
      if (isSignUp) {
        const { user, error } = await signUp(email, password);
        if (error) {
          showError(error.message || 'Sign up failed.');
        } else if (user) {
          showSuccess('Account created! Check your email to confirm.');
        }
      } else {
        const { user, error } = await signIn(email, password);
        if (error) {
          showError(error.message || 'Sign in failed.');
        }
        // If successful, onAuthStateChange in main.js will re-render
      }
    } catch (err) {
      showError('An unexpected error occurred. Please try again.');
    }

    setLoading(false);
  });

  // Magic link button
  magicLinkBtn.addEventListener('click', async () => {
    clearMessages();
    const email = emailInput.value.trim();

    if (!email) {
      showError('Please enter your email to receive a magic link.');
      return;
    }

    setLoading(true);

    try {
      const { error } = await sendMagicLink(email);
      if (error) {
        showError(error.message || 'Failed to send magic link.');
      } else {
        showSuccess(`Magic link sent to ${email}. Check your inbox!`);
      }
    } catch (err) {
      showError('Failed to send magic link. Please try again.');
    }

    setLoading(false);
  });

  return container;
}
