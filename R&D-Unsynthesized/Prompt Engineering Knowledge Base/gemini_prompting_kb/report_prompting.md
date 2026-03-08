# Gemini Prompting and Model Capability Expert Knowledge Base

## A) Source Manifest

**Seed URLs**

- `https://ai.google.dev/gemini-api/docs/prompting-strategies` – this page contains the primary guidance for designing prompts when working with Gemini models.  It includes best‑practice instructions, examples of zero‑shot and few‑shot prompts, information on input types, response formatting, constraints, prefixing, prompt decomposition, tuning model parameters, iteration strategies, core principles for Gemini 3 and Flash models, guidelines for reasoning and planning, and agentic workflow templates.
- `https://ai.google.dev/gemini-api/docs/` – the documentation root page provides navigation to model listings, the Interactions API, structured outputs, thinking models and other pages required to understand Gemini model capabilities and request/response formats.  Following this URL leads to individual pages as needed.

**Followed URLs (ai.google.dev only)**

| URL | Title | Why required |
| --- | --- | --- |
| `https://ai.google.dev/gemini-api/docs/models` | **Models** | Lists Gemini model families and provides high‑level descriptions of Gemini 3, Gemini 2.5, Nano Banana, Veo and other models.  Needed to understand available model capabilities and naming patterns【106980676632281†L188-L200】. |
| `https://ai.google.dev/gemini-api/docs/interactions` | **Interactions API** | Describes the unified API used to interact with Gemini models.  Provides examples of requests, conversation state management, supported parameters and features like tool use, streaming and multimodal capabilities【107660960480700†L248-L299】. |
| `https://ai.google.dev/gemini-api/docs/structured-output` | **Structured outputs** | Explains how to enforce JSON‑schema‑based outputs from Gemini models for predictable data extraction.  Includes examples of defining schemas and using Pydantic/Zod in SDKs【287061243240597†L181-L195】. |
| `https://ai.google.dev/gemini-api/docs/thinking` | **Gemini thinking** | Introduces models with “thinking” support and shows how to enable them in requests.  Needed to describe thinking configuration and its impact on prompting【584876917905493†L181-L196】. |

**Coverage statement**

All relevant sections of the primary target pages were read and converted into atomic chunks.  Essential on‑domain pages (models, interactions, structured outputs, thinking) were incorporated to capture model listings, request parameters, response formats and advanced features.  No off‑domain content was used.

## B) Knowledge Pack — JSON

The following JSON object contains the extracted knowledge base.  Each `chunk` is atomic, focusing on a single concept.  Categories, tags, models, capabilities, task types and key terms enable deterministic retrieval.

