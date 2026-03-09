/**
 * Tests — Upload Validation
 */
import { describe, it, expect } from 'vitest';
import { validateFile } from '../src/components/upload.js';

describe('validateFile', () => {
  it('rejects null/undefined files', () => {
    expect(validateFile(null).valid).toBe(false);
    expect(validateFile(undefined).valid).toBe(false);
  });

  it('rejects non-PDF files', () => {
    const file = { type: 'image/png', size: 1024 };
    const result = validateFile(file);
    expect(result.valid).toBe(false);
    expect(result.error).toContain('PDF');
  });

  it('rejects files exceeding 50MB', () => {
    const file = { type: 'application/pdf', size: 51 * 1024 * 1024 };
    const result = validateFile(file);
    expect(result.valid).toBe(false);
    expect(result.error).toContain('limit');
  });

  it('rejects empty files', () => {
    const file = { type: 'application/pdf', size: 0 };
    const result = validateFile(file);
    expect(result.valid).toBe(false);
    expect(result.error).toContain('empty');
  });

  it('accepts valid PDF files', () => {
    const file = { type: 'application/pdf', size: 1024 * 1024 };
    const result = validateFile(file);
    expect(result.valid).toBe(true);
    expect(result.error).toBeUndefined();
  });

  it('accepts PDFs at exactly the size limit', () => {
    const file = { type: 'application/pdf', size: 50 * 1024 * 1024 };
    const result = validateFile(file);
    expect(result.valid).toBe(true);
  });
});
