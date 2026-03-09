/**
 * Supabase Client — Frontend authentication and API helpers.
 *
 * Provides:
 *   - Supabase client instance
 *   - Auth helpers (signIn, signUp, signOut, getSession, getAccessToken)
 *   - API fetch wrapper with automatic JWT injection
 */

import { createClient } from '@supabase/supabase-js';

// These come from Vite's env system (prefixed with VITE_)
const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || '';
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY || '';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

/** @type {import('@supabase/supabase-js').SupabaseClient | null} */
let supabase = null;

/**
 * Check if Supabase is configured.
 * @returns {boolean}
 */
export function isSupabaseConfigured() {
  return Boolean(SUPABASE_URL && SUPABASE_ANON_KEY);
}

/**
 * Get or create the Supabase client singleton.
 * @returns {import('@supabase/supabase-js').SupabaseClient}
 */
export function getSupabase() {
  if (!supabase) {
    if (!isSupabaseConfigured()) {
      throw new Error('Supabase is not configured. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY.');
    }
    supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  }
  return supabase;
}

/**
 * Sign in with email and password.
 * @param {string} email
 * @param {string} password
 * @returns {Promise<{user: object|null, error: object|null}>}
 */
export async function signIn(email, password) {
  const { data, error } = await getSupabase().auth.signInWithPassword({ email, password });
  return { user: data?.user || null, error };
}

/**
 * Sign up with email and password.
 * @param {string} email
 * @param {string} password
 * @returns {Promise<{user: object|null, error: object|null}>}
 */
export async function signUp(email, password) {
  const { data, error } = await getSupabase().auth.signUp({ email, password });
  return { user: data?.user || null, error };
}

/**
 * Send a magic link to the user's email.
 * @param {string} email
 * @returns {Promise<{error: object|null}>}
 */
export async function sendMagicLink(email) {
  const { error } = await getSupabase().auth.signInWithOtp({ email });
  return { error };
}

/**
 * Sign out the current user.
 * @returns {Promise<void>}
 */
export async function signOut() {
  await getSupabase().auth.signOut();
}

/**
 * Get the current session (or null if not authenticated).
 * @returns {Promise<{session: object|null, user: object|null}>}
 */
export async function getSession() {
  const { data } = await getSupabase().auth.getSession();
  return {
    session: data?.session || null,
    user: data?.session?.user || null,
  };
}

/**
 * Get the current access token (JWT) for API calls.
 * @returns {Promise<string|null>}
 */
export async function getAccessToken() {
  const { session } = await getSession();
  return session?.access_token || null;
}

/**
 * Fetch wrapper that injects the Supabase JWT into API calls.
 * @param {string} path - API path (e.g., '/api/analyze')
 * @param {RequestInit} options - fetch options
 * @returns {Promise<Response>}
 */
export async function apiFetch(path, options = {}) {
  const token = await getAccessToken();
  const headers = { ...(options.headers || {}) };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = API_BASE_URL ? `${API_BASE_URL}${path}` : path;
  return fetch(url, { ...options, headers });
}

/**
 * Subscribe to auth state changes.
 * @param {(event: string, session: object|null) => void} callback
 * @returns {{ unsubscribe: () => void }}
 */
export function onAuthStateChange(callback) {
  const { data } = getSupabase().auth.onAuthStateChange((event, session) => {
    callback(event, session);
  });
  return { unsubscribe: () => data.subscription.unsubscribe() };
}