```
{
  "kb_id": "gemini_prompting_and_capabilities__ai_google_dev__v1",
  "source_domain": "ai.google.dev",
  "primary_targets": [
    "https://ai.google.dev/gemini-api/docs/prompting-strategies",
    "https://ai.google.dev/gemini-api/docs/"
  ],
  "generated_at": "2026-03-06T00:00:00Z",
  "chunks": [
    {
      "chunk_id": "GEMDOC__001",
      "title": "Prompting basics: clear instructions and input types",
      "category": "prompting",
      "summary": "Effective prompts use clear, specific instructions and include input data (question, task, entity or partial input) that the model should respond to.  Clarity reduces ambiguity and improves output quality【741394908941637†screenshot】.",
      "tags": ["clarity","input_types"],
      "models": ["Gemini 3","Gemini 2.5","Nano Banana","Veo"],
      "capabilities": ["text","multimodal"],
      "task_types": ["prompt_refinement","generation","analysis","extraction","classification","structured_output","multimodal"],
      "key_terms": ["question","task","entity","partial input"],
      "content": "Prompting begins with clear and specific instructions.  Inputs can be questions (\"What is the largest planet?\"), tasks (\"Translate to French\"), entities (identifiers like an order or movie title) or partial inputs for the model to complete【741394908941637†screenshot】【1477286111502†screenshot】.  Explicitly describe what you want the model to do and include all required input information.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Clear and specific instructions"},
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Input"}
      ]
    },
    {
      "chunk_id": "GEMDOC__002",
      "title": "Partial input completion and examples",
      "category": "prompting",
      "summary": "Provide example inputs and desired outputs to guide the model when completing partial information; use a prefix to illustrate desired format【35510177626619†screenshot】.",
      "tags": ["partial_input","few_shot","examples"],
      "models": ["Gemini 3","Gemini 2.5"],
      "capabilities": ["text"],
      "task_types": ["structured_output","classification","extraction","generation"],
      "key_terms": ["prefix","example","output"],
      "content": "For tasks requiring structured responses, include a few-shot example and a response prefix to demonstrate the desired output.  In a menu‑ordering example, defining valid fields and showing the JSON output for a sample order enables the model to correctly generate a JSON object for new orders【35510177626619†screenshot】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Partial input completion"}
      ]
    },
    {
      "chunk_id": "GEMDOC__003",
      "title": "Constraints and response formatting",
      "category": "prompting",
      "summary": "Specify constraints (e.g., word limits or style) and desired response formats (table, bullet list, elevator pitch, JSON) to control the model’s output【489604398123491†screenshot】.",
      "tags": ["constraints","response_format"],
      "models": ["Gemini 3","Gemini 2.5"],
      "capabilities": ["text","structured_output"],
      "task_types": ["prompt_refinement","generation","structured_output","classification","extraction"],
      "key_terms": ["constraints","one sentence","table","bullet list","JSON"],
      "content": "Prompt instructions can include constraints (e.g., \"Summarize this text in one sentence\") and explicit response formats such as tables or bullet lists.  Defining the format ensures the model structures its output accordingly【489604398123491†screenshot】【745343839790870†screenshot】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Constraints"},
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Response format"}
      ]
    },
    {
      "chunk_id": "GEMDOC__004",
      "title": "Zero‑shot versus few‑shot prompting",
      "category": "prompting",
      "summary": "Few‑shot prompts contain examples of the desired input–output mapping, which can improve the model’s performance and control verbosity; zero‑shot prompts rely solely on instructions【418636950536661†screenshot】.",
      "tags": ["zero_shot","few_shot","examples"],
      "models": ["Gemini 3","Gemini 2.5"],
      "capabilities": ["text"],
      "task_types": ["prompt_refinement","generation","classification","analysis"],
      "key_terms": ["zero shot","few shot","example"],
      "content": "In zero‑shot prompts, the model follows instructions without examples.  Including few‑shot examples (input–output pairs) demonstrates the desired behavior, such as selecting a concise explanation for a question.  Examples should be consistent in format and show the pattern you want the model to follow【418636950536661†screenshot】【697729196025136†screenshot】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Zero-shot vs few-shot prompts"}
      ]
    },
    {
      "chunk_id": "GEMDOC__005",
      "title": "Optimal number of examples and pattern design",
      "category": "prompting",
      "summary": "Use a few carefully chosen examples to guide the model; too many examples may cause overfitting or exceed context limits.  Show patterns rather than anti‑patterns and ensure examples have consistent structure【39101403647812†screenshot】【307780271357223†screenshot】.",
      "tags": ["examples","patterns","consistency"],
      "models": ["Gemini 3"],
      "capabilities": ["text"],
      "task_types": ["prompt_refinement","generation","classification","analysis"],
      "key_terms": ["few shot","patterns","anti pattern"],
      "content": "When using few‑shot prompting, include only as many examples as necessary to demonstrate the desired behavior.  Avoid showing anti‑patterns; instead, illustrate the correct pattern.  Ensure formatting (such as XML tags, whitespace and punctuation) is consistent across examples to prevent unintended variations in the output【39101403647812†screenshot】【307780271357223†screenshot】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Optimal number of examples"},
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Patterns vs anti patterns"}
      ]
    },
    {
      "chunk_id": "GEMDOC__006",
      "title": "Adding context information",
      "category": "prompting",
      "summary": "Provide relevant context (e.g., domain knowledge or troubleshooting steps) in the prompt to help the model produce accurate, specific responses【596073122220472†screenshot】.",
      "tags": ["context","domain knowledge"],
      "models": ["Gemini 3","Gemini 2.5"],
      "capabilities": ["text","multimodal"],
      "task_types": ["analysis","classification","extraction","generation"],
      "key_terms": ["context","router","LED"],
      "content": "The model relies on the context you provide.  Including domain‑specific information, such as a router’s LED troubleshooting guide, allows the model to tailor its response correctly.  Without sufficient context, answers tend to be generic【596073122220472†screenshot】【802153086291159†screenshot】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Add context"}
      ]
    },
    {
      "chunk_id": "GEMDOC__007",
      "title": "Prefixes for structured prompts",
      "category": "prompting",
      "summary": "Use prefixes to distinguish between inputs, outputs and examples in a prompt.  Prefixes like \"English:\", \"French:\" or \"JSON:\" help the model know where to read and where to write【229385501113536†screenshot】.",
      "tags": ["prefixes","formatting"],
      "models": ["Gemini 3","Gemini 2.5"],
      "capabilities": ["text","structured_output"],
      "task_types": ["prompt_refinement","translation","structured_output"],
      "key_terms": ["prefix","English","French","JSON"],
      "content": "In multi‑part prompts or few‑shot examples, use labels or prefixes to delineate inputs and outputs.  For instance, in a translation prompt, prefix the source text with \"English:\" and place the desired output label (such as \"French:\" or \"JSON:\") so the model knows what to produce【229385501113536†screenshot】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Add prefixes"}
      ]
    },
    {
      "chunk_id": "GEMDOC__008",
      "title": "Decomposing complex prompts",
      "category": "prompting",
      "summary": "Break complicated tasks into smaller steps, chain prompts sequentially, or aggregate responses when prompting the model【852300939187095†screenshot】【567952097142389†screenshot】.",
      "tags": ["decomposition","chaining","aggregation"],
      "models": ["Gemini 3","Gemini 2.5"],
      "capabilities": ["reasoning","analysis","extraction","generation"],
      "task_types": ["structured_output","analysis","multimodal","other"],
      "key_terms": ["break down","chain prompts","aggregate responses"],
      "content": "For complex tasks, divide the prompt into components.  Use sequential steps (planning then execution) or chain multiple prompts where each handles a subtask.  When working on large data sets, perform operations separately (e.g., summarizing sections) then aggregate the results【852300939187095†screenshot】【567952097142389†screenshot】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Break down prompts into components"}
      ]
    },
    {
      "chunk_id": "GEMDOC__009",
      "title": "Tuning model parameters: max tokens, temperature, topK and topP",
      "category": "parameters",
      "summary": "`max_output_tokens` limits the length of the response; `temperature` controls randomness (higher temperature yields more diverse outputs); `topK` and `topP` adjust token sampling distribution; `stop_sequences` specify where generation should end【936949385138201†screenshot】.",
      "tags": ["parameters","temperature","topK","topP","stop_sequences"],
      "models": ["Gemini 3","Gemini 2.5"],
      "capabilities": ["text","multimodal"],
      "task_types": ["generation","analysis","classification"],
      "key_terms": ["max_output_tokens","temperature","topK","topP","stop_sequences"],
      "content": "Gemini models support several generation parameters.  `max_output_tokens` limits response length; `temperature` controls creativity (0 = deterministic; higher values increase randomness); `topK` restricts sampling to the top K candidate tokens; `topP` selects tokens whose cumulative probability is ≤ topP; and `stop_sequences` tell the model where to stop generating【936949385138201†screenshot】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Experiment with model parameters"}
      ]
    },
    {
      "chunk_id": "GEMDOC__010",
      "title": "Prompt iteration strategies",
      "category": "evaluation",
      "summary": "Iterate on prompts by rephrasing tasks, framing them as analogous multiple‑choice questions, or reordering prompt elements to improve clarity【475677898775248†screenshot】【471422393604552†screenshot】.",
      "tags": ["iteration","rephrasing","analogous tasks","order"],
      "models": ["Gemini 3","Gemini 2.5"],
      "capabilities": ["analysis","generation","classification"],
      "task_types": ["evaluation","analysis","prompt_refinement"],
      "key_terms": ["prompt iteration","multiple choice"],
      "content": "If the initial prompt does not yield the desired response, experiment with alternate phrasings or analogous tasks.  For example, instead of asking the model to categorize a book using open‑ended text, present choices labelled A, B or C.  Changing the order of context, examples and instructions may also improve results【475677898775248†screenshot】【471422393604552†screenshot】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Prompt iteration strategies"}
      ]
    },
    {
      "chunk_id": "GEMDOC__011",
      "title": "Fallback responses and things to avoid",
      "category": "constraints",
      "summary": "Safety filters may trigger fallback responses if the prompt violates content policies; avoid using the model for factual research or complex math, and specify instructions to reduce fallback frequency【540530589576552†screenshot】.",
      "tags": ["safety","fallback","avoid"],
      "models": ["Gemini 3","Gemini 2.5"],
      "capabilities": ["text"],
      "task_types": ["safety","constraints"],
      "key_terms": ["fallback responses","safety filter"],
      "content": "If the model cannot answer due to policy restrictions, it returns a generic fallback response.  Avoid tasks that require factual accuracy or complex arithmetic; Gemini models may hallucinate or miscalculate.  Increase the `temperature` or adjust the prompt to avoid generic refusals【540530589576552†screenshot】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Fallback responses"}
      ]
    },
    {
      "chunk_id": "GEMDOC__012",
      "title": "Gemini 3 core prompting principles",
      "category": "prompting",
      "summary": "For Gemini 3 models, be precise and direct, use consistent structure (e.g., XML or Markdown tags), define ambiguous parameters, control verbosity, handle multimodal inputs coherently, prioritize critical instructions, structure long context effectively and anchor the context before asking the question【945235487871224†screenshot】.",
      "tags": ["Gemini 3","principles","structure","multimodal"],
      "models": ["Gemini 3"],
      "capabilities": ["multimodal","reasoning"],
      "task_types": ["prompt_refinement","multimodal","analysis","generation"],
      "key_terms": ["precise","direct","XML tags","Markdown headings"],
      "content": "The Gemini 3 series responds best to structured prompts.  Key recommendations include: specify exactly what you want; separate sections with clear delimiters (XML‑style tags or Markdown headings); define parameters explicitly; request concise or elaborate tone; when combining text, images, audio or video, explain how to treat each modality; list critical instructions at the start; place large context blocks before the question; and use a transition phrase like ‘Based on the information above…’【945235487871224†screenshot】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Gemini 3"}
      ]
    },
    {
      "chunk_id": "GEMDOC__013",
      "title": "Gemini 3 Flash strategies",
      "category": "prompting",
      "summary": "For Gemini 3 Flash models, include clauses in system instructions specifying the current date and knowledge cutoff, and instruct the model to rely only on provided context for improved grounding and recency【188980658577262†screenshot】.",
      "tags": ["Flash","current_date","grounding"],
      "models": ["Gemini 3 Flash","Gemini 3 Flash‑Lite"],
      "capabilities": ["text","multimodal"],
      "task_types": ["prompt_refinement","grounding","analysis","generation"],
      "key_terms": ["current day accuracy","knowledge cutoff","grounding"],
      "content": "When prompting Gemini 3 Flash models, set expectations for temporal accuracy by stating the current date and the model’s knowledge cutoff.  Instruct the model to base its answers solely on the provided context, preventing hallucinations and ensuring that queries are grounded in up‑to‑date information【188980658577262†screenshot】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Gemini 3 Flash strategies"}
      ]
    },
    {
      "chunk_id": "GEMDOC__014",
      "title": "Enhancing reasoning and planning",
      "category": "prompting",
      "summary": "For complex tasks, ask the model to create a plan or critique its output before responding.  Provide explicit steps for planning and self‑review【862646917849235†screenshot】.",
      "tags": ["reasoning","planning","self_critique"],
      "models": ["Gemini 3","Gemini 2.5"],
      "capabilities": ["reasoning","analysis"],
      "task_types": ["analysis","prompt_refinement","evaluation"],
      "key_terms": ["plan","critique","steps"],
      "content": "Leverage Gemini 3’s reasoning abilities by requesting intermediate planning or self‑critique before the final answer.  For example, instruct the model to break the goal into subtasks, check for missing information and produce a structured outline.  Or ask it to review its answer against specified criteria (e.g., addressing user intent or matching tone) before returning the response【862646917849235†screenshot】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Enhancing reasoning and planning"}
      ]
    },
    {
      "chunk_id": "GEMDOC__015",
      "title": "Structured prompt templates (XML/Markdown)",
      "category": "prompting",
      "summary": "Use structured templates with labelled sections (role, instructions, constraints, output format) to guide Gemini models; XML tags or Markdown headings can clarify context, task and output structure【182299138828045†screenshot】.",
      "tags": ["structured_prompts","templates","XML","Markdown"],
      "models": ["Gemini 3"],
      "capabilities": ["structured_output","reasoning"],
      "task_types": ["prompt_refinement","analysis","multimodal"],
      "key_terms": ["role","instructions","constraints","output format"],
      "content": "Structured prompts organise information into sections using tags or headings.  The template might include a `<role>` defining the assistant persona, `<instructions>` listing steps (plan, execute, validate, format), `<constraints>` setting tone or length limits, and `<output_format>` describing the expected structure of the answer.  User input can then be placed in `<context>`, `<task>` and `<final_instruction>` sections【182299138828045†screenshot】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Structured prompting examples"}
      ]
    },
    {
      "chunk_id": "GEMDOC__016",
      "title": "Agentic workflows: reasoning and execution controls",
      "category": "workflows",
      "summary": "Agentic prompts can specify parameters such as logical decomposition, problem diagnosis depth, information exhaustiveness, adaptability, persistence, risk assessment and verbosity to control the model’s behavior【453578305430695†screenshot】【937544351825367†screenshot】.",
      "tags": ["agentic_workflows","controls","risk_assessment"],
      "models": ["Gemini 3","Gemini 2.5"],
      "capabilities": ["reasoning","tool_use"],
      "task_types": ["prompt_refinement","tool_use","analysis","other"],
      "key_terms": ["logical decomposition","adaptability","persistence","risk assessment","ambiguity handling","verbosity"],
      "content": "When designing prompts for agents, consider how much reasoning and planning the model should perform.  Specify whether to fully decompose problems or use abductive reasoning, how exhaustive the information gathering should be, how strictly to follow a plan versus adapt to new data, how persistent the agent should be in recovering from errors, and how to handle risk and ambiguity.  Control the verbosity of reasoning output and define the required precision of results【453578305430695†screenshot】【937544351825367†screenshot】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Agentic workflows"}
      ]
    },
    {
      "chunk_id": "GEMDOC__017",
      "title": "Sample system instruction for agentic workflows",
      "category": "workflows",
      "summary": "A detailed system instruction template outlines steps for agents: evaluate requested actions, check prerequisites, research policies, prepare risk assessments, sequence operations, call tools, validate results and summarise.【840931689929677†screenshot】.",
      "tags": ["agentic_workflows","template","system_instruction"],
      "models": ["Gemini 3","Gemini 2.5"],
      "capabilities": ["tool_use","structured_output","planning"],
      "task_types": ["tool_use","analysis","other"],
      "key_terms": ["system instruction","policies","risk assessment"],
      "content": "Agentic system instructions can include guidelines such as: confirm user actions, identify applicable policies, plan steps and create a numbered task list; separate high‑risk tasks requiring confirmation; perform research and reasoning before executing tool calls; call tools in sequence; evaluate tool results; summarise actions; and ask clarifying questions when necessary【840931689929677†screenshot】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Agentic workflows"}
      ]
    },
    {
      "chunk_id": "GEMDOC__018",
      "title": "Generative models under the hood",
      "category": "overview",
      "summary": "Gemini uses a two‑stage process: a deterministic transformer predicts token probabilities, then decoding sampling produces actual output; random sampling depends on temperature and sampling parameters【816797463408549†screenshot】.",
      "tags": ["randomness","sampling","determinism"],
      "models": ["Gemini 3","Gemini 2.5"],
      "capabilities": ["text"],
      "task_types": ["analysis","education"],
      "key_terms": ["deterministic transformer","sampling","temperature"],
      "content": "Generation involves two phases: a deterministic transformer calculates probabilities for the next token, and a decoder samples from this distribution.  Randomness arises during sampling and is controlled by parameters like temperature, topK and topP.  A low temperature (close to zero) yields deterministic outputs, whereas higher values introduce diversity【816797463408549†screenshot】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Generative models under the hood"}
      ]
    },
    {
      "chunk_id": "GEMDOC__019",
      "title": "Gemini model listings and version patterns",
      "category": "models",
      "summary": "The models page lists Gemini 3, Gemini 2.5, Nano Banana, Veo, Lyria and other specialized models.  Each model type has preview and stable versions; version names follow a pattern such as `gemini-2.5-flash` or `gemini-3.1-pro-preview-09-2025`【106980676632281†L188-L200】.",
      "tags": ["models","versioning"],
      "models": ["Gemini 3","Gemini 2.5","Nano Banana","Veo","Lyria","Imagen","Embeddings","Robotics"],
      "capabilities": ["text","image","video","audio","music","embeddings","robotics"],
      "task_types": ["model_selection"],
      "key_terms": ["preview","stable","experimental","gemini-3.1-pro-preview","gemini-2.5-flash"],
      "content": "Gemini models are grouped into families such as Gemini 3 (Pro, Flash, Flash‑Lite), Gemini 2.5 (Flash, Flash‑Lite, Pro), Nano Banana (image generation), Veo (video generation), Lyria (music generation), Imagen (text‑to‑image), Embeddings and Robotics.  Model version names indicate stability (stable, preview, experimental) and release date【106980676632281†L188-L200】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/models", "section": "Gemini 3"}
      ]
    },
    {
      "chunk_id": "GEMDOC__020",
      "title": "Interactions API basics and example request",
      "category": "endpoint",
      "summary": "The Interactions API simplifies state management and tool orchestration.  To create an interaction, send a POST request specifying the model and input; the API returns an interaction object with outputs【107660960480700†L248-L299】.",
      "tags": ["interactions_api","generateContent","POST"],
      "models": ["Gemini 3","Gemini 2.5","Nano Banana","Veo"],
      "capabilities": ["text","image","video","multimodal"],
      "task_types": ["generation","analysis","classification","multimodal","tool_use"],
      "key_terms": ["interactions.create","model","input","outputs","previous_interaction_id"],
      "content": "The Interactions API provides a unified interface to interact with Gemini models.  A basic request uses `client.interactions.create` or a POST to `/v1beta/interactions` with fields: `model` (e.g., `gemini-3-flash-preview`) and `input` (string or list of content objects).  The API returns an `interaction` object whose `outputs` property contains the model’s response【107660960480700†L248-L299】.  Conversations can be continued statefully by passing the previous interaction ID in the `previous_interaction_id` parameter【107660960480700†L333-L349】.",
      "code_blocks": [
        {"language": "python", "code": "from google import genai\nclient = genai.Client()\ninteraction = client.interactions.create(\n    model=\"gemini-3-flash-preview\",\n    input=\"Tell me a short joke about programming.\"\n)\nprint(interaction.outputs[-1].text)"},
        {"language": "bash", "code": "curl -X POST \"https://generativelanguage.googleapis.com/v1beta/interactions\" \\\n-H \"Content-Type: application/json\" \\\n-H \"x-goog-api-key: $GEMINI_API_KEY\" \\\n-d '{\n  \"model\": \"gemini-3-flash-preview\",\n  \"input\": \"Tell me a short joke about programming.\"\n}'"}
      ],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/interactions", "section": "Basic interactions"}
      ]
    },
    {
      "chunk_id": "GEMDOC__021",
      "title": "Interactions API: stateful conversations",
      "category": "endpoint",
      "summary": "Continue a conversation by passing the ID of a previous interaction to the `previous_interaction_id` parameter.  The API remembers conversation history and only requires the new input【107660960480700†L333-L349】.",
      "tags": ["stateful","conversation"],
      "models": ["Gemini 3","Gemini 2.5"],
      "capabilities": ["dialog","analysis","multimodal"],
      "task_types": ["generation","analysis","tool_use"],
      "key_terms": ["previous_interaction_id","stateful conversation"],
      "content": "To maintain conversation context, call `client.interactions.create` with `previous_interaction_id` set to the ID of the prior interaction.  Only the new input must be supplied; the API inherits previous settings and context from the referenced interaction【107660960480700†L333-L349】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/interactions", "section": "Stateful conversation"}
      ]
    },
    {
      "chunk_id": "GEMDOC__022",
      "title": "Structured outputs via JSON Schema",
      "category": "structured_outputs",
      "summary": "Gemini models can be instructed to output data conforming to a JSON Schema.  This ensures predictable, type‑safe results for data extraction, classification and agentic workflows【287061243240597†L181-L195】.",
      "tags": ["structured_outputs","json_schema","data extraction"],
      "models": ["Gemini 3","Gemini 2.5"],
      "capabilities": ["structured_output","tool_use"],
      "task_types": ["extraction","classification","analysis","tool_use"],
      "key_terms": ["JSON Schema","object","array","string","integer"],
      "content": "Structured outputs allow you to define a JSON Schema that the model must follow.  This is ideal for data extraction, structured classification or generating inputs for tools.  The REST API and SDKs support defining schemas using standard types (`object`, `array`, `string`, `integer`) and tools such as Pydantic (Python) or Zod (JavaScript)【287061243240597†L181-L195】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/structured-output", "section": "Structured outputs"}
      ]
    },
    {
      "chunk_id": "GEMDOC__023",
      "title": "Thinking models and configuration",
      "category": "thinking",
      "summary": "Gemini 3 and 2.5 models support a ‘thinking process’ that improves reasoning and planning.  Use a model supporting thinking and specify the request as usual; results include deeper reasoning【584876917905493†L181-L196】.",
      "tags": ["thinking","reasoning","planning"],
      "models": ["Gemini 3","Gemini 2.5"],
      "capabilities": ["thinking","analysis","planning"],
      "task_types": ["analysis","generation","prompt_refinement"],
      "key_terms": ["thinking","thinking models"],
      "content": "Thinking models (in the Gemini 3 and 2.5 series) use an internal process to improve reasoning and multi‑step planning.  To enable this, specify a model variant with thinking support (e.g., `gemini-3-flash-preview`).  Request composition remains the same; the difference lies in the depth and structure of the response【584876917905493†L181-L196】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/thinking", "section": "Generating content with thinking"}
      ]
    }
  ],
  "index": {
    "by_category": {
      "overview": ["GEMDOC__018"],
      "models": ["GEMDOC__019"],
      "endpoint": ["GEMDOC__020","GEMDOC__021"],
      "structured_outputs": ["GEMDOC__022"],
      "thinking": ["GEMDOC__023"],
      "prompting": ["GEMDOC__001","GEMDOC__002","GEMDOC__003","GEMDOC__004","GEMDOC__005","GEMDOC__006","GEMDOC__007","GEMDOC__008","GEMDOC__012","GEMDOC__013","GEMDOC__014","GEMDOC__015"],
      "parameters": ["GEMDOC__009"],
      "evaluation": ["GEMDOC__010"],
      "constraints": ["GEMDOC__011"],
      "workflows": ["GEMDOC__016","GEMDOC__017"],
      "examples": [],
      "formats": [],
      "limits": [],
      "safety": ["GEMDOC__011"],
      "errors": [],
      "tools": [],
      "other": []
    },
    "by_tag": {
      "clarity": ["GEMDOC__001"],
      "input_types": ["GEMDOC__001"],
      "partial_input": ["GEMDOC__002"],
      "few_shot": ["GEMDOC__002","GEMDOC__004","GEMDOC__005"],
      "examples": ["GEMDOC__002","GEMDOC__004","GEMDOC__005"],
      "constraints": ["GEMDOC__003","GEMDOC__011"],
      "response_format": ["GEMDOC__003"],
      "zero_shot": ["GEMDOC__004"],
      "patterns": ["GEMDOC__005"],
      "consistency": ["GEMDOC__005"],
      "context": ["GEMDOC__006"],
      "prefixes": ["GEMDOC__007"],
      "decomposition": ["GEMDOC__008"],
      "parameters": ["GEMDOC__009"],
      "iteration": ["GEMDOC__010"],
      "safety": ["GEMDOC__011"],
      "Gemini 3": ["GEMDOC__012"],
      "Flash": ["GEMDOC__013"],
      "reasoning": ["GEMDOC__014","GEMDOC__018","GEMDOC__016"],
      "planning": ["GEMDOC__014"],
      "templates": ["GEMDOC__015","GEMDOC__017"],
      "agentic_workflows": ["GEMDOC__016","GEMDOC__017"],
      "randomness": ["GEMDOC__018"],
      "models": ["GEMDOC__019"],
      "interactions_api": ["GEMDOC__020","GEMDOC__021"],
      "structured_outputs": ["GEMDOC__022"],
      "thinking": ["GEMDOC__023"]
    },
    "by_key_term": {
      "question": ["GEMDOC__001"],
      "task": ["GEMDOC__001"],
      "entity": ["GEMDOC__001"],
      "prefix": ["GEMDOC__002","GEMDOC__007"],
      "example": ["GEMDOC__002","GEMDOC__004"],
      "constraints": ["GEMDOC__003","GEMDOC__011"],
      "JSON": ["GEMDOC__002","GEMDOC__003","GEMDOC__022"],
      "few shot": ["GEMDOC__004","GEMDOC__005"],
      "patterns": ["GEMDOC__005"],
      "context": ["GEMDOC__006"],
      "prefixes": ["GEMDOC__007"],
      "chain prompts": ["GEMDOC__008"],
      "max_output_tokens": ["GEMDOC__009"],
      "temperature": ["GEMDOC__009"],
      "topK": ["GEMDOC__009"],
      "topP": ["GEMDOC__009"],
      "stop_sequences": ["GEMDOC__009"],
      "multiple choice": ["GEMDOC__010"],
      "fallback responses": ["GEMDOC__011"],
      "Gemini 3": ["GEMDOC__012"],
      "current day accuracy": ["GEMDOC__013"],
      "knowledge cutoff": ["GEMDOC__013"],
      "plan": ["GEMDOC__014"],
      "self critique": ["GEMDOC__014"],
      "role": ["GEMDOC__015"],
      "instructions": ["GEMDOC__015"],
      "constraints": ["GEMDOC__015"],
      "output format": ["GEMDOC__015"],
      "logical decomposition": ["GEMDOC__016"],
      "risk assessment": ["GEMDOC__016"],
      "system instruction": ["GEMDOC__017"],
      "sampling": ["GEMDOC__018"],
      "preview": ["GEMDOC__019"],
      "interactions.create": ["GEMDOC__020"],
      "previous_interaction_id": ["GEMDOC__021"],
      "JSON Schema": ["GEMDOC__022"],
      "thinking": ["GEMDOC__023"]
    },
    "by_model": {
      "Gemini 3": ["GEMDOC__001","GEMDOC__002","GEMDOC__003","GEMDOC__004","GEMDOC__005","GEMDOC__006","GEMDOC__007","GEMDOC__008","GEMDOC__009","GEMDOC__010","GEMDOC__011","GEMDOC__012","GEMDOC__013","GEMDOC__014","GEMDOC__015","GEMDOC__016","GEMDOC__017","GEMDOC__018","GEMDOC__019","GEMDOC__020","GEMDOC__021","GEMDOC__022","GEMDOC__023"],
      "Gemini 2.5": ["GEMDOC__001","GEMDOC__002","GEMDOC__003","GEMDOC__004","GEMDOC__005","GEMDOC__006","GEMDOC__007","GEMDOC__008","GEMDOC__009","GEMDOC__010","GEMDOC__011","GEMDOC__014","GEMDOC__016","GEMDOC__017","GEMDOC__018","GEMDOC__019","GEMDOC__020","GEMDOC__021","GEMDOC__022","GEMDOC__023"],
      "Nano Banana": ["GEMDOC__001","GEMDOC__020"],
      "Veo": ["GEMDOC__020"],
      "Lyria": ["GEMDOC__019"],
      "Imagen": ["GEMDOC__019"],
      "Embeddings": ["GEMDOC__019"],
      "Robotics": ["GEMDOC__019"]
    },
    "by_capability": {
      "text": ["GEMDOC__001","GEMDOC__002","GEMDOC__003","GEMDOC__004","GEMDOC__005","GEMDOC__006","GEMDOC__007","GEMDOC__008","GEMDOC__009","GEMDOC__010","GEMDOC__011","GEMDOC__012","GEMDOC__013","GEMDOC__014","GEMDOC__015","GEMDOC__018","GEMDOC__019","GEMDOC__020","GEMDOC__021"],
      "multimodal": ["GEMDOC__001","GEMDOC__006","GEMDOC__012","GEMDOC__013","GEMDOC__014","GEMDOC__020","GEMDOC__023"],
      "structured_output": ["GEMDOC__003","GEMDOC__007","GEMDOC__015","GEMDOC__022"],
      "reasoning": ["GEMDOC__008","GEMDOC__014","GEMDOC__016","GEMDOC__018"],
      "analysis": ["GEMDOC__001","GEMDOC__004","GEMDOC__005","GEMDOC__006","GEMDOC__008","GEMDOC__009","GEMDOC__010","GEMDOC__012","GEMDOC__014","GEMDOC__016","GEMDOC__017","GEMDOC__018","GEMDOC__019","GEMDOC__020","GEMDOC__021","GEMDOC__022","GEMDOC__023"],
      "tool_use": ["GEMDOC__016","GEMDOC__017","GEMDOC__022","GEMDOC__020"],
      "planning": ["GEMDOC__014","GEMDOC__016","GEMDOC__017","GEMDOC__023"],
      "thinking": ["GEMDOC__014","GEMDOC__023"],
      "structured_output": ["GEMDOC__022"]
    },
    "by_task_type": {
      "prompt_refinement": ["GEMDOC__001","GEMDOC__003","GEMDOC__004","GEMDOC__005","GEMDOC__007","GEMDOC__008","GEMDOC__009","GEMDOC__010","GEMDOC__012","GEMDOC__013","GEMDOC__014","GEMDOC__015"],
      "analysis": ["GEMDOC__001","GEMDOC__004","GEMDOC__005","GEMDOC__006","GEMDOC__008","GEMDOC__009","GEMDOC__010","GEMDOC__014","GEMDOC__016","GEMDOC__017","GEMDOC__018","GEMDOC__020","GEMDOC__021","GEMDOC__022","GEMDOC__023"],
      "generation": ["GEMDOC__001","GEMDOC__002","GEMDOC__003","GEMDOC__004","GEMDOC__006","GEMDOC__007","GEMDOC__008","GEMDOC__009","GEMDOC__010","GEMDOC__012","GEMDOC__013","GEMDOC__014","GEMDOC__015","GEMDOC__020","GEMDOC__021"],
      "classification": ["GEMDOC__001","GEMDOC__004","GEMDOC__005","GEMDOC__006","GEMDOC__009","GEMDOC__010","GEMDOC__022"],
      "extraction": ["GEMDOC__001","GEMDOC__006","GEMDOC__009","GEMDOC__022"],
      "reasoning": ["GEMDOC__008","GEMDOC__014","GEMDOC__016","GEMDOC__018","GEMDOC__023"],
      "structured_output": ["GEMDOC__003","GEMDOC__007","GEMDOC__015","GEMDOC__022"],
      "multimodal": ["GEMDOC__001","GEMDOC__006","GEMDOC__008","GEMDOC__012","GEMDOC__013","GEMDOC__015","GEMDOC__020","GEMDOC__023"],
      "evaluation": ["GEMDOC__010","GEMDOC__016","GEMDOC__017"],
      "tool_use": ["GEMDOC__016","GEMDOC__017","GEMDOC__022","GEMDOC__020"],
      "other": ["GEMDOC__016","GEMDOC__017"]
    }
  }
}
```

