/**
 * Ontology Engine — Format Utilities
 * Shared formatting helpers for currency, percentages, dates, and DOM.
 */

/**
 * Format a number as USD currency.
 * @param {number} value
 * @returns {string}
 */
export function formatCurrency(value) {
  if (value == null || isNaN(value)) return '—';
  const abs = Math.abs(value);
  const formatted = abs.toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  });
  return value < 0 ? `-${formatted}` : formatted;
}

/**
 * Format a number as a percentage.
 * @param {number} value - Raw ratio (e.g. 0.15 for 15%)
 * @param {number} decimals
 * @returns {string}
 */
export function formatPercent(value, decimals = 1) {
  if (value == null || isNaN(value)) return '—';
  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Format a file size in bytes to a human-readable string.
 * @param {number} bytes
 * @returns {string}
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(i > 0 ? 1 : 0)} ${units[i]}`;
}

/**
 * Create a DOM element with attributes and children.
 * @param {string} tag
 * @param {Object} attrs
 * @param  {...(Node|string)} children
 * @returns {HTMLElement}
 */
export function createElement(tag, attrs = {}, ...children) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key === 'className') {
      el.className = value;
    } else if (key === 'dataset') {
      for (const [dk, dv] of Object.entries(value)) {
        el.dataset[dk] = dv;
      }
    } else if (key.startsWith('on') && typeof value === 'function') {
      el.addEventListener(key.slice(2).toLowerCase(), value);
    } else {
      el.setAttribute(key, value);
    }
  }
  for (const child of children) {
    if (child == null) continue;
    if (typeof child === 'string' || typeof child === 'number') {
      el.appendChild(document.createTextNode(String(child)));
    } else {
      el.appendChild(child);
    }
  }
  return el;
}

/**
 * Determine the CSS class for a money cell (positive/negative).
 * @param {number} value
 * @returns {string}
 */
export function moneyClass(value) {
  if (value > 0) return 'money positive';
  if (value < 0) return 'money negative';
  return 'money';
}

/**
 * Determine the badge type from a gap_type string.
 * @param {string} gapType
 * @returns {string}
 */
export function gapTypeBadge(gapType) {
  switch (gapType) {
    case 'missing_item': return 'badge-danger';
    case 'quantity_delta': return 'badge-warning';
    case 'pricing_delta': return 'badge-info';
    default: return 'badge-neutral';
  }
}

/**
 * Human-readable gap type label.
 * @param {string} gapType
 * @returns {string}
 */
export function gapTypeLabel(gapType) {
  switch (gapType) {
    case 'missing_item': return 'Missing';
    case 'quantity_delta': return 'Qty Δ';
    case 'pricing_delta': return 'Price Δ';
    default: return gapType;
  }
}
