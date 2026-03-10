/**
 * Q2-Q4 — Feedback Widget (Paste + Voice + Supabase)
 *
 * Features:
 *   - Floating feedback button (💬) anchored bottom-right
 *   - Modal with textarea supporting clipboard paste for screenshots
 *   - Web Speech API microphone button for voice-to-text
 *   - Category selector (bug, suggestion, question, other)
 *   - Submits to Supabase: text → feedback table, screenshots → storage bucket
 */

import { createElement } from '../utils/format.js';
import { getState } from '../utils/state.js';
import { getSupabase, isSupabaseConfigured, getAccessToken } from '../utils/supabase.js';

/** @type {boolean} */
let isOpen = false;

/** @type {File[]} */
let attachedImages = [];

/** @type {boolean} */
let isRecording = false;

/** @type {SpeechRecognition|null} */
let recognition = null;

/** @type {boolean} */
let isSubmitting = false;

/* ── Helpers ── */

/**
 * Check if Web Speech API is available.
 * @returns {boolean}
 */
export function isSpeechSupported() {
  return !!(window.SpeechRecognition || window.webkitSpeechRecognition);
}

/**
 * Toggle the feedback modal open/closed.
 */
export function toggleFeedback() {
  isOpen = !isOpen;
  renderFeedbackModal();
}

/**
 * Close the feedback modal and reset state.
 */
export function closeFeedback() {
  isOpen = false;
  attachedImages = [];
  isRecording = false;
  isSubmitting = false;
  if (recognition) {
    recognition.abort();
    recognition = null;
  }
  renderFeedbackModal();
}

/* ── Speech Recognition ── */

/**
 * Start/stop voice recording via Web Speech API.
 * Appends recognized text to the textarea.
 * @param {HTMLTextAreaElement} textarea
 * @param {HTMLButtonElement} micBtn
 */
function toggleVoice(textarea, micBtn) {
  if (isRecording && recognition) {
    recognition.stop();
    isRecording = false;
    micBtn.classList.remove('recording');
    micBtn.textContent = '🎙️';
    return;
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) return;

  recognition = new SpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = 'en-US';

  let finalTranscript = '';

  recognition.onresult = (event) => {
    let interim = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const t = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalTranscript += t + ' ';
      } else {
        interim = t;
      }
    }
    // Append final transcript to textarea
    if (finalTranscript) {
      const cursor = textarea.selectionStart;
      const before = textarea.value.slice(0, cursor);
      const after = textarea.value.slice(cursor);
      textarea.value = before + finalTranscript + after;
      textarea.selectionStart = textarea.selectionEnd = cursor + finalTranscript.length;
      finalTranscript = '';
    }
  };

  recognition.onerror = () => {
    isRecording = false;
    micBtn.classList.remove('recording');
    micBtn.textContent = '🎙️';
  };

  recognition.onend = () => {
    isRecording = false;
    micBtn.classList.remove('recording');
    micBtn.textContent = '🎙️';
  };

  recognition.start();
  isRecording = true;
  micBtn.classList.add('recording');
  micBtn.textContent = '⏹️';
}

/* ── Clipboard Paste ── */

/**
 * Handle paste event on the textarea to capture images.
 * @param {ClipboardEvent} e
 */
function handlePaste(e) {
  const items = e.clipboardData?.items;
  if (!items) return;

  for (const item of items) {
    if (item.type.startsWith('image/')) {
      e.preventDefault();
      const file = item.getAsFile();
      if (file && attachedImages.length < 5) {
        attachedImages.push(file);
        renderAttachments();
      }
      return; // only handle first image
    }
  }
  // If no images, allow normal text paste
}

/**
 * Re-render the attachments preview strip.
 */