## C) Prompt Template Library — JSON

This JSON file provides foundational templates with variable placeholders.  Templates are categorized by type, task and recommended models.  The `origin` field indicates whether the pattern is documented in the source or is an IA Decision (a design choice informed by the documentation).

```
{
  "template_pack_id": "gemini_prompt_templates__ai_google_dev__v1",
  "source_domain": "ai.google.dev",
  "generated_at": "2026-03-06T00:00:00Z",
  "templates": [
    {
      "template_id": "TMPL__001",
      "title": "System instruction template for analysis tasks",
      "template_type": "system",
      "task_types": ["analysis","prompt_refinement"],
      "recommended_models": ["Gemini 3"],
      "prompting_patterns": ["structured","XML"],
      "variables": ["[assistant_role]","[tone]","[constraints]"],
      "template_text": "<role>You are a [assistant_role]. Respond in a [tone] manner.</role>\n<instructions>1. Read the context and task carefully.\n2. Plan your approach and break down the problem into steps.\n3. Execute the plan and generate your answer.\n4. Validate that the answer addresses the user’s intent and meets the constraints.\n5. Format the response according to the specified structure.</instructions>\n<constraints>[constraints]</constraints>",
      "origin": "IA DECISION",
      "doc_basis": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Structured prompting examples"}
      ],
      "usage_notes": "Adapt the roles and tone to the domain.  Insert this system instruction before user prompts for tasks requiring planning and analysis."
    },
    {
      "template_id": "TMPL__002",
      "title": "Direction prompt with input, context and constraints",
      "template_type": "direction",
      "task_types": ["analysis","generation","extraction"],
      "recommended_models": ["Gemini 3","Gemini 2.5"],
      "prompting_patterns": ["structured","Markdown"],
      "variables": ["[context]","[task]","[constraints]"],
      "template_text": "# Context\n[context]\n\n# Task\n[task]\n\n# Constraints\n[constraints]\n\n# Output Format\nProvide the answer in the specified format.",
      "origin": "docs",
      "doc_basis": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Gemini 3"}
      ],
      "usage_notes": "Use clear Markdown headers to separate the context, task and constraints.  Include any required JSON schema or formatting instructions under the constraints section."
    },
    {
      "template_id": "TMPL__003",
      "title": "Few‑shot classification template",
      "template_type": "refinement",
      "task_types": ["classification","extraction"],
      "recommended_models": ["Gemini 3","Gemini 2.5"],
      "prompting_patterns": ["few_shot"],
      "variables": ["[examples]","[new_input]","[output_label]"],
      "template_text": "Classify the following input based on the provided examples.\n\nExamples:\n[examples]\n\nNew Input: [new_input]\n\nAnswer in the form: [output_label]: <your answer>",
      "origin": "docs",
      "doc_basis": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Zero-shot vs few-shot prompts"}
      ],
      "usage_notes": "Ensure the examples are consistently formatted.  The model will infer the pattern from the examples and apply it to the new input."
    },
    {
      "template_id": "TMPL__004",
      "title": "Structured output template with JSON Schema",
      "template_type": "structured_output",
      "task_types": ["extraction","structured_output","classification"],
      "recommended_models": ["Gemini 3","Gemini 2.5"],
      "prompting_patterns": ["schema"],
      "variables": ["[schema]","[input_text]"],
      "template_text": "Use the following JSON Schema to structure the output:\n[schema]\n\nExtract the relevant information from the input and produce a JSON object that satisfies the schema.\n\nInput:\n[input_text]",
      "origin": "docs",
      "doc_basis": [
        {"url": "https://ai.google.dev/gemini-api/docs/structured-output", "section": "Structured outputs"}
      ],
      "usage_notes": "Place the schema in-line.  The model will validate its output against the schema and return a predictable JSON object."
    },
    {
      "template_id": "TMPL__005",
      "title": "Refinement prompt for reasoning and planning",
      "template_type": "refinement",
      "task_types": ["analysis","planning","generation"],
      "recommended_models": ["Gemini 3"],
      "prompting_patterns": ["plan_and_execute"],
      "variables": ["[goal]","[criteria]"],
      "template_text": "Before answering, please do the following steps:\n1. Parse the goal: [goal].\n2. Break it down into sub‑tasks and list them.\n3. Identify any missing information.\n4. Create a brief outline of your approach.\n5. Execute your plan and return the final answer.\n\nCheck your answer against these criteria: [criteria] and refine if necessary.",
      "origin": "docs",
      "doc_basis": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Enhancing reasoning and planning"}
      ],
      "usage_notes": "Use this template when tasks require deep reasoning or multi‑step planning.  The criteria can include tone, accuracy or completeness."
    },
    {
      "template_id": "TMPL__006",
      "title": "Agentic workflow system instruction",
      "template_type": "system",
      "task_types": ["tool_use","analysis","other"],
      "recommended_models": ["Gemini 3"],
      "prompting_patterns": ["agentic"],
      "variables": ["[policies]","[risk_level]"],
      "template_text": "You are an agentic assistant.  For each user request:\n1. Evaluate whether the requested actions are permitted under these policies: [policies].\n2. Decompose the problem into a sequence of steps.\n3. Identify prerequisites, resources and potential risks.  If risk level is above [risk_level], ask for user confirmation.\n4. Plan the tasks and call appropriate tools.  After each tool call, verify outputs before proceeding.\n5. Summarise the actions taken and results.  Ask clarifying questions if necessary.",
      "origin": "docs",
      "doc_basis": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Agentic workflows"}
      ],
      "usage_notes": "This template helps configure an agentic model to follow policies, manage risk, plan steps and use tools.  Provide a list of policies and a risk tolerance."
    },
    {
      "template_id": "TMPL__007",
      "title": "Model selection decision prompt",
      "template_type": "model_selection",
      "task_types": ["model_selection"],
      "recommended_models": ["Gemini 3","Gemini 2.5","Nano Banana","Veo","Lyria","Imagen"],
      "prompting_patterns": ["decision_tree"],
      "variables": ["[user_goal]","[input_modalities]"],
      "template_text": "Choose the most appropriate Gemini model for the following task.\n\nUser goal: [user_goal]\nInput modalities: [input_modalities]\n\nConsider the model families (Gemini 3 for advanced reasoning, Gemini 2.5 for high‑volume tasks, Nano Banana for images, Veo for videos, Lyria for music, Imagen for text‑to‑image).  Explain your choice in one sentence.",
      "origin": "IA DECISION",
      "doc_basis": [
        {"url": "https://ai.google.dev/gemini-api/docs/models", "section": "Gemini 3"}
      ],
      "usage_notes": "Use this template as a decision guide when the assistant must select the right model based on the user’s goal and input modality."
    },
    {
      "template_id": "TMPL__008",
      "title": "Evaluation and critique template",
      "template_type": "evaluation",
      "task_types": ["evaluation","iteration"],
      "recommended_models": ["Gemini 3","Gemini 2.5"],
      "prompting_patterns": ["self_critique"],
      "variables": ["[response]","[criteria]"],
      "template_text": "Given the model’s response:\n[response]\n\nCritique the response based on these criteria: [criteria].\nIdentify any errors or omissions and suggest how to improve the prompt or the response.",
      "origin": "IA DECISION",
      "doc_basis": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Enhancing reasoning and planning"}
      ],
      "usage_notes": "Use this template to evaluate outputs and decide how to iterate on prompts for better results."
    },
    {
      "template_id": "TMPL__009",
      "title": "Multimodal prompting template",
      "template_type": "multimodal",
      "task_types": ["multimodal","analysis","generation"],
      "recommended_models": ["Gemini 3","Gemini 2.5"],
      "prompting_patterns": ["multimodal"],
      "variables": ["[text_input]","[image_descriptions]","[audio_descriptions]","[constraints]"],
      "template_text": "You will receive multiple types of inputs.\n\nText: [text_input]\nImages: [image_descriptions]\nAudio: [audio_descriptions]\n\nTask: Combine information from all modalities to accomplish the task.\nConstraints: [constraints]\n\nProvide your final answer, clearly referencing how each modality informed your conclusion.",
      "origin": "IA DECISION",
      "doc_basis": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Gemini 3"}
      ],
      "usage_notes": "Use this template when the task requires combining text, images or audio inputs.  Clearly describe each modality and instruct the model to integrate them."
    },
    {
      "template_id": "TMPL__010",
      "title": "Tool decision template",
      "template_type": "tool_decision",
      "task_types": ["tool_use"],
      "recommended_models": ["Gemini 3"],
      "prompting_patterns": ["decision_tree"],
      "variables": ["[task_description]","[available_tools]"],
      "template_text": "Given the task description:\n[task_description]\n\nand the following tools:\n[available_tools]\n\nDecide whether to call a tool or answer directly.  If using a tool, specify which one and why.  Otherwise, state why a tool is unnecessary.",
      "origin": "IA DECISION",
      "doc_basis": [
        {"url": "https://ai.google.dev/gemini-api/docs/prompting-strategies", "section": "Agentic workflows"}
      ],
      "usage_notes": "This template helps the assistant decide whether a tool call is needed.  Provide the list of available tools with descriptions." 
    }
  ],
  "index": {
    "by_template_type": {
      "system": ["TMPL__001","TMPL__006"],
      "direction": ["TMPL__002"],
      "refinement": ["TMPL__003","TMPL__005"],
      "structured_output": ["TMPL__004"],
      "evaluation": ["TMPL__008"],
      "iteration": ["TMPL__008"],
      "model_selection": ["TMPL__007"],
      "tool_decision": ["TMPL__010"],
      "multimodal": ["TMPL__009"],
      "workflow": []
    },
    "by_task_type": {
      "analysis": ["TMPL__001","TMPL__002","TMPL__005","TMPL__008"],
      "generation": ["TMPL__002","TMPL__005","TMPL__009"],
      "extraction": ["TMPL__002","TMPL__003","TMPL__004"],
      "classification": ["TMPL__003","TMPL__004"],
      "reasoning": ["TMPL__005"],
      "structured_output": ["TMPL__004"],
      "multimodal": ["TMPL__009"],
      "evaluation": ["TMPL__008"],
      "iteration": ["TMPL__008"],
      "model_selection": ["TMPL__007"],
      "tool_use": ["TMPL__006","TMPL__010"],
      "other": []
    },
    "by_model": {
      "Gemini 3": ["TMPL__001","TMPL__002","TMPL__003","TMPL__004","TMPL__005","TMPL__006","TMPL__007","TMPL__008","TMPL__009","TMPL__010"],
      "Gemini 2.5": ["TMPL__002","TMPL__003","TMPL__004","TMPL__005","TMPL__007","TMPL__008","TMPL__009"],
      "Nano Banana": [],
      "Veo": [],
      "Lyria": [],
      "Imagen": []
    },
    "by_pattern": {
      "structured": ["TMPL__001","TMPL__002"],
      "few_shot": ["TMPL__003"],
      "schema": ["TMPL__004"],
      "plan_and_execute": ["TMPL__005"],
      "agentic": ["TMPL__006"],
      "decision_tree": ["TMPL__007","TMPL__010"],
      "self_critique": ["TMPL__008"],
      "multimodal": ["TMPL__009"]
    }
  }
}
```

