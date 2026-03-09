/**
 * Tests — Application State Store
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { getState, setState, subscribe, setView, setFile, updateNode, setReport, setHitlQueue, resolveHitlItem } from '../src/utils/state.js';

describe('State Store', () => {
  beforeEach(() => {
    // Reset to defaults
    setState({
      activeView: 'upload',
      files: { adjuster: null, contractor: null },
      pipelineNodes: [
        { id: 1, name: 'Ingestion', description: 'PDF parse', status: 'idle', progress: 0 },
        { id: 2, name: 'Extraction', description: 'LLM', status: 'idle', progress: 0 },
        { id: 3, name: 'Calculus', description: 'Math', status: 'idle', progress: 0 },
        { id: 4, name: 'Output', description: 'CSV/JSON', status: 'idle', progress: 0 },
        { id: 5, name: 'Comparator', description: 'Diff', status: 'idle', progress: 0 },
        { id: 6, name: 'Supplement', description: 'Report', status: 'idle', progress: 0 },
      ],
      supplementReport: null,
      hitlQueue: [],
      pipelineRunning: false,
    });
  });

  it('returns initial state', () => {
    const state = getState();
    expect(state.activeView).toBe('upload');
    expect(state.files.adjuster).toBeNull();
    expect(state.files.contractor).toBeNull();
    expect(state.pipelineNodes).toHaveLength(6);
  });

  it('updates state via setState', () => {
    setState({ activeView: 'pipeline' });
    expect(getState().activeView).toBe('pipeline');
  });

  it('notifies subscribers on state change', () => {
    let called = false;
    const unsub = subscribe(() => { called = true; });
    setState({ activeView: 'report' });
    expect(called).toBe(true);
    unsub();
  });

  it('unsubscribes correctly', () => {
    let count = 0;
    const unsub = subscribe(() => { count++; });
    setState({ activeView: 'report' });
    expect(count).toBe(1);
    unsub();
    setState({ activeView: 'upload' });
    expect(count).toBe(1); // not called again
  });

  it('setView updates activeView', () => {
    setView('review');
    expect(getState().activeView).toBe('review');
  });

  it('setFile updates a specific file slot', () => {
    const fakeFile = { name: 'test.pdf', size: 1024 };
    setFile('adjuster', fakeFile);
    expect(getState().files.adjuster).toBe(fakeFile);
    expect(getState().files.contractor).toBeNull();
  });

  it('updateNode patches a specific node', () => {
    updateNode(3, { status: 'running', progress: 50 });
    const node3 = getState().pipelineNodes.find((n) => n.id === 3);
    expect(node3.status).toBe('running');
    expect(node3.progress).toBe(50);

    // Other nodes unchanged
    const node1 = getState().pipelineNodes.find((n) => n.id === 1);
    expect(node1.status).toBe('idle');
  });

  it('setReport stores the report', () => {
    const report = { summary: { total_delta: 1234 } };
    setReport(report);
    expect(getState().supplementReport).toEqual(report);
  });

  it('setHitlQueue replaces the queue', () => {
    setHitlQueue([{ title: 'Item 1' }, { title: 'Item 2' }]);
    expect(getState().hitlQueue).toHaveLength(2);
  });

  it('resolveHitlItem removes an item by index', () => {
    setHitlQueue([{ title: 'A' }, { title: 'B' }, { title: 'C' }]);
    resolveHitlItem(1);
    const queue = getState().hitlQueue;
    expect(queue).toHaveLength(2);
    expect(queue[0].title).toBe('A');
    expect(queue[1].title).toBe('C');
  });
});
