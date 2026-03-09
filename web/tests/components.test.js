/**
 * Tests — Component Rendering (DOM integration)
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { JSDOM } from 'jsdom';
import { setState, getState } from '../src/utils/state.js';

// Set up jsdom globals
const dom = new JSDOM('<!DOCTYPE html><html><body><div id="app"></div></body></html>');
globalThis.document = dom.window.document;
globalThis.window = dom.window;
globalThis.HTMLElement = dom.window.HTMLElement;

import { renderUploadView } from '../src/components/upload.js';
import { renderPipelineView } from '../src/components/pipeline.js';
import { renderReportView } from '../src/components/report.js';
import { renderReviewView } from '../src/components/review.js';

describe('Component Rendering', () => {
  beforeEach(() => {
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
  });

  describe('Upload View', () => {
    it('renders two upload zones', () => {
      const el = renderUploadView();
      const zones = el.querySelectorAll('.upload-zone');
      expect(zones.length).toBe(2);
    });

    it('renders run button disabled when no files', () => {
      const el = renderUploadView();
      const btn = el.querySelector('#btn-run-pipeline');
      expect(btn).toBeTruthy();
      expect(btn.hasAttribute('disabled')).toBe(true);
    });

    it('renders run button enabled when both files present', () => {
      setState({
        files: {
          adjuster: { name: 'a.pdf', size: 1024, type: 'application/pdf' },
          contractor: { name: 'c.pdf', size: 2048, type: 'application/pdf' },
        },
      });
      const el = renderUploadView();
      const btn = el.querySelector('#btn-run-pipeline');
      expect(btn.hasAttribute('disabled')).toBe(false);
    });
  });

  describe('Pipeline View', () => {
    it('renders 6 pipeline node cards', () => {
      const el = renderPipelineView();
      const nodes = el.querySelectorAll('.pipeline-node');
      expect(nodes.length).toBe(6);
    });

    it('shows connectors between nodes', () => {
      const el = renderPipelineView();
      const connectors = el.querySelectorAll('.pipeline-connector');
      expect(connectors.length).toBe(5); // 6 nodes - 1
    });

    it('marks completed nodes correctly', () => {
      setState({
        pipelineNodes: getState().pipelineNodes.map((n) =>
          n.id <= 3 ? { ...n, status: 'completed', progress: 100 } : n
        ),
      });
      const el = renderPipelineView();
      const completed = el.querySelectorAll('.pipeline-node.completed');
      expect(completed.length).toBe(3);
    });
  });

  describe('Report View', () => {
    it('shows empty state when no report', () => {
      const el = renderReportView();
      const empty = el.querySelector('.empty-state');
      expect(empty).toBeTruthy();
    });

    it('renders gap table when report data present', () => {
      setState({
        supplementReport: {
          summary: { adjuster_rcv: 1000, contractor_rcv: 1500, total_delta: 500, gap_count: 2, adjuster_line_count: 10, contractor_line_count: 12 },
          line_item_gaps: [
            { gap_type: 'missing_item', category: 'Roofing', description: 'Test item', contractor_total: 500, adjuster_total: null, trade: 'Roofing' },
          ],
          op_analysis: {
            trade_count: 3, op_warranted: true,
            adjuster_op_applied: { overhead: 100, profit: 100 },
            contractor_op_applied: { overhead: 150, profit: 150 },
            op_recovery_amount: 100,
            trades_detected: ['Roofing', 'Gutters', 'Drywall'],
          },
          depreciation_findings: [],
        },
      });
      const el = renderReportView();
      const table = el.querySelector('#gap-table');
      expect(table).toBeTruthy();
      const rows = table.querySelectorAll('tbody tr');
      expect(rows.length).toBe(1);
    });
  });

  describe('Review View', () => {
    it('shows empty queue message when no items', () => {
      const el = renderReviewView();
      const empty = el.querySelector('.hitl-empty');
      expect(empty).toBeTruthy();
    });

    it('renders HITL items with approve/reject buttons', () => {
      setState({
        hitlQueue: [
          { type: 'f9_override', title: 'Test Flag', description: 'Desc', severity: 'warning', nodeId: 2, lineItem: 'Item' },
        ],
      });
      const el = renderReviewView();
      const items = el.querySelectorAll('.hitl-item');
      expect(items.length).toBe(1);

      const approveBtn = el.querySelector('#hitl-approve-0');
      const rejectBtn = el.querySelector('#hitl-reject-0');
      expect(approveBtn).toBeTruthy();
      expect(rejectBtn).toBeTruthy();
    });
  });
});