## D) Metadata Categorization Blueprint (IA)

### Category list and definitions (IA DECISION)

| Category | Definition |
| --- | --- |
| **overview** | High‑level descriptions of model behavior, generation processes or general background. |
| **models** | Information about model families, versioning, capabilities and naming patterns. |
| **model_selection** | Guidelines for choosing the appropriate model for a task based on capabilities, performance and modality. |
| **capabilities** | Descriptions of what the models can do (text generation, image generation, video, audio, structured outputs, reasoning, tool use). |
| **modalities** | Support for different input/output types (text, image, video, audio, files) and multimodal combinations. |
| **endpoint** | API endpoints and their usage in SDKs or REST, including parameters like `model`, `input` and conversation state management. |
| **request_schema** | Structure of API requests: fields, `contents` array, safety settings, generation config, tool config and schema definitions. |
| **response_schema** | Fields returned by the API (e.g., `outputs`, streaming chunks, generated files) and metadata. |
| **parameters** | Adjustable configuration options that influence generation (max tokens, temperature, topK, topP, stop sequences). |
| **tools** | Information about built‑in tools (Search, Maps, Code execution, File search, etc.) and how to call them via function calling. |
| **structured_outputs** | How to specify JSON schemas and extract structured data from model outputs. |
| **thinking** | Use of thinking‑enabled models and thinking configuration for reasoning and planning. |
| **prompting** | Best practices for crafting prompts, including clarity, examples, context, prefixes, decomposition and iteration strategies. |
| **evaluation** | Methods to critique and improve model outputs, iterate on prompts and refine responses. |
| **constraints** | Limitations and safety considerations: fallback responses, avoidance of factual research and tasks outside the model’s capabilities. |
| **limits** | Hard limits such as context size, rate limits, token quotas (not detailed in our sources). |
| **safety** | Safety guidance, filters and content policies (some covered under constraints). |
| **errors** | Known error messages and troubleshooting steps (not covered in our sources). |
| **workflows** | Complex prompting patterns for agents, including reasoning controls, planning steps and system instruction templates. |
| **examples** | Code examples and illustrative prompts demonstrating usage (embedded within chunks). |
| **formats** | Output or input formats (e.g., JSON, YAML, Markdown). |
| **other** | Miscellaneous items that don’t fit other categories. |

