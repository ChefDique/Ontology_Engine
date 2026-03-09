/**
 * N4 — Frontend Wiring Tests
 * Tests for auth flow, upload → API wiring, history display, and error states.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { JSDOM } from 'jsdom';
import { setState, getState, setView, setFile, updateNode } from '../src/utils/state.js';

// Set up jsdom globals
const dom = new JSDOM('<!DOCTYPE html><html><body><div id="app"></div></body></html>');
globalThis.document = dom.window.document;
globalThis.window = dom.window;
globalThis.HTMLElement = dom.window.HTMLElement;

// Mock fetch for API tests
globalThis.fetch = vi.fn();

// Mock import.meta.env
if (!globalThis.import) {
  // Vitest handles import.meta.env natively; this is just a safety catch
}

import { renderUploadView } from '../src/components/upload.js';
import { renderPipelineView } from '../src/components/pipeline.js';
import { renderReportView } from '../src/components/report.js';

/** Reset state to defaults */
function resetState() {
  setState({
    activeView: 'upload',
    files: { adjuster: null, contractor: null },
    pipelineNodes: [
      { id: 1, name: 'Ingestion', description: 'Ingest', status: 'idle', progress: 0 },
      { id: 2, name: 'Extraction', description: 'Extract', status: 'idle', progress: 0 },
      { id: 3, name: 'Calculus', description: 'Calc', status: 'idle', progress: 0 },
      { id: 4, name: 'Output', description: 'Out', status: 'idle', progress: 0 },
      { id: 5, name: 'Comparator', description: 'Compare', status: 'idle', progress: 0 },
      { id: 6, name: 'Supplement', description: 'Report', status: 'idle', progress: 0 },
    ],
    supplementReport: null,
    hitlQueue: [],
    pipelineRunning: false,
    pipelineError: null,
    lastAnalysisId: null,
    lastMetadata: null,
    rateLimitRemaining: null,
    historyList: [],
    historyLoading: false,
    historyError: null,
    historyDetail: null,
    historyDetailLoading: false,
  });
}