function renderAttachments() {
  const strip = document.getElementById('feedback-attachments');
  if (!strip) return;

  strip.innerHTML = '';

  attachedImages.forEach((file, i) => {
    const thumb = document.createElement('div');
    thumb.className = 'feedback-thumb';

    const img = document.createElement('img');
    img.src = URL.createObjectURL(file);
    img.alt = `Screenshot ${i + 1}`;

    const remove = document.createElement('button');
    remove.className = 'feedback-thumb-remove';
    remove.textContent = '×';
    remove.title = 'Remove';
    remove.addEventListener('click', (e) => {
      e.stopPropagation();
      attachedImages.splice(i, 1);
      renderAttachments();
    });

    thumb.append(img, remove);
    strip.appendChild(thumb);
  });

  // Update counter
  const counter = document.getElementById('feedback-attachment-count');
  if (counter) {
    counter.textContent = attachedImages.length > 0
      ? `${attachedImages.length}/5 screenshot${attachedImages.length > 1 ? 's' : ''}`
      : 'Paste (Ctrl+V) to attach screenshots';
  }
}

/* ── Submission ── */

/**
 * Submit feedback to Supabase.
 * @param {string} text
 * @param {string} category
 * @returns {Promise<{success: boolean, error?: string}>}
 */
export async function submitFeedback(text, category) {
  if (!isSupabaseConfigured()) {
    return { success: false, error: 'Supabase is not configured' };
  }

  isSubmitting = true;
  updateSubmitButton();

  try {
    const supabase = getSupabase();
    const state = getState();

    // Upload screenshots to storage
    const screenshotUrls = [];
    for (let i = 0; i < attachedImages.length; i++) {
      const file = attachedImages[i];
      const ext = file.type.split('/')[1] || 'png';
      const path = `feedback/${Date.now()}-${i}.${ext}`;

      const { error: uploadError } = await supabase.storage
        .from('feedback-screenshots')
        .upload(path, file, { contentType: file.type });

      if (!uploadError) {
        const { data: urlData } = supabase.storage
          .from('feedback-screenshots')
          .getPublicUrl(path);
        screenshotUrls.push(urlData.publicUrl);
      }
    }

    // Insert feedback record
    const { error: insertError } = await supabase
      .from('feedback')
      .insert({
        text,
        category,
        screenshots: screenshotUrls,
        analysis_id: state.lastAnalysisId || null,
        view_context: state.activeView,
      });

    if (insertError) {
      isSubmitting = false;
      updateSubmitButton();
      return { success: false, error: insertError.message };
    }

    isSubmitting = false;
    return { success: true };

  } catch (err) {
    isSubmitting = false;
    updateSubmitButton();
    return { success: false, error: err.message || 'Unexpected error' };
  }
}

/**
 * Update the submit button state during submission.
 */
function updateSubmitButton() {
  const btn = document.getElementById('feedback-submit-btn');
  if (!btn) return;
  if (isSubmitting) {
    btn.setAttribute('disabled', 'true');
    btn.textContent = '⏳ Sending...';
  } else {
    btn.removeAttribute('disabled');
    btn.textContent = '📨 Send Feedback';
  }
}

/* ── Rendering ── */

/**
 * Render the feedback modal (overlay) into the DOM.
 * Called on open/close toggle.
 */