### Tagging rules (IA DECISION)

* Tags describe the main ideas in a chunk.  Use nouns or short phrases like `clarity`, `few_shot`, `parameters`, `agentic_workflows`.  Do not include verbs or adjectives.  Tags must be deterministic: if a chunk mentions temperature or topK, include the `parameters` tag; if it describes conversation state, include `stateful`.  Use the models and capabilities tags sparingly—only when the chunk content explicitly references a specific model or capability.

### Model tagging rules (IA DECISION)

* A chunk should list all models to which the information applies.  If the chunk covers general guidance (e.g., clarity), include all major Gemini series (Gemini 3, Gemini 2.5).  If the chunk is about a specific model feature (Flash strategies), list only the relevant model (Gemini 3 Flash).  Include specialized models (Nano Banana, Veo) only when directly referenced.

### Capability tagging rules (IA DECISION)

* Capabilities indicate what functions the described feature supports: `text`, `image`, `video`, `audio`, `structured_output`, `reasoning`, `planning`, `tool_use`, etc.  Assign capabilities when the chunk content relates to that type of output or operation.  For example, a chunk on structured outputs should include `structured_output`; a chunk on thinking should include `planning` and `reasoning`.

### Task type rules (IA DECISION)

* Task types classify the user tasks addressed by a chunk: `prompt_refinement`, `analysis`, `generation`, `classification`, `extraction`, `reasoning`, `structured_output`, `multimodal`, `evaluation`, `tool_use`, `model_selection`, `other`.  Use multiple task types if the chunk applies to several.  For example, parameter tuning affects generation, analysis and classification tasks.

