# Gemini Deep Research Knowledge Base

## A) SOURCE MANIFEST

- **Seed URL:** `https://ai.google.dev/gemini-api/docs/deep-research`
- **Required followed URLs:**
  - `https://ai.google.dev/gemini-api/docs/interactions` — required because Deep Research is **Interactions API only** and uses the Interactions request/response lifecycle. 
  - `https://ai.google.dev/gemini-api/docs/models/deep-research-pro-preview-12-2025` — required for the agent code, supported input/output types, and token limits.
- **Coverage statement:** This package covers the Deep Research overview, execution model, async/background requirement, start-and-poll flow, report-follow-up flow via `previous_interaction_id`, fit/use cases, pricing/cost-shape guidance, supported tools/data, beta limitations, maximum runtime, Interactions API constraints, and the Deep Research model card.

## B) KNOWLEDGE PACK — JSON

```json
{
  "kb_id": "gemini_deep_research__ai_google_dev__v1",
  "source_domain": "ai.google.dev",
  "seed_url": "https://ai.google.dev/gemini-api/docs/deep-research",
  "generated_at": "2026-03-06T06:00:00Z",
  "chunks": [
    {
      "chunk_id": "DR__001",
      "title": "What Gemini Deep Research is",
      "category": "overview",
      "summary": "Gemini Deep Research Agent autonomously plans, searches, reads, and synthesizes multi-step research into cited reports. It is powered by Gemini 3.1 Pro and is meant for long-running analyst-style tasks rather than low-latency chat.",
      "tags": ["overview", "agent", "research"],
      "key_terms": ["Gemini Deep Research Agent", "multi-step research", "cited reports", "Gemini 3.1 Pro"],
      "content": "The Deep Research Agent autonomously plans, executes, and synthesizes multi-step research tasks. It navigates web sources and user data to produce detailed, cited reports. It is positioned as an 'analyst-in-a-box' rather than a chatbot.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/deep-research", "section": "Overview"}
      ]
    },
    {
      "chunk_id": "DR__002",
      "title": "Access path and execution requirement",
      "category": "endpoint",
      "summary": "Deep Research is only available through the Interactions API and cannot be called through generate_content. It must run asynchronously with background=true and be polled for completion.",
      "tags": ["interactions", "background", "async"],
      "key_terms": ["Interactions API", "background", "background=true", "generate_content"],
      "content": "Deep Research is exclusively available through the Interactions API. Requests must set background=true because research takes minutes and is not a synchronous generate_content workflow.",
      "code_blocks": [
        {
          "language": "python",
          "code": "interaction = client.interactions.create(\n    input='Research the history of Google TPUs.',\n    agent='deep-research-pro-preview-12-2025',\n    background=True\n)"
        }
      ],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/deep-research", "section": "Start a research task"},
        {"url": "https://ai.google.dev/gemini-api/docs/interactions", "section": "Interactions API overview"}
      ]
    },
    {
      "chunk_id": "DR__003",
      "title": "Polling lifecycle",
      "category": "workflows",
      "summary": "After creating a Deep Research interaction, clients poll interactions.get until status becomes completed or failed. On completion, the final report text is available in the last output item.",
      "tags": ["polling", "status", "workflow"],
      "key_terms": ["client.interactions.get", "status", "completed", "failed", "outputs[-1].text"],
      "content": "The standard lifecycle is create → poll → read final output. Clients repeatedly fetch the interaction by ID until status is completed or failed, then read the final report from the last output entry.",
      "code_blocks": [
        {
          "language": "javascript",
          "code": "const interaction = await client.interactions.create({\n  input: 'Research the history of Google TPUs.',\n  agent: 'deep-research-pro-preview-12-2025',\n  background: true\n});\nwhile (true) {\n  const result = await client.interactions.get(interaction.id);\n  if (result.status === 'completed') {\n    console.log(result.outputs[result.outputs.length - 1].text);\n    break;\n  }\n  if (result.status === 'failed') {\n    console.log(result.error);\n    break;\n  }\n}"
        }
      ],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/deep-research", "section": "Start a research task"}
      ]
    },
    {
      "chunk_id": "DR__004",
      "title": "Follow-up on completed reports",
      "category": "workflows",
      "summary": "After a Deep Research report completes, follow-up questions are asked with a normal model call using previous_interaction_id, not by rerunning the agent. This supports elaboration on prior report content.",
      "tags": ["follow-up", "previous_interaction_id"],
      "key_terms": ["previous_interaction_id", "model", "gemini-3.1-pro-preview"],
      "content": "To continue the conversation after a report is finished, create a new interaction with a standard model such as gemini-3.1-pro-preview and set previous_interaction_id to the completed Deep Research interaction ID.",
      "code_blocks": [
        {
          "language": "python",
          "code": "interaction = client.interactions.create(\n    input='Can you elaborate on the second point in the report?',\n    model='gemini-3.1-pro-preview',\n    previous_interaction_id='COMPLETED_INTERACTION_ID'\n)"
        }
      ],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/deep-research", "section": "Follow-up questions"}
      ]
    },
    {
      "chunk_id": "DR__005",
      "title": "When to use Deep Research",
      "category": "overview",
      "summary": "Deep Research is better for market analysis, due diligence, literature reviews, and competitive landscaping. Standard Gemini models remain better for low-latency chat, extraction, and creative tasks.",
      "tags": ["use-cases", "fit"],
      "key_terms": ["market analysis", "due diligence", "literature reviews", "competitive landscaping"],
      "content": "The docs contrast standard Gemini models and Deep Research. Standard models are optimized for seconds-scale generation, while Deep Research is optimized for minutes-scale planning, search, reading, iteration, and detailed reports.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/deep-research", "section": "When to use Gemini Deep Research Agent"}
      ]
    },
    {
      "chunk_id": "DR__006",
      "title": "Cost shape and estimated task ranges",
      "category": "limits",
      "summary": "Costs depend on search volume and token consumption. The docs estimate roughly $2–$3 for a standard task and $3–$5 for a more complex task, with substantial search and token usage.",
      "tags": ["pricing", "costs"],
      "key_terms": ["80 search queries", "160 search queries", "250k input tokens", "900k input tokens"],
      "content": "The documentation frames Deep Research pricing as an agentic loop rather than a single request-response. Example estimates include ~80 searches / ~250k input tokens / ~60k output tokens for a standard task and up to ~160 searches / ~900k input tokens / ~80k output tokens for a complex task.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/deep-research", "section": "Estimated costs"}
      ]
    },
    {
      "chunk_id": "DR__007",
      "title": "Deep Research prompting guidance",
      "category": "parameters",
      "summary": "Prompt quality matters. The docs recommend specifying the exact task, defining the desired structure and evaluation criteria, explicitly telling the agent how to handle unknowns, and providing grounding context.",
      "tags": ["prompting", "instructions"],
      "key_terms": ["Prompt for unknowns", "Provide context", "desired structure", "evaluation criteria"],
      "content": "Prompts should clearly define the research objective, constraints, and deliverable structure. The docs specifically recommend telling the agent how to treat unavailable figures or projections, and providing contextual constraints directly in the input prompt.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/deep-research", "section": "Prompting best practices"}
      ]
    },
    {
      "chunk_id": "DR__008",
      "title": "Supported inputs and outputs",
      "category": "formats",
      "summary": "The Deep Research preview agent accepts Text, Image, PDF, Audio, and Video as inputs and outputs Text cited reports.",
      "tags": ["inputs", "outputs", "model-card"],
      "key_terms": ["Text", "Image", "PDF", "Audio", "Video", "Text (Cited Reports)"],
      "content": "According to the model card, deep-research-pro-preview-12-2025 supports multimodal inputs across text, image, PDF, audio, and video, while its output is text in the form of cited reports.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/models/deep-research-pro-preview-12-2025", "section": "Supported data types"}
      ]
    },
    {
      "chunk_id": "DR__009",
      "title": "Agent code and token limits",
      "category": "models",
      "summary": "The Deep Research preview agent code is deep-research-pro-preview-12-2025. Its model card lists a 1,048,576 input context window and a 65,536 output token limit.",
      "tags": ["agent-code", "token-limits"],
      "key_terms": ["deep-research-pro-preview-12-2025", "1,048,576", "65,536"],
      "content": "The current preview agent is identified by deep-research-pro-preview-12-2025. The model card reports a 1,048,576-token input context window and a 65,536-token output limit.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/models/deep-research-pro-preview-12-2025", "section": "Model card"}
      ]
    },
    {
      "chunk_id": "DR__010",
      "title": "Tooling and product limitations",
      "category": "constraints",
      "summary": "The docs state that custom function-calling tools and remote MCP servers are not currently supported, and Deep Research does not currently support human-approved planning or structured outputs.",
      "tags": ["limitations", "tools", "structured-output"],
      "key_terms": ["custom Function Calling tools", "remote MCP", "structured outputs", "plan approval"],
      "content": "Deep Research currently cannot be extended with custom function-calling tools or remote MCP servers. It also lacks human-approved planning and structured output support at this time.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/deep-research", "section": "Limitations"}
      ]
    },
    {
      "chunk_id": "DR__011",
      "title": "Maximum runtime and practical completion time",
      "category": "limits",
      "summary": "The maximum Deep Research runtime is 60 minutes, though the docs say most tasks should finish within 20 minutes.",
      "tags": ["runtime", "time-limits"],
      "key_terms": ["60 minutes", "20 minutes"],
      "content": "Deep Research has a hard maximum research time of 60 minutes. The docs also indicate that most tasks should complete within 20 minutes, making it suitable for substantial but bounded investigations.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/deep-research", "section": "Limitations"}
      ]
    },
    {
      "chunk_id": "DR__012",
      "title": "Interactions API beta caveats relevant to Deep Research",
      "category": "constraints",
      "summary": "Because Deep Research runs on the Interactions API, it inherits beta-stage caveats: schemas and behavior may change, and there are known output-ordering issues for some built-in tools.",
      "tags": ["beta", "breaking-changes", "interactions"],
      "key_terms": ["Beta", "breaking changes", "output ordering"],
      "content": "The Interactions API is in beta/preview, and Google explicitly warns that schemas, SDK signatures, and behavior can change. It also notes a known content-ordering issue for some built-in tools, which matters when designing robust client logic around agent outputs.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/interactions", "section": "Limitations"},
        {"url": "https://ai.google.dev/gemini-api/docs/interactions", "section": "Breaking changes"}
      ]
    }
  ],
  "index": {
    "by_category": {
      "overview": ["DR__001", "DR__005"],
      "endpoint": ["DR__002"],
      "workflows": ["DR__003", "DR__004"],
      "limits": ["DR__006", "DR__011"],
      "parameters": ["DR__007"],
      "formats": ["DR__008"],
      "models": ["DR__009"],
      "constraints": ["DR__010", "DR__012"]
    },
    "by_tag": {
      "overview": ["DR__001"],
      "agent": ["DR__001"],
      "research": ["DR__001"],
      "interactions": ["DR__002", "DR__012"],
      "background": ["DR__002"],
      "async": ["DR__002"],
      "polling": ["DR__003"],
      "status": ["DR__003"],
      "workflow": ["DR__003"],
      "follow-up": ["DR__004"],
      "use-cases": ["DR__005"],
      "fit": ["DR__005"],
      "pricing": ["DR__006"],
      "costs": ["DR__006"],
      "prompting": ["DR__007"],
      "instructions": ["DR__007"],
      "inputs": ["DR__008"],
      "outputs": ["DR__008"],
      "model-card": ["DR__008"],
      "agent-code": ["DR__009"],
      "token-limits": ["DR__009"],
      "limitations": ["DR__010"],
      "tools": ["DR__010"],
      "structured-output": ["DR__010"],
      "runtime": ["DR__011"],
      "time-limits": ["DR__011"],
      "beta": ["DR__012"],
      "breaking-changes": ["DR__012"]
    },
    "by_key_term": {
      "Gemini Deep Research Agent": ["DR__001"],
      "Gemini 3.1 Pro": ["DR__001"],
      "Interactions API": ["DR__002", "DR__012"],
      "background": ["DR__002"],
      "background=true": ["DR__002"],
      "generate_content": ["DR__002"],
      "client.interactions.get": ["DR__003"],
      "completed": ["DR__003"],
      "failed": ["DR__003"],
      "outputs[-1].text": ["DR__003"],
      "previous_interaction_id": ["DR__004"],
      "gemini-3.1-pro-preview": ["DR__004"],
      "market analysis": ["DR__005"],
      "due diligence": ["DR__005"],
      "literature reviews": ["DR__005"],
      "competitive landscaping": ["DR__005"],
      "80 search queries": ["DR__006"],
      "160 search queries": ["DR__006"],
      "250k input tokens": ["DR__006"],
      "900k input tokens": ["DR__006"],
      "Prompt for unknowns": ["DR__007"],
      "Provide context": ["DR__007"],
      "Text": ["DR__008"],
      "Image": ["DR__008"],
      "PDF": ["DR__008"],
      "Audio": ["DR__008"],
      "Video": ["DR__008"],
      "Text (Cited Reports)": ["DR__008"],
      "deep-research-pro-preview-12-2025": ["DR__002", "DR__009"],
      "1,048,576": ["DR__009"],
      "65,536": ["DR__009"],
      "custom Function Calling tools": ["DR__010"],
      "remote MCP": ["DR__010"],
      "structured outputs": ["DR__010"],
      "plan approval": ["DR__010"],
      "60 minutes": ["DR__011"],
      "20 minutes": ["DR__011"],
      "Beta": ["DR__012"],
      "breaking changes": ["DR__012"],
      "output ordering": ["DR__012"]
    }
  }
}
```