describe('N4: Frontend Wiring Tests', () => {
  beforeEach(() => {
    resetState();
    vi.clearAllMocks();
  });

  // ── Upload → API wiring ──────────────────────────────────────────────

  describe('Upload view wiring', () => {
    it('disables run button when pipeline is running', () => {
      setState({
        files: {
          adjuster: { name: 'a.pdf', size: 1024, type: 'application/pdf' },
          contractor: { name: 'c.pdf', size: 2048, type: 'application/pdf' },
        },
        pipelineRunning: true,
      });
      const el = renderUploadView();
      const btn = el.querySelector('#btn-run-pipeline');
      expect(btn.hasAttribute('disabled')).toBe(true);
      expect(btn.textContent).toContain('Analyzing');
    });

    it('shows pipeline error banner when pipelineError set', () => {
      setState({ pipelineError: 'Rate limit exceeded' });
      const el = renderUploadView();
      const errBanner = el.querySelector('#pipeline-error');
      expect(errBanner).toBeTruthy();
      expect(errBanner.textContent).toContain('Rate limit exceeded');
    });

    it('hides error banner when no pipelineError', () => {
      const el = renderUploadView();
      const errBanner = el.querySelector('#pipeline-error');
      expect(errBanner).toBeFalsy();
    });

    it('shows rate limit info when available', () => {
      setState({ rateLimitRemaining: 42 });
      const el = renderUploadView();
      const rateInfo = el.querySelector('.rate-limit-info');
      expect(rateInfo).toBeTruthy();
      expect(rateInfo.textContent).toContain('42');
    });

    it('disables clear button when pipeline is running', () => {
      setState({
        files: {
          adjuster: { name: 'a.pdf', size: 1024, type: 'application/pdf' },
          contractor: { name: 'c.pdf', size: 2048, type: 'application/pdf' },
        },
        pipelineRunning: true,
      });
      const el = renderUploadView();
      const clearBtn = el.querySelector('#btn-clear-files');
      expect(clearBtn.hasAttribute('disabled')).toBe(true);
    });
  });

  // ── Pipeline error display ─────────────────────────────────────────

  describe('Pipeline view error handling', () => {
    it('shows error banner when pipeline fails', () => {
      setState({
        pipelineError: 'Server error: 500',
        pipelineRunning: false,
        pipelineNodes: getState().pipelineNodes.map((n) =>
          n.id <= 2 ? { ...n, status: 'failed' } : n
        ),
      });
      const el = renderPipelineView();
      const errBanner = el.querySelector('#pipeline-error');
      expect(errBanner).toBeTruthy();
      expect(errBanner.textContent).toContain('Pipeline Failed');
      expect(errBanner.textContent).toContain('Server error: 500');
    });

    it('does not show error banner during running state', () => {
      setState({
        pipelineError: 'Something went wrong',
        pipelineRunning: true,
      });
      const el = renderPipelineView();
      const errBanner = el.querySelector('#pipeline-error');
      expect(errBanner).toBeFalsy();
    });

    it('shows running indicator with timing note', () => {
      setState({ pipelineRunning: true });
      const el = renderPipelineView();
      const text = el.textContent;
      expect(text).toContain('Pipeline Running');
      expect(text).toContain('30–60 seconds');
    });

    it('shows metadata and analysis ID after completion', () => {
      // Set all nodes completed
      setState({
        pipelineNodes: getState().pipelineNodes.map((n) => ({
          ...n, status: 'completed', progress: 100,
        })),
        lastMetadata: { duration_seconds: 12.5 },
        lastAnalysisId: 'abc12345-test-id',
      });
      const el = renderPipelineView();
      const text = el.textContent;
      expect(text).toContain('12.5');
      expect(text).toContain('abc12345');
    });

    it('renders View Report and Review buttons after completion', () => {
      setState({
        pipelineNodes: getState().pipelineNodes.map((n) => ({
          ...n, status: 'completed', progress: 100,
        })),
      });
      const el = renderPipelineView();
      expect(el.textContent).toContain('View Report');
      expect(el.textContent).toContain('Review Queue');
    });
  });

  // ── State management ─────────────────────────────────────────────────

  describe('State - new fields', () => {
    it('initializes pipelineError as null', () => {
      resetState();
      expect(getState().pipelineError).toBeNull();
    });

    it('stores and retrieves lastAnalysisId', () => {
      setState({ lastAnalysisId: 'test-123' });
      expect(getState().lastAnalysisId).toBe('test-123');
    });

    it('stores history list', () => {
      setState({ historyList: [{ id: '1', created_at: '2025-01-01' }] });
      expect(getState().historyList).toHaveLength(1);
    });

    it('tracks history loading state', () => {
      setState({ historyLoading: true });
      expect(getState().historyLoading).toBe(true);
    });

    it('tracks history error', () => {
      setState({ historyError: 'fetch failed' });
      expect(getState().historyError).toBe('fetch failed');
    });

    it('tracks rate limit remaining', () => {
      setState({ rateLimitRemaining: 48 });
      expect(getState().rateLimitRemaining).toBe(48);
    });
  });

  // ── Report view with real data shapes ──────────────────────────────

  describe('Report view with API-shaped data', () => {
    it('renders report from API gap_report shape', () => {
      // This mirrors the shape that upload.js maps from API response
      setState({
        supplementReport: {
          summary: {
            adjuster_rcv: 18245.67,
            contractor_rcv: 24890.12,
            total_delta: 6644.45,
            gap_count: 3,
            adjuster_line_count: 23,
            contractor_line_count: 31,
          },
          line_item_gaps: [
            {
              gap_type: 'missing_item',
              category: 'Roofing',
              description: 'Ice & water shield',
              contractor_total: 1245.00,
              adjuster_total: null,
              trade: 'Roofing',
            },
            {
              gap_type: 'quantity_delta',
              category: 'Roofing',
              description: 'Architectural shingles',
              contractor_qty: 28,
              adjuster_qty: 24,
              quantity_delta: 4,
              contractor_total: 3920.00,
              adjuster_total: 3360.00,
              pricing_delta: 560.00,
              trade: 'Roofing',
            },
          ],
          op_analysis: {
            trade_count: 3,
            op_warranted: true,
            adjuster_op_applied: { overhead: 1800, profit: 1800 },
            contractor_op_applied: { overhead: 2400, profit: 2400 },
            op_recovery_amount: 1200,
            trades_detected: ['Roofing', 'Gutters', 'Drywall'],
          },
          depreciation_findings: [
            {
              category: 'Roofing',
              description: 'Shingles',
              depreciation_pct: 0.45,
              flagged: true,
              flag_reason: 'Exceeds threshold',
              recoverable_amount: 1764.00,
            },
          ],
        },
      });

      const el = renderReportView();
      
      // Verify gap table renders
      const table = el.querySelector('#gap-table');
      expect(table).toBeTruthy();
      const rows = table.querySelectorAll('tbody tr');
      expect(rows.length).toBe(2);

      // Verify summary stats render
      const statCards = el.querySelectorAll('.stat-card');
      expect(statCards.length).toBeGreaterThan(0);

      // Verify O&P section renders
      expect(el.textContent).toContain('Overhead & Profit');
      
      // Verify depreciation renders
      expect(el.textContent).toContain('Depreciation');
    });
  });
});