### Key term rules (IA DECISION)

* Key terms are exact identifiers (field names, parameter names, model IDs, endpoint paths, enumeration values).  Include each identifier once per chunk.  Do not include human‑readable phrases.  For instance, use `max_output_tokens` rather than “maximum tokens”.  These terms enable precise retrieval when looking up documentation.

### Chunk sizing rules (IA DECISION)

* Each chunk should express a single idea or closely related set of ideas.  Avoid combining unrelated concepts into one chunk.  Chunks should be short—one or two paragraphs—so that retrieval returns only the necessary information.  If a section covers multiple topics (e.g., parameters and iteration), split it into separate chunks.

### Template classification rules (IA DECISION)

* Templates are classified by `template_type` (system, direction, refinement, evaluation, iteration, model_selection, tool_decision, structured_output, multimodal, workflow) and by `task_types` and `patterns`.  Use `origin` to differentiate between patterns drawn directly from the docs (`docs`) and those designed as IA decisions (`IA DECISION`).

### Retrieval patterns for a Gem/GPT/agent

* To find guidance on a particular aspect of prompting or capabilities, the assistant should search the index by category (`prompting`, `parameters`, `models`, etc.) and then filter by tags or key terms.  For instance, to tune randomness, search for the key term `temperature`; to find model‑selection advice, search by category `models` and tag `versioning`.  Use the template index to locate a template by type or pattern (e.g., `few_shot` or `plan_and_execute`).

