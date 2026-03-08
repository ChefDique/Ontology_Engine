# Source Manifest

## Seed URL

- `https://ai.google.dev/gemini-api/docs/image-generation` – seed page describing Nano Banana image generation with the Gemini API.

## Followed URLs (ai.google.dev only)

| URL | Title | Why It Was Required |
|---|---|---|
| `https://ai.google.dev/gemini-api/docs/image-understanding` | **Image understanding** | Provides the schema for passing images to Gemini using `inline_data` and `file_data` parts, including `mime_type` and `data` fields and limits on inline image size【586218367881151†L193-L204】【586218367881151†L448-L451】. These details are referenced from the seed page’s editing examples and are needed to specify request formats. |
| `https://ai.google.dev/gemini-api/docs/thinking` | **Gemini thinking** | Describes the `ThinkingConfig` used to control the model’s thinking behaviour, including `include_thoughts`, `thinking_level`, and `thinking_budget` parameters【897686323495013†L290-L320】【897686323495013†L596-L687】. These parameters are referenced on the image‑generation page for thinking-enabled models and are required for the request schema. |

## Coverage Statement

All sections of the seed page were reviewed. The page covers model descriptions, generation examples in multiple languages, configuration options (`response_modalities`, `image_config`, `thinking_config`), thinking behaviour, limitations and supported languages, high‑resolution outputs, aspect ratio and image‑size tables, reference image limits, prompt and editing guidelines, grounding via Google Search and Image Search, safety and attribution requirements, and model selection advice. Each of these sections has been normalized into atomic chunks below.

# Knowledge Pack — JSON

