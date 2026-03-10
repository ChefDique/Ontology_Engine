# Agent Q — Feedback Widget (Paste + Voice)

## Verify Results

- `cd web && npm run build` — PASS (51 modules, 311ms)
- `cd web && npm test` — PASS (81 tests, 6 files, 0 failures)
- Contract validation — N/A (frontend-only component)
- Scope boundary respected — YES (3 new files, all in scope)

## Shared File Requests

### Q1: Create Supabase `feedback` table (migration)

The feedback component expects a `feedback` table in Supabase with these columns:

```sql
CREATE TABLE feedback (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) DEFAULT auth.uid(),
  text TEXT NOT NULL,
  category TEXT NOT NULL CHECK (category IN ('bug','suggestion','question','other')),
  screenshots TEXT[] DEFAULT '{}',
  analysis_id UUID,
  view_context TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can insert own feedback" ON feedback FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can view own feedback" ON feedback FOR SELECT USING (auth.uid() = user_id);
```

Also needs a `feedback-screenshots` storage bucket (public or with appropriate policies).

### Q5: Wire feedback into main.js, report.js, review.js

These files are outside scope. The component exports:

- `createFeedbackButton()` → returns a floating FAB, add to `renderApp()` in `main.js`
- `createFeedbackLink('report')` → inline button, add to bottom of `renderReportView()` in `report.js`
- `createFeedbackLink('review')` → inline button, add to bottom of `renderReviewView()` in `review.js`
- `import '../components/feedback.css'` → add to `main.js`

## Changes

```
 web/src/components/feedback.css | 303 +++++++++
 web/src/components/feedback.js  | 465 ++++++++++++++
 web/tests/feedback.test.js      | 191 ++++++
 3 files changed, 959 insertions(+)
```

## Notes

- The feedback widget is fully self-contained and exports clean entry points for integration
- Web Speech API availability is detected at runtime; mic button only appears when supported
- Screenshot paste supports up to 5 images via Ctrl+V into the textarea
- All Supabase calls gracefully degrade if not configured (returns error, doesn't crash)