## C) METADATA CATEGORIZATION BLUEPRINT (IA)

### Final category list + definition

- **overview** — what the Deep Research agent is and when it fits.
- **endpoint** — where and how it is invoked.
- **workflows** — operational sequences like create → poll and follow-up.
- **limits** — runtime and cost-shape guidance.
- **parameters** — prompt and input-shaping guidance.
- **formats** — input/output modality support.
- **models** — agent code and token limits.
- **constraints** — non-negotiable platform limitations and beta caveats.

### Tagging rules (IA DECISION)

- Tag every chunk with the smallest stable nouns a developer would naturally search for.
- Prefer implementation terms over abstract themes.
- Reuse the same tag for the same concept across chunks; do not create synonyms without a strong retrieval reason.

### Key_term rules (IA DECISION)

- Always include exact API identifiers, field names, enum-like values, model/agent codes, and numeric limits.
- Include user-query phrases only when they map directly to documented terminology.
- Do not include invented abstractions or paraphrased identifiers.

### Chunk sizing rules (IA DECISION)

- One chunk = one micro-step or one bounded concept.
- Split whenever a chunk would otherwise mix invocation, limits, and follow-up behavior.
- Keep summaries short enough to be retrieved in one pass, but detailed enough to execute the step without opening the source doc.

### Retrieval patterns for a Gem/GPT

