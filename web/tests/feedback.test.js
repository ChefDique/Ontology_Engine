/**
 * Tests — Feedback Widget (Agent Q)
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { JSDOM } from 'jsdom';

// Set up jsdom globals
const dom = new JSDOM('<!DOCTYPE html><html><body><div id="app"></div></body></html>');
globalThis.document = dom.window.document;
globalThis.window = dom.window;
globalThis.HTMLElement = dom.window.HTMLElement;
globalThis.requestAnimationFrame = (fn) => setTimeout(fn, 0);
globalThis.URL = dom.window.URL || { createObjectURL: () => 'blob:mock' };

// Mock URL.createObjectURL for image thumbnails
if (!globalThis.URL.createObjectURL) {
  globalThis.URL.createObjectURL = () => 'blob:mock-url';
}

import { createFeedbackButton, createFeedbackLink, isSpeechSupported, toggleFeedback, closeFeedback } from '../src/components/feedback.js';

describe('Feedback Widget', () => {
  beforeEach(() => {
    // Clean up any modals from previous tests
    const modal = document.getElementById('feedback-modal-overlay');
    if (modal) modal.remove();
  });

  describe('createFeedbackButton', () => {
    it('returns a button element', () => {
      const btn = createFeedbackButton();
      expect(btn.tagName).toBe('BUTTON');
    });

    it('has the feedback-fab class', () => {
      const btn = createFeedbackButton();
      expect(btn.classList.contains('feedback-fab')).toBe(true);
    });

    it('has the correct id', () => {
      const btn = createFeedbackButton();
      expect(btn.id).toBe('feedback-fab');
    });

    it('contains the chat emoji', () => {
      const btn = createFeedbackButton();
      expect(btn.textContent).toContain('💬');
    });
  });

  describe('createFeedbackLink', () => {
    it('returns a button element with inline link class', () => {
      const link = createFeedbackLink('report');
      expect(link.tagName).toBe('BUTTON');
      expect(link.classList.contains('feedback-inline-link')).toBe(true);
    });

    it('uses context in the id', () => {
      const link = createFeedbackLink('review');
      expect(link.id).toBe('feedback-link-review');
    });

    it('defaults to general context', () => {
      const link = createFeedbackLink();
      expect(link.id).toBe('feedback-link-general');
    });

    it('shows feedback text', () => {
      const link = createFeedbackLink('report');
      expect(link.textContent).toContain('Give Feedback');
    });
  });

  describe('isSpeechSupported', () => {
    it('returns false when SpeechRecognition is not available', () => {
      // jsdom doesn't have SpeechRecognition
      delete window.SpeechRecognition;
      delete window.webkitSpeechRecognition;
      expect(isSpeechSupported()).toBe(false);
    });

    it('returns true when SpeechRecognition is available', () => {
      window.SpeechRecognition = class {};
      expect(isSpeechSupported()).toBe(true);
      delete window.SpeechRecognition;
    });

    it('returns true when webkitSpeechRecognition is available', () => {
      window.webkitSpeechRecognition = class {};
      expect(isSpeechSupported()).toBe(true);
      delete window.webkitSpeechRecognition;
    });
  });

  describe('toggleFeedback', () => {
    it('opens the modal overlay on first call', () => {
      toggleFeedback();
      const overlay = document.getElementById('feedback-modal-overlay');
      expect(overlay).toBeTruthy();
      expect(overlay.classList.contains('feedback-overlay')).toBe(true);
      // Clean up
      closeFeedback();
    });

    it('renders the modal with all key elements', () => {
      toggleFeedback();
      const modal = document.getElementById('feedback-modal');
      expect(modal).toBeTruthy();

      // Title
      const title = modal.querySelector('.feedback-modal-title');
      expect(title).toBeTruthy();
      expect(title.textContent).toContain('Feedback');

      // Close button
      const closeBtn = document.getElementById('feedback-close-btn');
      expect(closeBtn).toBeTruthy();

      // Category buttons
      const catBtns = modal.querySelectorAll('.feedback-category-btn');
      expect(catBtns.length).toBe(4);

      // Textarea
      const textarea = document.getElementById('feedback-text');
      expect(textarea).toBeTruthy();
      expect(textarea.tagName).toBe('TEXTAREA');

      // Submit button
      const submitBtn = document.getElementById('feedback-submit-btn');
      expect(submitBtn).toBeTruthy();

      // Cancel button
      const cancelBtn = document.getElementById('feedback-cancel-btn');
      expect(cancelBtn).toBeTruthy();

      closeFeedback();
    });

    it('suggestion category is selected by default', () => {
      toggleFeedback();
      const suggestionBtn = document.getElementById('feedback-cat-suggestion');
      expect(suggestionBtn.classList.contains('active')).toBe(true);
      closeFeedback();
    });
  });

  describe('closeFeedback', () => {
    it('removes the modal overlay', () => {
      toggleFeedback();
      expect(document.getElementById('feedback-modal-overlay')).toBeTruthy();

      closeFeedback();
      expect(document.getElementById('feedback-modal-overlay')).toBeFalsy();
    });
  });

  describe('Category Selection', () => {
    it('switches active category on click', () => {
      toggleFeedback();

      const bugBtn = document.getElementById('feedback-cat-bug');
      const suggestionBtn = document.getElementById('feedback-cat-suggestion');

      expect(suggestionBtn.classList.contains('active')).toBe(true);
      expect(bugBtn.classList.contains('active')).toBe(false);

      bugBtn.click();

      expect(bugBtn.classList.contains('active')).toBe(true);
      expect(suggestionBtn.classList.contains('active')).toBe(false);

      closeFeedback();
    });
  });

  describe('Textarea Validation', () => {
    it('shakes textarea when submitting empty text', () => {
      toggleFeedback();
      const submitBtn = document.getElementById('feedback-submit-btn');
      const textarea = document.getElementById('feedback-text');

      textarea.value = '';
      submitBtn.click();

      // Textarea should get the error class momentarily
      expect(textarea.classList.contains('feedback-textarea-error')).toBe(true);

      closeFeedback();
    });
  });
});