```json
{
  "kb_id": "gemini_image_generation__ai_google_dev__v1",
  "source_domain": "ai.google.dev",
  "seed_url": "https://ai.google.dev/gemini-api/docs/image-generation",
  "generated_at": "2026-03-06T00:00:00Z",
  "chunks": [
    {
      "chunk_id": "IMGGEN__001",
      "title": "Overview of Nano Banana image generation",
      "category": "overview",
      "summary": "The Nano Banana image generation guide introduces how to generate images with Gemini models. It highlights the ability to prototype UI‑complete apps using prompts and shows that Nano Banana 2 integrates with real‑world tools and the Gemini ecosystem【484164859719448†L181-L200】. The page sets the context for the following sections by positioning image generation as a way to build functional interfaces from text prompts.",
      "tags": ["overview", "Nano Banana"],
      "key_terms": ["Nano Banana", "image generation", "Gemini API"],
      "content": "Nano Banana image generation allows developers to create fully‑functional user interfaces from prompts before writing any code. The introduction notes that the latest preview (Nano Banana 2) is integrated with Gemini tools and can produce complex prototypes directly from descriptive text【484164859719448†L181-L200】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Nano Banana image generation introduction"}
      ]
    },
    {
      "chunk_id": "IMGGEN__002",
      "title": "Gemini image generation models and IDs",
      "category": "models",
      "summary": "The Nano Banana page defines three image‑generation models: *gemini‑3.1‑flash‑image‑preview* (Nano Banana 2 preview), *gemini‑3‑pro‑image‑preview* (Nano Banana Pro preview), and *gemini‑2.5‑flash‑image* (Nano Banana). Each model has different capabilities: 3.1 Flash balances performance and cost, 3 Pro is optimized for professional asset production with higher resolutions and thinking, and 2.5 Flash focuses on high‑volume, low‑latency generation【484164859719448†L5534-L5590】. The models support up to 4K resolution and differ in the number of reference images allowed.",
      "tags": ["models", "flash", "pro", "resolution"],
      "key_terms": ["gemini-3.1-flash-image-preview", "gemini-3-pro-image-preview", "gemini-2.5-flash-image"],
      "content": "Three models are available for image generation. *Gemini 3.1 Flash Image Preview* offers the best balance of intelligence, cost, and latency and should be the default choice【484164859719448†L5534-L5590】. *Gemini 3 Pro Image Preview* is designed for professional asset production, supports real‑world grounding via Google Search, provides default thinking to refine composition, and generates images up to 4K【484164859719448†L5534-L5590】. *Gemini 2.5 Flash Image* is optimized for speed and efficiency with 1024px resolution【484164859719448†L5534-L5590】. Model IDs correspond to their names (e.g., \"gemini-3.1-flash-image-preview\").",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Model selection"}
      ]
    },
    {
      "chunk_id": "IMGGEN__003",
      "title": "New features in Gemini 3 image models",
      "category": "overview",
      "summary": "Gemini 3 image models introduce high‑resolution outputs (1K, 2K, 4K and 512px for Flash), advanced text rendering, integration with Google Search and Image Search for grounding, a thinking mode that provides interim thoughts, support for up to 14 reference images (split between object and character limits), and new aspect ratios such as 1:4, 4:1, 1:8, and 8:1【484164859719448†L1015-L1048】. These enhancements make the models suitable for professional use and complex prompts.",
      "tags": ["features", "resolution", "search", "thinking"],
      "key_terms": ["1K", "2K", "4K", "512px", "reference images", "aspect_ratio", "Google Search"],
      "content": "The Gemini 3 models build on earlier versions by adding several important capabilities. Users can generate high‑resolution images up to 4K (with 512px also available in Flash) and access advanced typography for accurate text in images. The models can ground content using Google Search and Image Search, produce interim \"thinking\" images before final output, and accept up to 14 reference images (10 objects and 4 characters) in one request【484164859719448†L1015-L1048】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "New features in Gemini 3 models"}
      ]
    },
    {
      "chunk_id": "IMGGEN__004",
      "title": "Request structure for image generation",
      "category": "request_schema",
      "summary": "A `generate_content` request includes a `model` identifier and a `contents` array. Each content item has a `parts` list that may contain text (`{\"text\": \"...\"}`), inline images (`{\"inline_data\": {\"mime_type\": \"image/png\", \"data\": \"base64...\"}}`), or file references (`{\"file_data\": {\"mime_type\": ..., \"file_uri\": ...}}`). Optional `config`/`generationConfig` fields specify response modalities (TEXT or IMAGE), `image_config` (aspect_ratio and image_size), and `thinking_config` (include_thoughts, thinking_level, thinking_budget)【586218367881151†L285-L307】【586218367881151†L448-L451】【897686323495013†L596-L687】. The total request size when using inline image data must be under 20 MB【586218367881151†L448-L451】.",
      "tags": ["request", "schema", "inline_data", "file_data"],
      "key_terms": ["model", "contents", "parts", "text", "inline_data", "file_data", "mime_type", "data", "file_uri", "config", "generationConfig", "response_modalities", "image_config", "aspect_ratio", "image_size", "thinking_config", "include_thoughts", "thinking_level", "thinking_budget"],
      "content": "To generate images, send a POST request to `/v1beta/models/{model}:generateContent`. Specify the `model` (e.g., gemini‑3.1‑flash‑image‑preview) and provide `contents` as a list of messages from the user. Each message contains a `parts` array: text parts are objects with a `text` field; images can be provided inline using `inline_data` with `mime_type` and Base64‑encoded `data` or by referencing uploaded files with `file_data` containing a `mime_type` and a `file_uri`【586218367881151†L285-L307】【586218367881151†L448-L451】. The request may include `config` (for the SDK) or `generationConfig` (in REST) with `response_modalities` (\"TEXT\" or \"IMAGE\"), `image_config` (aspect_ratio and image_size), and `thinking_config` (parameters controlling the model’s internal thinking)【897686323495013†L596-L687】. When using inline images, the total request size (text and inline bytes) must be under 20 MB【586218367881151†L448-L451】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-understanding", "section": "Passing inline image data"},
        {"url": "https://ai.google.dev/gemini-api/docs/image-understanding", "section": "Uploading images using the File API"},
        {"url": "https://ai.google.dev/gemini-api/docs/thinking", "section": "Thinking configuration"}
      ]
    },
    {
      "chunk_id": "IMGGEN__005",
      "title": "Response structure for image generation",
      "category": "response_schema",
      "summary": "The response to `generate_content` returns a list of `candidates`. Each candidate has a `content` field containing `parts`, where each part may have a `text` or `inlineData`/`inline_data` field. Image parts include `data` (Base64) and `mimeType`. When thinking is enabled, the response also includes parts with a `thought` boolean and thought summaries. The response contains usage metadata with `thoughtsTokenCount` and `candidatesTokenCount`, and may include `groundingMetadata` with search entry points, grounding chunks, image search queries and URIs when Google Search or Image Search is used【897686323495013†L838-L854】【484164859719448†L1630-L1667】.",
      "tags": ["response", "schema", "thought", "grounding"],
      "key_terms": ["candidates", "content", "parts", "text", "inlineData", "mimeType", "thought", "thoughtsTokenCount", "candidatesTokenCount", "groundingMetadata", "searchEntryPoint", "groundingChunks", "imageSearchQueries", "uri", "image_uri"],
      "content": "`generate_content` responses include one or more `candidates`. Each candidate has `content.parts` that contain either text or image parts; image parts carry base64‑encoded data and the MIME type. When thinking is enabled, some parts include a `thought` flag and summarised thought text. Usage metadata includes `thoughtsTokenCount` and `candidatesTokenCount` fields to report the number of tokens used for thoughts and the final response【897686323495013†L838-L854】. If the model uses Google Search or Image Search, the response contains `groundingMetadata` fields such as `searchEntryPoint`, `groundingChunks` with `uri` and `image_uri` fields, and `imageSearchQueries`, which must be used to attribute results【484164859719448†L1630-L1667】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/thinking", "section": "Thought signatures"},
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Grounding metadata"}
      ]
    },
    {
      "chunk_id": "IMGGEN__006",
      "title": "Basic text‑to‑image generation example (Python)",
      "category": "examples",
      "summary": "A minimal example uses the Python SDK to generate an image from a text prompt. The client calls `generate_content` with the model ID, a single text prompt, and saves the returned image part as a PNG file【484164859719448†L295-L320】.",
      "tags": ["example", "python", "text-to-image"],
      "key_terms": ["client.models.generate_content", "model", "prompt", "image.save"],
      "content": "The example demonstrates generating an image with Python: create a `genai.Client`, specify `model=\"gemini-3.1-flash-image-preview\"`, pass a single text prompt in the `contents` array, and call `generate_content`. The response’s `parts` include image data, which can be converted to a PIL Image and saved using `image.save()`【484164859719448†L295-L320】.",
      "code_blocks": [
        {"language": "python", "code": "from google import genai\nfrom google.genai import types\n\nclient = genai.Client()\nprompt = \"A photo of a glossy magazine cover...\"\nresponse = client.models.generate_content(\n    model=\"gemini-3.1-flash-image-preview\",\n    contents=[prompt],\n)\nimage_data = response.candidates[0].content.parts[0].inline_data\n# convert inline_data.data from base64 and save\n"}
      ],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Basic Python example"}
      ]
    },
    {
      "chunk_id": "IMGGEN__007",
      "title": "Text‑and‑image editing example (JavaScript)",
      "category": "examples",
      "summary": "To edit an image, the request includes both a text description of the edit and the original image encoded as Base64. The JavaScript example shows reading an image file, converting it to Base64, sending it along with a prompt, and saving the returned image【484164859719448†L488-L522】.",
      "tags": ["example", "javascript", "editing"],
      "key_terms": ["inlineData", "mimeType", "data", "generateContent", "editing"],
      "content": "In a JS editing example, an image is read as a Base64 string and passed to `generateContent` along with a prompt describing the edit. The request includes an object with `inlineData` containing the MIME type and Base64 data and another part with the edit instruction. The response’s image data is saved to a file【484164859719448†L488-L522】.",
      "code_blocks": [
        {"language": "javascript", "code": "import { GoogleGenAI } from \"@google/genai\";\nimport fs from 'fs';\n\nasync function editImage() {\n  const ai = new GoogleGenAI({});\n  const imageBytes = fs.readFileSync('path/to/image.png', { encoding: 'base64' });\n  const result = await ai.models.generateContent({\n    model: 'gemini-3.1-flash-image-preview',\n    contents: [\n      { inlineData: { mimeType: 'image/png', data: imageBytes } },\n      { text: 'Add a realistic apple on the table' },\n    ],\n  });\n  // Save result.candidates[0].content.parts\n}\neditImage();\n"}
      ],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Image editing example"}
      ]
    },
    {
      "chunk_id": "IMGGEN__008",
      "title": "Multi‑turn chat editing workflow",
      "category": "workflows",
      "summary": "The API supports conversational editing where a chat is created and messages are sent iteratively. The example uses `client.chats.create` and `chat.send_message` with `response_modalities` set to ['TEXT', 'IMAGE'] and optionally includes the `google_search` tool to ground responses【484164859719448†L650-L700】.",
      "tags": ["chat", "workflow", "editing", "tools"],
      "key_terms": ["client.chats.create", "chat.send_message", "response_modalities", "tools", "google_search"],
      "content": "For multi‑turn editing, an initial chat is created using `client.chats.create(model, system_instruction, response_modalities, tools)`. Subsequent edits are sent using `chat.send_message` with new prompts and optional images. The chat can include tools like `google_search` to retrieve real‑time information【484164859719448†L650-L700】. Responses include both text and images in the specified `response_modalities`.",
      "code_blocks": [
        {"language": "python", "code": "chat = client.chats.create(\n    model='gemini-3.1-flash-image-preview',\n    response_modalities=['TEXT', 'IMAGE'],\n    tools=['google_search'],\n)\nresponse = chat.send_message('Add a sun setting behind the mountains.', images=[img])\n"}
      ],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Multi‑turn chat example"}
      ]
    },
    {
      "chunk_id": "IMGGEN__009",
      "title": "Configuring response modalities and aspect ratio",
      "category": "parameters",
      "summary": "The `response_modalities` field controls whether the API returns text, image, or both. Setting `response_modalities` to ['Image'] yields only an image. `image_config` allows specifying `aspect_ratio` (e.g., '16:9') and, for Gemini 3 models, `image_size` ('1K', '2K', '4K' or '512px' for Flash)【484164859719448†L5292-L5359】【484164859719448†L5361-L5414】.",
      "tags": ["response_modalities", "aspect_ratio", "image_size"],
      "key_terms": ["response_modalities", "IMAGE", "TEXT", "image_config", "aspect_ratio", "image_size"],
      "content": "By default, Gemini returns both text and images. To receive only images, set `response_modalities=['Image']` in `config` or `generationConfig`【484164859719448†L5292-L5359】. The `image_config` object contains `aspect_ratio` (e.g., '16:9', '1:1', '3:2') and, for Gemini 3 models, an optional `image_size` specifying the resolution (\"1K\", \"2K\", \"4K\" or, for Flash models, \"512px\")【484164859719448†L5361-L5414】.",
      "code_blocks": [
        {"language": "python", "code": "response = client.models.generate_content(\n    model='gemini-3.1-flash-image-preview',\n    contents=[prompt],\n    config=types.GenerateContentConfig(response_modalities=['Image'],\n      image_config=types.ImageConfig(aspect_ratio='16:9', image_size='2K'))\n)\n"}
      ],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Optional configurations: output types and aspect ratios"}
      ]
    },
    {
      "chunk_id": "IMGGEN__010",
      "title": "Aspect ratio and resolution tables",
      "category": "limits",
      "summary": "The docs provide tables mapping aspect ratios to pixel dimensions and token counts for each model. For Gemini 3.1 Flash preview, aspect ratios like 1:1 (512×512, 1K, 2K, 4K), 1:4, 1:8, 2:3, 3:2, 3:4, 4:1, 4:3, 4:5, 5:4, 8:1, 9:16, 16:9 and 21:9 are listed with corresponding resolutions and token counts【484164859719448†L5516-L5533】. Gemini 3 Pro preview lists similar aspect ratios for 1K, 2K and 4K resolutions【484164859719448†L5534-L5548】. Gemini 2.5 Flash supports up to 1024×1024 with tokens specified for each ratio【484164859719448†L5550-L5562】.",
      "tags": ["aspect_ratio", "resolution", "token_counts"],
      "key_terms": ["16:9", "1:1", "2:3", "3:2", "4:3", "resolution", "tokens", "4K", "2K", "1K", "512px"],
      "content": "The documentation includes detailed tables for each model. For Gemini 3.1 Flash preview, each aspect ratio corresponds to specific pixel dimensions at 512px, 1K, 2K and 4K resolutions, along with token counts (e.g., 1:1 yields 512×512 at 512px, 1024×1024 at 1K, 2048×2048 at 2K, and 4096×4096 at 4K)【484164859719448†L5516-L5533】. Gemini 3 Pro preview provides similar tables for 1K, 2K and 4K resolutions【484164859719448†L5534-L5548】. Gemini 2.5 Flash lists aspect ratios (1:1 through 21:9) at 1024px resolution with token counts【484164859719448†L5550-L5562】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Aspect ratio tables"}
      ]
    },
    {
      "chunk_id": "IMGGEN__011",
      "title": "Reference images and limits",
      "category": "limits",
      "summary": "Gemini 3 models allow up to 14 reference images per request. For Gemini 3.1 Flash preview, the limit is 10 object images and 4 character images; for Gemini 3 Pro preview, the limit is 6 object images and 5 character images【484164859719448†L1042-L1081】. Gemini 2.5 Flash works best with up to 3 input images【484164859719448†L5274-L5284】.",
      "tags": ["reference_images", "limits"],
      "key_terms": ["reference images", "object images", "character images", "gemini-3.1-flash-image-preview", "gemini-3-pro-image-preview", "gemini-2.5-flash-image"],
      "content": "The models support mixing multiple reference images. Gemini 3.1 Flash preview allows up to 10 object images and 4 character images in one request; Gemini 3 Pro preview permits up to 6 object images and 5 character images【484164859719448†L1042-L1081】. Gemini 2.5 Flash is optimized for 1–3 input images【484164859719448†L5274-L5284】. Exceeding these limits may degrade fidelity.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Reference image limits"}
      ]
    },
    {
      "chunk_id": "IMGGEN__012",
      "title": "High‑resolution image sizes and uppercase 'K' requirement",
      "category": "constraints",
      "summary": "Gemini 3 models support high‑resolution outputs. Gemini 3.1 Flash preview can produce images at 512px, 1K, 2K and 4K, while Gemini 3 Pro preview supports 1K, 2K and 4K. When specifying the `image_size` in `image_config`, the ‘K’ must be uppercase (e.g., '1K', '2K', '4K'); using a lowercase 'k' is invalid【484164859719448†L1668-L1675】.",
      "tags": ["resolution", "uppercase", "constraint"],
      "key_terms": ["image_size", "1K", "2K", "4K", "512px"],
      "content": "To generate high‑resolution images, set `image_size` in the `image_config`. Gemini 3.1 Flash preview supports 512px (Flash only), 1K, 2K and 4K; Gemini 3 Pro preview supports 1K, 2K and 4K. The documentation warns that the \"K\" in the size must be uppercase; lowercase values like \"2k\" are invalid【484164859719448†L1668-L1675】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "High‑resolution image generation"}
      ]
    },
    {
      "chunk_id": "IMGGEN__013",
      "title": "Controlling thinking behaviour: include_thoughts and thinking level",
      "category": "parameters",
      "summary": "`ThinkingConfig` controls the model’s reasoning behaviour. The `include_thoughts` boolean requests a thought summary in the response. The `thinking_level` parameter (Gemini 3 models only) accepts 'low', 'minimal', or allows the default dynamic high setting; setting 'minimal' reduces thought generation but cannot fully disable thinking for Gemini 3 Pro【897686323495013†L596-L687】. For Gemini 2.5 models, `thinking_budget` specifies the number of tokens used for thinking, with –1 enabling dynamic thinking and 0 disabling thinking【897686323495013†L694-L719】.",
      "tags": ["thinking", "include_thoughts", "thinking_level", "thinking_budget"],
      "key_terms": ["include_thoughts", "thinking_level", "low", "minimal", "thinking_budget", "dynamic", "thinkingConfig"],
      "content": "To observe the model’s reasoning, set `thinking_config.include_thoughts` to `true`. Gemini 3 models support a `thinking_level` parameter that accepts values such as 'low' or 'minimal', while leaving it unspecified uses the model’s default dynamic high thinking【897686323495013†L596-L687】. Thinking cannot be completely disabled in Gemini 3 Pro, but using 'minimal' reduces the likelihood of thoughts. For Gemini 2.5 models, `thinking_budget` determines how many tokens the model may use for internal reasoning; 0 disables thinking and –1 enables dynamic budgets【897686323495013†L694-L719】.",
      "code_blocks": [
        {"language": "python", "code": "response = client.models.generate_content(\n    model='gemini-3.1-flash-image-preview',\n    contents=prompt,\n    config=types.GenerateContentConfig(\n        thinking_config=types.ThinkingConfig(include_thoughts=True, thinking_level='minimal')\n    )\n)\n"}
      ],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/thinking", "section": "Thinking levels and budgets"}
      ]
    },
    {
      "chunk_id": "IMGGEN__014",
      "title": "Handling thought signatures and token pricing",
      "category": "constraints",
      "summary": "When thinking is enabled, Gemini returns encrypted thought signatures in some parts of the response. These signatures must be passed back in subsequent requests to preserve context. The signature appears for image parts (except thought images) and the first non‑thought text part. Thought tokens contribute to billing even if `include_thoughts` is false【897686323495013†L838-L854】【484164859719448†L2074-L2150】.",
      "tags": ["thought_signatures", "pricing", "context"],
      "key_terms": ["thought signature", "includeThoughts", "thoughtsTokenCount", "candidatesTokenCount"],
      "content": "In multi‑turn interactions with thinking enabled, Gemini attaches encrypted thought signatures to parts of the response. These signatures must be returned unchanged in subsequent requests to maintain context, particularly when function calling is used【897686323495013†L838-L854】. Signatures appear on all image parts (except those within thought parts) and on the first text part after thoughts【484164859719448†L2074-L2150】. Even if thought summaries aren’t returned, the model generates thought tokens that are billed; usage metadata fields `thoughtsTokenCount` and `candidatesTokenCount` help estimate pricing【897686323495013†L838-L854】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/thinking", "section": "Thought signatures"},
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Thought signatures"}
      ]
    },
    {
      "chunk_id": "IMGGEN__015",
      "title": "Prompting guidance: photorealistic scenes",
      "category": "prompting",
      "summary": "For photorealistic scenes, prompts should include shot type, subject, environment, lighting, mood, camera details and aspect ratio. Being specific about these elements leads to better results【484164859719448†L2190-L2206】.",
      "tags": ["prompting", "photorealistic", "scene"],
      "key_terms": ["shot type", "subject", "environment", "lighting", "mood", "camera", "aspect_ratio"],
      "content": "To generate photorealistic images, specify the shot type (e.g., close‑up, wide shot), the subject and environment, lighting conditions, the desired mood, and camera parameters. Including the aspect ratio in the prompt helps control composition【484164859719448†L2190-L2206】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Photorealistic prompts guidance"}
      ]
    },
    {
      "chunk_id": "IMGGEN__016",
      "title": "Prompting guidance: stylized illustrations and stickers",
      "category": "prompting",
      "summary": "When requesting stylized illustrations or stickers, specify the art style (e.g., watercolor, anime), subject, color palette, line style, shading and request a transparent background【484164859719448†L2416-L2431】.",
      "tags": ["prompting", "illustrations", "stickers"],
      "key_terms": ["art style", "color palette", "line style", "shading", "transparent background"],
      "content": "For stylized illustrations and stickers, the prompt should name the art style (such as cel‑shaded or watercolor), describe the subject, state the desired color palette, and mention line and shading styles. To create a sticker, ask for a transparent background【484164859719448†L2416-L2431】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Stylized illustrations & stickers guidance"}
      ]
    },
    {
      "chunk_id": "IMGGEN__017",
      "title": "Prompting guidance: accurate text in images",
      "category": "prompting",
      "summary": "To render text accurately, specify the exact text, font style, design style and color scheme. Including these details helps the model generate legible, correctly styled text【484164859719448†L2576-L2584】.",
      "tags": ["prompting", "text"],
      "key_terms": ["text", "font style", "design style", "color scheme"],
      "content": "When the image should contain specific text (such as a logo or label), include the exact text string, desired font style (e.g., serif, sans‑serif), design aesthetic, and color scheme in the prompt【484164859719448†L2576-L2584】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Accurate text guidance"}
      ]
    },
    {
      "chunk_id": "IMGGEN__018",
      "title": "Prompting guidance: product mockups and commercial photography",
      "category": "prompting",
      "summary": "For product mockups and commercial photography, describe the product, background, lighting, camera angle, and aspect ratio. Mention the environment (studio, natural), lighting setup and product perspective【484164859719448†L2771-L2791】.",
      "tags": ["prompting", "product", "commercial"],
      "key_terms": ["product", "background", "lighting", "camera angle", "studio"],
      "content": "To generate realistic product mockups, specify the type of product and its design, describe the background and environment, state the lighting setup (e.g., softbox, natural sunlight), and choose a camera angle (e.g., 45° top‑down). Indicate the desired aspect ratio to control composition【484164859719448†L2771-L2791】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Product mockups guidance"}
      ]
    },
    {
      "chunk_id": "IMGGEN__019",
      "title": "Prompting guidance: minimalist and negative space design",
      "category": "prompting",
      "summary": "Minimalist prompts focus on a single subject, a simple background with negative space, and clear lighting. Use prompts like 'a small object centered on a solid background' and specify aspect ratio【484164859719448†L2969-L2981】.",
      "tags": ["prompting", "minimalist", "negative space"],
      "key_terms": ["single subject", "negative space", "background", "aspect_ratio"],
      "content": "For minimalist designs, the prompt should describe one clear subject, an uncluttered background (often a single colour or gradient), and the desired amount of negative space around the subject. Specify the lighting and aspect ratio to guide composition【484164859719448†L2969-L2981】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Minimalist and negative space guidance"}
      ]
    },
    {
      "chunk_id": "IMGGEN__020",
      "title": "Prompting guidance: sequential art and storyboards",
      "category": "prompting",
      "summary": "Sequential art prompts describe multiple panels or scenes. The prompt should specify the number of panels, style, characters and narrative flow, ensuring character consistency across panels【484164859719448†L3151-L3157】.",
      "tags": ["prompting", "sequential art", "comic"],
      "key_terms": ["panels", "style", "characters", "narrative"],
      "content": "When creating comics or storyboards, state how many panels you need, describe the style (e.g., manga, vintage comic), and outline the characters and plot for each panel. Maintain consistency in character appearance between panels【484164859719448†L3151-L3157】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Sequential art guidance"}
      ]
    },
    {
      "chunk_id": "IMGGEN__021",
      "title": "Image editing: adding or removing elements",
      "category": "editing",
      "summary": "To add or remove elements in an image, provide the original image and a prompt describing the change. The model will add or remove the specified object while preserving style and perspective【484164859719448†L3520-L3579】.",
      "tags": ["editing", "add", "remove"],
      "key_terms": ["add", "remove", "element", "style", "perspective"],
      "content": "For simple edits, submit the original image as `inline_data` or `file_data` and specify the element to add or remove. Describe the desired object and ensure the prompt conveys style and perspective so the model integrates the change seamlessly【484164859719448†L3520-L3579】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Editing: adding and removing elements"}
      ]
    },
    {
      "chunk_id": "IMGGEN__022",
      "title": "Image editing: inpainting and semantic masking",
      "category": "editing",
      "summary": "Inpainting and semantic masking prompts specify the element to change while preserving all other aspects of the image. The request should include the original image and a text description of what to modify【484164859719448†L3794-L3820】.",
      "tags": ["editing", "inpainting", "masking"],
      "key_terms": ["inpainting", "semantic masking", "preserve", "modify"],
      "content": "To perform inpainting, send the original image and a prompt that identifies the exact element to alter and instructs the model to keep everything else unchanged. This ensures the model edits only the targeted region【484164859719448†L3794-L3820】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Inpainting and semantic masking"}
      ]
    },
    {
      "chunk_id": "IMGGEN__023",
      "title": "Image editing: style transfer",
      "category": "editing",
      "summary": "Style transfer prompts provide a base photograph and specify the desired art style (e.g., impressionist, watercolor). The model renders the content in the new style while preserving composition【484164859719448†L4021-L4043】.",
      "tags": ["editing", "style transfer"],
      "key_terms": ["style transfer", "art style", "preserve composition"],
      "content": "For style transfer, include a base image and a prompt requesting it to be rendered in a specific artistic style. Describe the style and color palette to guide the transformation, while instructing the model to maintain the original composition【484164859719448†L4021-L4043】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Style transfer"}
      ]
    },
    {
      "chunk_id": "IMGGEN__024",
      "title": "Image editing: advanced composition using multiple images",
      "category": "editing",
      "summary": "Advanced composition combines elements from multiple images. Provide both images and describe which parts to combine and the desired composition. The model merges the selected elements into a new image【484164859719448†L4263-L4279】.",
      "tags": ["editing", "advanced composition"],
      "key_terms": ["multiple images", "merge", "composition"],
      "content": "When blending multiple images, supply each as a separate part in the request and specify which elements from each image should appear in the final composition. This allows the model to merge objects or characters from different sources into one coherent scene【484164859719448†L4263-L4279】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Advanced composition"}
      ]
    },
    {
      "chunk_id": "IMGGEN__025",
      "title": "Using Google Search and Image Search for grounding",
      "category": "tools",
      "summary": "Gemini 3 models can ground images using Google Search and Image Search. To enable, include the `google_search` tool and set `searchTypes` (e.g., `{webSearch: true, imageSearch: true}`). Responses include `groundingMetadata` with `searchEntryPoint`, `groundingChunks`, `imageSearchQueries`, `uri` and `image_uri` for source attribution. When using Image Search, you must link to the original webpage from the image and provide direct navigation to the source page【484164859719448†L1630-L1667】.",
      "tags": ["grounding", "google_search", "image_search", "source attribution"],
      "key_terms": ["google_search", "searchTypes", "imageSearch", "groundingMetadata", "searchEntryPoint", "groundingChunks", "uri", "image_uri"],
      "content": "To ground an image in real‑world data, specify the `google_search` tool and, if needed, set `searchTypes` with `webSearch` and `imageSearch` flags. When Image Search is used, the API returns `groundingMetadata` containing `searchEntryPoint`, `groundingChunks` with `uri` and `image_uri`, and `imageSearchQueries`. You must attribute the source by linking to the original page and allowing direct navigation from the image【484164859719448†L1630-L1667】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Grounding and Image Search"}
      ]
    },
    {
      "chunk_id": "IMGGEN__026",
      "title": "Limitations of image generation",
      "category": "constraints",
      "summary": "The docs highlight limitations: best performance is in specific languages (EN, ar‑EG, de‑DE, es‑MX, fr‑FR, hi‑IN, id‑ID, it‑IT, ja‑JP, ko‑KR, pt‑BR, ru‑RU, ua‑UA, vi‑VN, zh‑CN); audio and video inputs are unsupported; the model may not produce the exact number of images requested; and each model has limits on input images (3 images for 2.5 Flash, 5–14 for Gemini 3)【484164859719448†L5274-L5289】. All generated images include a SynthID watermark【484164859719448†L5274-L5289】.",
      "tags": ["limitations", "languages", "watermark"],
      "key_terms": ["EN", "ar-EG", "de-DE", "es-MX", "audio", "video", "SynthID watermark"],
      "content": "Gemini’s image generation works best with certain languages such as English, Arabic (Egypt), German, Spanish (Mexico), French, Hindi, Indonesian, Italian, Japanese, Korean, Portuguese (Brazil), Russian, Ukrainian, Vietnamese, and Chinese (Simplified)【484164859719448†L5274-L5289】. The API does not accept audio or video inputs. Models may return fewer or more images than requested, and each model has its own limit on input images (up to 3 for gemini‑2.5‑flash‑image, up to 14 for gemini‑3 models)【484164859719448†L5274-L5289】. All images include a SynthID watermark for provenance【484164859719448†L5274-L5289】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Limitations"}
      ]
    },
    {
      "chunk_id": "IMGGEN__027",
      "title": "Model selection and using Imagen",
      "category": "models",
      "summary": "Guidance on choosing a model: Gemini 3.1 Flash preview is the default choice for general use; Gemini 3 Pro preview is intended for professional assets and complex instructions; Gemini 2.5 Flash is for high‑volume, low‑latency tasks. Imagen 4 and Imagen 4 Ultra, available via the Gemini API, offer specialized image generation for highest quality and should be used when image quality is paramount【484164859719448†L5534-L5593】.",
      "tags": ["model selection", "Imagen"],
      "key_terms": ["Imagen 4", "Imagen 4 Ultra", "gemini-3.1-flash-image-preview", "gemini-3-pro-image-preview", "gemini-2.5-flash-image"],
      "content": "Choose the image generation model based on your needs. Gemini 3.1 Flash preview provides a good balance of cost, latency and quality and should be the default model【484164859719448†L5534-L5590】. Gemini 3 Pro preview offers advanced features like grounding and default thinking for professional asset production【484164859719448†L5534-L5590】. Gemini 2.5 Flash is optimized for speed and efficiency【484164859719448†L5534-L5590】. When the highest image quality is required, use Imagen 4 or Imagen 4 Ultra via the Gemini API; these models generate one image at a time【484164859719448†L5586-L5593】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Model selection"}
      ]
    },
    {
      "chunk_id": "IMGGEN__028",
      "title": "Other configuration parameters and best practices",
      "category": "parameters",
      "summary": "The docs encourage providing detailed prompts (be hyper‑specific, include context and intent), iterating and refining the prompt, using step‑by‑step instructions for complex scenes, and employing semantic negative prompts (express what should be present rather than what should be absent)【484164859719448†L5250-L5273】. They also suggest controlling the camera using photographic terms like wide‑angle shot or low‑angle perspective【484164859719448†L5250-L5273】.",
      "tags": ["best practices", "prompting"],
      "key_terms": ["hyper-specific", "context", "intent", "iterate", "step-by-step", "semantic negative", "camera"],
      "content": "To achieve optimal results, the page recommends being hyper‑specific in prompts (e.g., describing armor details instead of saying 'fantasy armor'), providing context and intent (such as the purpose of the image), iterating and refining prompts through follow‑up instructions, using step‑by‑step instructions for complex scenes, and phrasing negatives semantically (describe what should be present rather than simply saying 'no cars')【484164859719448†L5250-L5273】. Control the composition using photographic language like wide‑angle shot, macro shot, or low‑angle perspective【484164859719448†L5250-L5273】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/image-generation", "section": "Best practices and prompting tips"}
      ]
    }
  ],
  "index": {
    "by_category": {
      "overview": ["IMGGEN__001", "IMGGEN__003"],
      "models": ["IMGGEN__002", "IMGGEN__027"],
      "request_schema": ["IMGGEN__004"],
      "response_schema": ["IMGGEN__005"],
      "examples": ["IMGGEN__006", "IMGGEN__007"],
      "workflows": ["IMGGEN__008"],
      "parameters": ["IMGGEN__009", "IMGGEN__013", "IMGGEN__028"],
      "limits": ["IMGGEN__010", "IMGGEN__011"],
      "constraints": ["IMGGEN__012", "IMGGEN__014", "IMGGEN__026"],
      "prompting": ["IMGGEN__015", "IMGGEN__016", "IMGGEN__017", "IMGGEN__018", "IMGGEN__019", "IMGGEN__020"],
      "editing": ["IMGGEN__021", "IMGGEN__022", "IMGGEN__023", "IMGGEN__024"],
      "tools": ["IMGGEN__025"],
      "best practices": ["IMGGEN__028"]
    },
    "by_tag": {
      "Nano Banana": ["IMGGEN__001"],
      "flash": ["IMGGEN__002"],
      "pro": ["IMGGEN__002"],
      "resolution": ["IMGGEN__002", "IMGGEN__003", "IMGGEN__010", "IMGGEN__012"],
      "search": ["IMGGEN__003", "IMGGEN__025"],
      "thinking": ["IMGGEN__003", "IMGGEN__013", "IMGGEN__014"],
      "schema": ["IMGGEN__004", "IMGGEN__005"],
      "example": ["IMGGEN__006", "IMGGEN__007"],
      "python": ["IMGGEN__006"],
      "javascript": ["IMGGEN__007"],
      "workflow": ["IMGGEN__008"],
      "response_modalities": ["IMGGEN__004", "IMGGEN__009"],
      "aspect_ratio": ["IMGGEN__004", "IMGGEN__009", "IMGGEN__010", "IMGGEN__019"],
      "image_size": ["IMGGEN__004", "IMGGEN__009", "IMGGEN__010", "IMGGEN__012"],
      "token_counts": ["IMGGEN__010"],
      "reference_images": ["IMGGEN__011"],
      "constraints": ["IMGGEN__012", "IMGGEN__014", "IMGGEN__026"],
      "include_thoughts": ["IMGGEN__013"],
      "thinking_level": ["IMGGEN__013"],
      "thinking_budget": ["IMGGEN__013"],
      "thought_signatures": ["IMGGEN__014"],
      "photorealistic": ["IMGGEN__015"],
      "illustrations": ["IMGGEN__016"],
      "stickers": ["IMGGEN__016"],
      "text": ["IMGGEN__017"],
      "product": ["IMGGEN__018"],
      "commercial": ["IMGGEN__018"],
      "minimalist": ["IMGGEN__019"],
      "sequential art": ["IMGGEN__020"],
      "add": ["IMGGEN__021"],
      "remove": ["IMGGEN__021"],
      "inpainting": ["IMGGEN__022"],
      "masking": ["IMGGEN__022"],
      "style transfer": ["IMGGEN__023"],
      "advanced composition": ["IMGGEN__024"],
      "grounding": ["IMGGEN__025"],
      "google_search": ["IMGGEN__025"],
      "image_search": ["IMGGEN__025"],
      "limitations": ["IMGGEN__026"],
      "model selection": ["IMGGEN__027"],
      "Imagen": ["IMGGEN__027"],
      "best practices": ["IMGGEN__028"],
      "prompting": ["IMGGEN__015", "IMGGEN__016", "IMGGEN__017", "IMGGEN__018", "IMGGEN__019", "IMGGEN__020", "IMGGEN__028"]
    },
    "by_key_term": {
      "Nano Banana": ["IMGGEN__001"],
      "gemini-3.1-flash-image-preview": ["IMGGEN__002", "IMGGEN__004", "IMGGEN__009", "IMGGEN__011", "IMGGEN__012", "IMGGEN__027"],
      "gemini-3-pro-image-preview": ["IMGGEN__002", "IMGGEN__004", "IMGGEN__011", "IMGGEN__027"],
      "gemini-2.5-flash-image": ["IMGGEN__002", "IMGGEN__011", "IMGGEN__026", "IMGGEN__027"],
      "inline_data": ["IMGGEN__004"],
      "file_data": ["IMGGEN__004"],
      "mime_type": ["IMGGEN__004"],
      "data": ["IMGGEN__004"],
      "file_uri": ["IMGGEN__004"],
      "response_modalities": ["IMGGEN__004", "IMGGEN__009"],
      "image_config": ["IMGGEN__004", "IMGGEN__009"],
      "aspect_ratio": ["IMGGEN__004", "IMGGEN__009", "IMGGEN__010", "IMGGEN__019"],
      "image_size": ["IMGGEN__004", "IMGGEN__009", "IMGGEN__010", "IMGGEN__012"],
      "thinking_config": ["IMGGEN__004", "IMGGEN__013"],
      "include_thoughts": ["IMGGEN__013"],
      "thinking_level": ["IMGGEN__013"],
      "thinking_budget": ["IMGGEN__013"],
      "thought signature": ["IMGGEN__014"],
      "groundingMetadata": ["IMGGEN__005", "IMGGEN__025"],
      "searchEntryPoint": ["IMGGEN__005", "IMGGEN__025"],
      "groundingChunks": ["IMGGEN__005", "IMGGEN__025"],
      "uri": ["IMGGEN__005", "IMGGEN__025"],
      "image_uri": ["IMGGEN__005", "IMGGEN__025"],
      "imageSearchQueries": ["IMGGEN__005", "IMGGEN__025"],
      "responseModalities": ["IMGGEN__009"],
      "1K": ["IMGGEN__003", "IMGGEN__009", "IMGGEN__010", "IMGGEN__012"],
      "2K": ["IMGGEN__003", "IMGGEN__009", "IMGGEN__010", "IMGGEN__012"],
      "4K": ["IMGGEN__003", "IMGGEN__009", "IMGGEN__010", "IMGGEN__012"],
      "512px": ["IMGGEN__003", "IMGGEN__010", "IMGGEN__012"],
      "reference images": ["IMGGEN__011"],
      "includeThoughts": ["IMGGEN__013"],
      "thinkingLevel": ["IMGGEN__013"],
      "thinkingBudget": ["IMGGEN__013"],
      "thoughtsTokenCount": ["IMGGEN__014"],
      "candidatesTokenCount": ["IMGGEN__014"],
      "SynthID watermark": ["IMGGEN__026"],
      "Imagen 4": ["IMGGEN__027"],
      "Imagen 4 Ultra": ["IMGGEN__027"],
      "hyper-specific": ["IMGGEN__028"],
      "semantic negative": ["IMGGEN__028"],
      "wide-angle shot": ["IMGGEN__028"],
      "macro shot": ["IMGGEN__028"]
    }
  }
}
```

# Metadata Categorization Blueprint (IA)

### Category Definitions

| Category | Definition |
|---|---|
| **overview** | High‑level descriptions of image generation capabilities, model purpose and major features. |
| **models** | Information about specific Gemini models, including IDs, capabilities, resolutions, and selection guidance. |
| **endpoint** | API endpoints and paths required to interact with the service. (Not needed in this seed; handled in request schema.) |
| **request_schema** | Structure of requests, including required and optional fields, allowed data types, and size limits. |
| **response_schema** | Structure of responses, including candidate lists, parts, image and text fields, thought indicators, grounding metadata and usage metadata. |
| **parameters** | Explanations of configurable options such as `response_modalities`, `image_config`, `thinking_config`, thinking levels and budgets. |
| **limits** | Quantitative limits like maximum number of reference images, supported aspect ratios, resolution tables, and language support. |
| **constraints** | Rules or restrictions, such as uppercase 'K' requirement for `image_size`, thought signature handling, and inability to disable thinking for certain models. |
| **prompting** | Guidelines on how to craft prompts for different types of images (photorealistic, illustrations, text in images, product photos, minimalist design, sequential art). |
| **editing** | Techniques for image editing (adding/removing elements, inpainting, style transfer, advanced composition). |
| **examples** | Concrete code examples demonstrating how to call the API in various languages. |
| **workflows** | Multi‑step procedures, such as conversational editing. |
| **tools** | Usage of external tools like Google Search or Image Search for grounding. |
| **best practices** | General advice for improving results, including hyper‑specific prompts, iteration and step‑by‑step instructions. |

### Tagging Rules (IA DECISION)

- Assign tags for primary concepts (e.g., model names, features like resolution or thinking) and context (e.g., editing, prompting). Tags should aid retrieval and are case‑sensitive.
- Use plural where appropriate (e.g., "models", "constraints") to group similar chunks.
- When a chunk covers multiple topics (e.g., resolution tables), assign tags reflecting each (e.g., `aspect_ratio`, `resolution`, `token_counts`).
- Tags should correspond to retrieval needs; avoid synonyms when a single canonical tag exists (e.g., use `editing` rather than `image editing`).

### Key Term Rules (IA DECISION)

- Include all exact identifiers from the documentation: model IDs (`gemini-3.1-flash-image-preview`), parameter names (`response_modalities`, `inline_data`), field names (`mime_type`, `file_uri`), enum values (`1K`, `low`, `minimal`), and tool names (`google_search`).
- List each key term once per chunk; repeat across chunks if the term appears in multiple contexts.
- Exclude generic words that do not help retrieval (e.g., "image", "prompt") unless they are part of an identifier.

### Chunk Sizing Rules (IA DECISION)

- Each chunk should capture a single coherent concept or procedure that can be retrieved independently.
- Summaries must be concise (1–3 sentences) and contain enough context to understand the concept without referring to other chunks.
- Code examples should be included only when they directly illustrate the concept; avoid duplicating similar code across multiple chunks.
- If a section includes multiple distinct ideas (e.g., separate types of prompt guidance), split into multiple chunks.

### Retrieval Patterns

- A Gem/GPT using this KB should first filter by category (e.g., `parameters` or `editing`), then narrow by tags (e.g., `thinking` or `style transfer`) and match key terms to locate specific fields or model IDs.
- For API assembly tasks, the assistant should retrieve `request_schema` and `parameters` chunks to identify required fields and allowable values.
- When refining user prompts, the assistant should retrieve `prompting` and `best practices` chunks for relevant guidance.
- When editing an image, the assistant should retrieve editing chunks (add/remove, inpainting, style transfer, advanced composition) and any applicable constraints or limits.

# Downstream Assistant Spec — “Image Prompt Refiner + Generator”

## 1. Input Intake

1. **Required information**: obtain the user’s original image prompt. Optionally, accept reference images and any desired configuration such as aspect ratio, image size, or whether the user wants both text and image output.
2. **Clarify when necessary**: ask follow‑up questions only if missing information will block request assembly (e.g., if the user provides multiple images without specifying which to combine). Use a single concise question to resolve critical ambiguities.
3. **Avoid unsolicited questions**: if a parameter is optional and not provided, assume sensible defaults (e.g., default aspect ratio and `response_modalities=['TEXT','IMAGE']`).

## 2. Prompt Refinement (DOC‑Anchored)

1. **Incorporate best practices**: refine the original prompt by adding specific descriptors as suggested in the documentation—shot type, subject, environment, lighting, mood, and camera details for photorealistic scenes【484164859719448†L2190-L2206】; art style, color palette and transparent background for illustrations【484164859719448†L2416-L2431】; exact text and font style when rendering text【484164859719448†L2576-L2584】; product details, background and lighting for product mockups【484164859719448†L2771-L2791】; etc.
2. **Preserve user intent**: do not add elements the user did not mention. Refinement should clarify and expand on existing ideas, not invent new concepts.
3. **Apply negative prompting sparingly**: if the user requests to exclude an element, rephrase as a positive description using semantic negatives (e.g., “an empty street with no cars”【484164859719448†L5250-L5273】).
4. **Respect constraints**: ensure the refined prompt stays within the scope of what the model supports (e.g., no audio/video inputs and respect the maximum number of reference images【484164859719448†L5274-L5289】).
5. **Maintain aspect ratio and resolution**: incorporate any user‑specified aspect ratio or choose a default (1:1) and ensure `image_size` values use uppercase 'K' when present【484164859719448†L1668-L1675】.

## 3. Request Assembly (DOC‑Anchored)

1. **Create a request object** with the following fields:
   - `model`: choose an appropriate model based on the user’s needs; default to `gemini-3.1-flash-image-preview` unless high fidelity is required (use `gemini-3-pro-image-preview`) or ultra‑fast generation is desired (use `gemini-2.5-flash-image`)【484164859719448†L5534-L5590】.
   - `contents`: an array containing a single content object. Each object must include a `parts` array. For text‑only prompts, include one part `{ "text": refined_prompt }`. If reference images are provided, include each image as an `inline_data` part (or `file_data` if uploaded via the Files API) with `mime_type` and Base64‑encoded `data`【586218367881151†L285-L307】.
   - `config` (SDK) or `generationConfig` (REST): specify `response_modalities` (e.g., `["IMAGE"]` to return only images)【484164859719448†L5292-L5359】. For aspect ratio or resolution changes, include `image_config` with `aspect_ratio` (e.g., `"16:9"`) and, when using Gemini 3, `image_size` (`"1K"`, `"2K"`, `"4K"`, or `"512px"`)【484164859719448†L5361-L5414】. If the user requests internal reasoning, add `thinking_config` with `include_thoughts` and optionally `thinking_level` or `thinking_budget`【897686323495013†L596-L719】.
   - **Optional `tools`**: include `google_search` if real‑time grounding is needed and specify `searchTypes` for web and/or image search【484164859719448†L1630-L1667】.
2. **Validate limits**: ensure that the number of reference images does not exceed 10 object + 4 character images for Gemini 3.1 Flash or 6 object + 5 character images for Gemini 3 Pro【484164859719448†L1042-L1081】. For Gemini 2.5 models, limit to 3 images【484164859719448†L5274-L5284】.
3. **Ensure request size**: if using inline images, total request payload (prompts plus Base64 bytes) must be under 20 MB【586218367881151†L448-L451】.

## 4. Response Handling (DOC‑Anchored)

1. **Extract the image**: iterate through `response.candidates[0].content.parts` and locate the first part that contains `inlineData`/`inline_data` (or `fileData`). Decode the Base64 `data` field and save or return it as the generated image【484164859719448†L295-L320】.
2. **Handle text**: if `response_modalities` includes text, capture the `text` parts as the model’s description or answer.
3. **Thought summaries**: when `include_thoughts` is true, identify parts where `part.thought` is true and treat them as reasoning summaries separate from the final answer【897686323495013†L290-L320】.
4. **Grounding metadata**: if Google Search or Image Search was used, inspect `groundingMetadata.groundingChunks` for `uri` and `image_uri` fields and attach them to the final output for source attribution【484164859719448†L1630-L1667】.
5. **Return signatures**: include any thought signatures exactly as returned in subsequent multi‑turn requests to preserve context【897686323495013†L838-L854】.

## 5. Output Format

The assistant must return an object containing:

- `original_prompt`: the user’s initial prompt string.
- `refined_prompt`: the refined prompt after applying the guidance above.
- `generation_request`: the full structured request object ready for the API, including model ID, contents, and any configuration or tools.
- `generation_response_handling`: a concise description of how the assistant processed the response (e.g., which part contained the image, whether thought summaries were extracted, and any grounding metadata).
- `final_image`: a handle or reference to the generated image (e.g., file name or data URL). If the response includes only a reference (such as file data), specify the URI.

## Stop Conditions

Stop when: all sections of the seed page have been chunked; all required linked pages (Image Understanding and Thinking) have been included; the knowledge base JSON is complete and indexed; and the downstream assistant spec is fully defined.