## E) Downstream Assistant Spec — “Gemini Prompting + Capability Expert”

This specification defines the behavior of a downstream assistant (e.g., a Gem or GPT) that is preloaded with the knowledge base above and the prompt template library.  Its goal is to help users craft effective prompts for various tasks using Gemini models and capabilities.

### 1) Input intake

* The assistant should collect the following information from the user:
  - **User goal**: a concise description of what the user wants to achieve.
  - **Desired output type**: e.g., text, structured data (JSON), image, video, audio.
  - **Input modalities**: whether the user will provide text, images, audio or videos.
  - **Specific constraints or preferences**: such as length limits, tone, style, or formatting requirements.
  - **Existing examples or context**: any relevant examples or domain knowledge the user wants to include.

* **Decision rule**: Ask only when missing information blocks proper task classification, model selection, request assembly or output quality.  For instance, if the user does not specify the desired output format, ask whether the answer should be free text or structured JSON.

### 2) Task classification

* Use the user goal and modalities to classify the task into one or more of the defined task types: `generation`, `analysis`, `extraction`, `classification`, `structured_output`, `multimodal`, `reasoning`, `evaluation`, `model_selection`, `tool_use` or `other`.  If the user’s task cannot be mapped directly to a documented type, classify it as `other` and proceed conservatively.  These classifications influence model selection and prompt refinement.

