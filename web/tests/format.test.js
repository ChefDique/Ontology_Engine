/**
 * Tests — Format Utilities
 */
import { describe, it, expect } from 'vitest';
import { formatCurrency, formatPercent, formatFileSize, moneyClass, gapTypeBadge, gapTypeLabel } from '../src/utils/format.js';

describe('formatCurrency', () => {
  it('formats positive numbers as USD', () => {
    expect(formatCurrency(1234.56)).toBe('$1,234.56');
  });

  it('formats negative numbers with minus sign', () => {
    expect(formatCurrency(-500)).toBe('-$500.00');
  });

  it('returns dash for null/undefined', () => {
    expect(formatCurrency(null)).toBe('—');
    expect(formatCurrency(undefined)).toBe('—');
  });

  it('returns dash for NaN', () => {
    expect(formatCurrency(NaN)).toBe('—');
  });

  it('formats zero as $0.00', () => {
    expect(formatCurrency(0)).toBe('$0.00');
  });
});

describe('formatPercent', () => {
  it('formats ratio as percentage', () => {
    expect(formatPercent(0.15)).toBe('15.0%');
  });

  it('respects custom decimal places', () => {
    expect(formatPercent(0.456, 2)).toBe('45.60%');
  });

  it('returns dash for null', () => {
    expect(formatPercent(null)).toBe('—');
  });
});

describe('formatFileSize', () => {
  it('formats bytes', () => {
    expect(formatFileSize(512)).toBe('512 B');
  });

  it('formats kilobytes', () => {
    expect(formatFileSize(2048)).toBe('2.0 KB');
  });

  it('formats megabytes', () => {
    expect(formatFileSize(5 * 1024 * 1024)).toBe('5.0 MB');
  });

  it('formats zero', () => {
    expect(formatFileSize(0)).toBe('0 B');
  });
});

describe('moneyClass', () => {
  it('returns positive class for positive numbers', () => {
    expect(moneyClass(100)).toBe('money positive');
  });

  it('returns negative class for negative numbers', () => {
    expect(moneyClass(-50)).toBe('money negative');
  });

  it('returns neutral for zero', () => {
    expect(moneyClass(0)).toBe('money');
  });
});

describe('gapTypeBadge', () => {
  it('maps missing_item to danger', () => {
    expect(gapTypeBadge('missing_item')).toBe('badge-danger');
  });

  it('maps quantity_delta to warning', () => {
    expect(gapTypeBadge('quantity_delta')).toBe('badge-warning');
  });

  it('maps pricing_delta to info', () => {
    expect(gapTypeBadge('pricing_delta')).toBe('badge-info');
  });

  it('maps unknown to neutral', () => {
    expect(gapTypeBadge('other')).toBe('badge-neutral');
  });
});

describe('gapTypeLabel', () => {
  it('returns human labels for known types', () => {
    expect(gapTypeLabel('missing_item')).toBe('Missing');
    expect(gapTypeLabel('quantity_delta')).toBe('Qty Δ');
    expect(gapTypeLabel('pricing_delta')).toBe('Price Δ');
  });

  it('passes through unknown types', () => {
    expect(gapTypeLabel('custom')).toBe('custom');
  });
});
