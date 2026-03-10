/**
 * Login View — Email/password, magic link, and Google OAuth authentication.
 *
 * Renders a login form with:
 *   - Google OAuth sign-in
 *   - Email + password sign-in
 *   - Magic link option
 *   - Create account toggle
 *   - Error/success messaging
 */

import { signIn, signUp, sendMagicLink, signInWithGoogle } from '../utils/supabase.js';

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

      <button id="google-signin-btn" class="google-signin-btn">
        <svg width="18" height="18" viewBox="0 0 48 48">
          <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
          <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
          <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
          <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
        </svg>
        Continue with Google
      </button>

      <div class="login-divider">
        <span>or sign in with email</span>
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
  const googleBtn = container.querySelector('#google-signin-btn');
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

  // Google OAuth sign-in
  googleBtn.addEventListener('click', async () => {
    clearMessages();
    googleBtn.disabled = true;
    googleBtn.textContent = 'Redirecting to Google...';

    try {
      const { error } = await signInWithGoogle();
      if (error) {
        showError(error.message || 'Google sign-in failed.');
        googleBtn.disabled = false;
        googleBtn.innerHTML = `
          <svg width="18" height="18" viewBox="0 0 48 48">
            <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
            <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
            <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
            <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
          </svg>
          Continue with Google`;
      }
      // If successful, Supabase redirects to Google — no further action needed here
    } catch (err) {
      showError('Google sign-in failed. Please try again.');
      googleBtn.disabled = false;
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