- For **how do I call it?** → search `by_key_term` for `Interactions API`, `background=true`, `deep-research-pro-preview-12-2025`.
- For **how do I continue after report generation?** → search `previous_interaction_id`.
- For **what can it take in / output?** → search `Text`, `Image`, `PDF`, `Audio`, `Video`, `Text (Cited Reports)`.
- For **fit / whether to use it** → search tags `use-cases`, `fit`.
- For **operational risk** → search tags `limitations`, `beta`, `breaking-changes`, `runtime`.

## D) DOWNSTREAM ASSISTANT SPEC — “Deep Research Task Refiner + Runner”

### 1) INPUT INTAKE

Ask only when missing information would block request assembly or would produce the wrong report.

Capture:
- research question / objective
- scope boundaries
- preferred output shape
- handling of unknowns / unavailable data
- whether follow-up analysis should build on a prior completed interaction

### 2) PROMPT REFINEMENT (DOC-ANCHORED)

Transform `original_prompt` into `refined_prompt` by:
1. making the research objective explicit
2. adding scope constraints
3. specifying the desired report structure
4. instructing how to treat missing data or unavailable figures
5. adding domain context the agent should treat as grounding

Heuristics beyond the docs should stay conservative. Do not invent workflow capabilities like plan approval or structured outputs because the docs explicitly say those are not supported.

### 3) REQUEST ASSEMBLY (DOC-ANCHORED)

For a new Deep Research run, assemble:

```json
{
  "input": "<refined_prompt>",
  "agent": "deep-research-pro-preview-12-2025",
  "background": true
}
```

For a follow-up on a completed report, assemble:

```json
{
  "input": "<follow_up_prompt>",
  "model": "gemini-3.1-pro-preview",
  "previous_interaction_id": "<COMPLETED_INTERACTION_ID>"
}
```

If a field is not documented for the target workflow, mark it `NOT FOUND IN SOURCE` rather than inventing it.

### 4) RESPONSE HANDLING (DOC-ANCHORED)

- poll `interactions.get(id)` until status is `completed` or `failed`
- on success, extract final text from the last output item
- on failure, surface `interaction.error`
- do not assume synchronous completion
- do not assume structured JSON output support

### 5) OUTPUT FORMAT

Return:
- `original_prompt`
- `refined_prompt`
- `generation_request` (structured interaction request)
- `generation_response_handling` (polling + extraction instructions)
- `final_report` (completed cited text report, when available)

## E) STOP CONDITIONS

Stop when: all seed sections are chunked; all required linked pages are included; KB JSON is complete + indexed; downstream assistant spec is complete.