function renderFeedbackModal() {
  // Remove existing modal
  const existing = document.getElementById('feedback-modal-overlay');
  if (existing) existing.remove();

  if (!isOpen) return;

  // Overlay
  const overlay = createElement('div', {
    className: 'feedback-overlay',
    id: 'feedback-modal-overlay',
  });

  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) closeFeedback();
  });

  // Modal
  const modal = createElement('div', {
    className: 'feedback-modal',
    id: 'feedback-modal',
  });

  // ── Header ──
  const header = createElement('div', { className: 'feedback-modal-header' },
    createElement('h2', { className: 'feedback-modal-title' }, '💬 Send Feedback'),
    createElement('button', {
      className: 'feedback-close-btn',
      id: 'feedback-close-btn',
      onClick: closeFeedback,
    }, '×'),
  );

  // ── Category selector ──
  const categoryRow = createElement('div', { className: 'feedback-category-row' });
  const categories = [
    { value: 'bug', label: '🐛 Bug', },
    { value: 'suggestion', label: '💡 Suggestion' },
    { value: 'question', label: '❓ Question' },
    { value: 'other', label: '📝 Other' },
  ];

  let selectedCategory = 'suggestion';

  categories.forEach(({ value, label }) => {
    const btn = createElement('button', {
      className: `feedback-category-btn ${value === selectedCategory ? 'active' : ''}`,
      id: `feedback-cat-${value}`,
    }, label);
    btn.addEventListener('click', () => {
      selectedCategory = value;
      categoryRow.querySelectorAll('.feedback-category-btn').forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
    });
    categoryRow.appendChild(btn);
  });

  // ── Textarea ──
  const textarea = document.createElement('textarea');
  textarea.className = 'feedback-textarea';
  textarea.id = 'feedback-text';
  textarea.placeholder = 'Describe your feedback… (paste screenshots with Ctrl+V)';
  textarea.rows = 5;
  textarea.addEventListener('paste', handlePaste);

  // ── Attachments preview strip ──
  const attachStrip = createElement('div', {
    className: 'feedback-attachments',
    id: 'feedback-attachments',
  });

  const attachCounter = createElement('div', {
    className: 'feedback-attachment-hint',
    id: 'feedback-attachment-count',
  }, 'Paste (Ctrl+V) to attach screenshots');

  // ── Toolbar (mic button) ──
  const toolbar = createElement('div', { className: 'feedback-toolbar' });

  if (isSpeechSupported()) {
    const micBtn = createElement('button', {
      className: 'btn btn-ghost btn-sm feedback-mic-btn',
      id: 'feedback-mic-btn',
      title: 'Voice-to-text',
    }, '🎙️');
    micBtn.addEventListener('click', () => toggleVoice(textarea, micBtn));
    toolbar.appendChild(micBtn);
  }

  // ── Actions ──
  const actions = createElement('div', { className: 'feedback-actions' });

  const cancelBtn = createElement('button', {
    className: 'btn btn-ghost',
    id: 'feedback-cancel-btn',
    onClick: closeFeedback,
  }, 'Cancel');

  const submitBtn = createElement('button', {
    className: 'btn btn-primary',
    id: 'feedback-submit-btn',
  }, '📨 Send Feedback');

  submitBtn.addEventListener('click', async () => {
    const text = textarea.value.trim();
    if (!text) {
      textarea.classList.add('feedback-textarea-error');
      setTimeout(() => textarea.classList.remove('feedback-textarea-error'), 1500);
      return;
    }

    const result = await submitFeedback(text, selectedCategory);

    if (result.success) {
      // Show success state briefly, then close
      modal.innerHTML = '';
      const successEl = createElement('div', { className: 'feedback-success' },
        createElement('div', { className: 'feedback-success-icon' }, '✅'),
        createElement('div', { className: 'feedback-success-text' }, 'Thank you! Your feedback has been submitted.'),
      );
      modal.appendChild(successEl);
      setTimeout(() => closeFeedback(), 1800);
    } else {
      // Show error inline
      let errorEl = modal.querySelector('.feedback-error');
      if (!errorEl) {
        errorEl = createElement('div', { className: 'feedback-error' });
        actions.after(errorEl);
      }
      errorEl.textContent = `❌ ${result.error}`;
    }
  });

  actions.append(cancelBtn, submitBtn);
  toolbar.appendChild(actions);

  modal.append(header, categoryRow, textarea, attachStrip, attachCounter, toolbar);
  overlay.appendChild(modal);
  document.body.appendChild(overlay);

  // Focus textarea after render
  requestAnimationFrame(() => textarea.focus());
}

/**
 * Create the floating feedback trigger button.
 * Should be called once to add to the DOM.
 * @returns {HTMLElement}
 */
export function createFeedbackButton() {
  const btn = createElement('button', {
    className: 'feedback-fab',
    id: 'feedback-fab',
    title: 'Send feedback',
  }, '💬');

  btn.addEventListener('click', toggleFeedback);

  return btn;
}

/**
 * Create an inline "Give Feedback" link for embedding in report/review views.
 * @param {string} [context] - Additional context (e.g., 'report', 'review')
 * @returns {HTMLElement}
 */
export function createFeedbackLink(context) {
  const link = createElement('button', {
    className: 'btn btn-ghost btn-sm feedback-inline-link',
    id: `feedback-link-${context || 'general'}`,
  }, '💬 Give Feedback');

  link.addEventListener('click', () => {
    toggleFeedback();
    // Pre-fill context after modal renders
    requestAnimationFrame(() => {
      const textarea = document.getElementById('feedback-text');
      if (textarea && context) {
        textarea.placeholder = `Feedback on the ${context} view…`;
      }
    });
  });

  return link;
}