* **Classification heuristics (IA DECISION)**:  
  - **Generation**: tasks requiring the model to produce new text, code or media.  
  - **Analysis**: tasks requiring summarization, explanation or reasoning over provided input.  
  - **Extraction**: tasks requiring specific fields or facts pulled from text, images or other media.  
  - **Classification**: tasks requiring assignment of a label or category.  
  - **Structured output**: tasks requiring the output to conform to a JSON schema.  
  - **Multimodal**: tasks requiring understanding or combining multiple modalities.  
  - **Reasoning**: tasks requiring multi‑step planning or logic.  
  - **Evaluation**: tasks requiring review and critique of model outputs.  
  - **Model_selection**: tasks requiring the assistant to choose the appropriate model.  
  - **Tool_use**: tasks requiring use of external tools (search, maps, code execution).  
  - **Other**: none of the above; proceed with caution and limit scope.

### 3) Model / capability selection

* Based on the task type(s) and modalities, select the most appropriate model from the Gemini family.  Use the model listings to map capabilities: 
  - **Gemini 3 Pro/Flash/Flash‑Lite**: advanced reasoning, multimodal understanding and tool use【106980676632281†L188-L200】.  
  - **Gemini 2.5 Flash/Flash‑Lite/Pro**: high‑volume tasks with good reasoning.  
  - **Nano Banana**: image generation and editing【106980676632281†L188-L200】.  
  - **Veo**: video generation【106980676632281†L188-L200】.  
  - **Lyria**: music generation【106980676632281†L292-L329】.  
  - **Imagen**: text‑to‑image【106980676632281†L331-L337】.  
  - **Embeddings**: vector embeddings for semantic search【106980676632281†L360-L366】.  
  - **Robotics**: embodied reasoning【106980676632281†L369-L372】.  

* If the task requires structured JSON or tool invocation, ensure the chosen model supports those features (e.g., use Gemini 3 models for tool use and structured outputs).  If unknown, mark `NOT FOUND IN SOURCE`.

### 4) Prompt refinement (doc‑anchored)

* **Step sequence**:
  1. **Clarify the user goal and desired format** using the input intake.  
  2. **Select an appropriate template** from the template library based on task type, model and desired pattern.  
  3. **Fill in the template variables** with user‑provided context, tasks, constraints and examples.  
  4. **Add context and examples** where needed: include domain knowledge or few‑shot examples to improve accuracy【596073122220472†screenshot】.  
  5. **Specify constraints and formatting** such as word limits, tone, output format or JSON Schema【489604398123491†screenshot】.  
  6. **Set model parameters** if necessary: adjust `max_output_tokens`, `temperature`, `topK`, `topP` or `stop_sequences` based on creative or deterministic needs【936949385138201†screenshot】.  
  7. **For Gemini 3 or Flash models**: apply core prompting principles—use consistent structure (XML/Markdown tags), specify knowledge cutoffs and ground answers on provided context【945235487871224†screenshot】【188980658577262†screenshot】.  
  8. **Add planning or self‑critique instructions** for reasoning‑heavy tasks【862646917849235†screenshot】.

* If the documentation lacks guidance for a particular refinement step (e.g., advanced tone tuning), keep the refinement conservative and label any heuristic as an IA Decision.

### 5) Request assembly (doc‑anchored)

* **Interactions API**: Use the Interactions API via SDK or REST.  Compose a request with fields:
  - `model`: selected model string (e.g., `gemini-3-flash-preview`).  
  - `input`: the refined prompt (string or content list).  
  - Optional `previous_interaction_id`: for stateful conversations【107660960480700†L333-L349】.  
  - Optional configuration: `generation_config` (parameters like `temperature`, `max_output_tokens`, `topK`, `topP`, `stop_sequences`), `safety_settings`, `tools` or `structured_output` definitions【107660960480700†L248-L299】.  
  - For JSON Schema outputs, include a `schema` definition as shown in the structured outputs documentation【287061243240597†L181-L195】.  

* **Background execution**: By default, interactions are stored (`store=true`) to enable state management.  Users can opt out if desired.【107660960480700†L333-L336】.

* For file, image, audio or video inputs, the assistant must instruct the user to upload the file or provide a URL if supported (beyond the scope of this KB).

* **Unknown fields**: If any necessary field is not documented (e.g., a specific API version), mark it as `NOT FOUND IN SOURCE` and advise the user to consult the official API reference.

### 6) Response handling (doc‑anchored)

* **Outputs**: The Interactions API returns an `interaction` object with an `outputs` array.  For generation tasks, the last element of `outputs` contains the response text【107660960480700†L248-L299】.  
* **Structured outputs**: When using a JSON Schema, parse the returned JSON and validate it against the schema【287061243240597†L181-L195】.  
* **Stateful conversation**: Keep track of the returned `interaction.id` to continue the conversation【107660960480700†L333-L349】.  
* **Fallback responses**: If the response contains a fallback message (e.g., the model declines to answer), identify this and either adjust the prompt (e.g., change temperature) or inform the user that the request is outside the model’s capabilities【540530589576552†screenshot】.

### 7) Evaluation and iteration

* After receiving a response, use the evaluation template (TMPL__008) to critique the output against the user’s criteria.  Identify errors, omissions or tone mismatches.  Suggest prompt revisions, such as adding examples, changing instructions, adjusting parameters or rephrasing the task【475677898775248†screenshot】.  
* Iterate using the refined prompt until the output meets the desired quality.  Document each iteration to track changes and improvements.

### 8) Output format

The assistant must return the following fields to the user:

| Field | Description |
| --- | --- |
| **original_request** | The user’s initial goal and any constraints they provided. |
| **task_type** | The task classification derived from the goal (e.g., generation, extraction, etc.). |
| **recommended_model_or_capability** | The chosen model or capability with a brief justification. |
| **refined_prompt** | The final prompt assembled using the template library and refinement steps. |
| **request_object** | The structured request (JSON) to be sent to the Interactions API, including model, input and configuration. |
| **response_handling_notes** | Instructions on how to extract the answer (e.g., parse JSON, use `outputs[-1].text`). |
| **evaluation_notes** | Critique of the output (if applicable) and recommendations for further iterations. |
| **next_iteration_prompt** | If further improvement is needed, a revised prompt or strategy for the next request. |

### 9) Stop conditions

* Stop when all relevant sections of the primary target pages have been broken into chunks; all required linked pages have been included; the Knowledge Pack JSON and Prompt Template Library JSON are complete and internally consistent; the metadata categorization blueprint covers categories, tags, models, capabilities, task types, key terms and retrieval rules; and the downstream assistant spec addresses input intake, task classification, model selection, prompt refinement, request assembly, response handling, evaluation and iteration, and output format.
