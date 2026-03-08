# Gemini Video Generation Knowledge Base (Veo)

## A) SOURCE MANIFEST

- **Seed URL:** `https://ai.google.dev/gemini-api/docs/video`
- **Followed URLs:** No additional ai.google.dev pages were required beyond the seed page. All necessary details (models, parameters, limits, request/response formats, prompt‑writing guidance, etc.) were contained on the seed page itself. Tabs for different model versions were viewed within the same page to capture their contents.
- **Coverage statement:** Every section of the seed page was reviewed and converted into atomic knowledge chunks, including the introduction, text‑to‑video and image‑to‑video examples, aspects of controlling aspect ratio and resolution, using reference images, first/last frames, video extension, asynchronous operation handling, parameter tables, the Veo prompt guide (prompt writing basics, audio, reference images, extension, examples, negative prompts, aspect ratios), limitations, model features and versions, and other notes. No off‑domain pages were consulted.

## B) KNOWLEDGE PACK — JSON

```json
{
  "kb_id": "gemini_video_generation__ai_google_dev__v1",
  "source_domain": "ai.google.dev",
  "seed_url": "https://ai.google.dev/gemini-api/docs/video",
  "generated_at": "2026-03-06T05:50:43Z",
  "chunks": [
    {
      "chunk_id": "VIDGEN__001",
      "title": "Veo overview and features",
      "category": "overview",
      "summary": "Introduces Veo 3.1, Google’s state‑of‑the‑art video‑generation model. It produces up to eight‑second high‑fidelity videos at 720p, 1080p or 4K with native audio and realistic motion. New features include portrait videos (16:9 or 9:16), video extension, the ability to specify first and last frames, and using up to three reference images to preserve subject appearance. A Veo prompt guide provides strategies for effective prompting.",
      "tags": ["veo", "overview", "features"],
      "key_terms": ["Veo 3.1", "portrait video", "video extension", "first frame", "last frame", "reference images"],
      "content": "Veo 3.1 is Google’s generative model for video creation within the Gemini API. It can generate high‑fidelity videos up to eight seconds long with native audio at 720p, 1080p or 4K. New capabilities include portrait orientation (16:9 or 9:16), the ability to extend existing Veo videos, specifying the first and last frames to guide the interpolation of motion, and using up to three reference images to preserve subject appearance. A companion prompt guide offers techniques for writing clear, descriptive prompts and leveraging these features effectively【85533995214274†screenshot】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/video", "section": "Introduction and features"}
      ]
    },
    {
      "chunk_id": "VIDGEN__002",
      "title": "Model names and availability",
      "category": "models",
      "summary": "Lists the Veo model identifiers and distinguishes between preview and stable versions. Models include Veo 3.1 Preview (`veo-3.1-generate-preview`), Veo 3.1 Fast Preview (`veo-3.1-fast-generate-preview`), Veo 3 & 3 Fast (stable), and Veo 2 (`veo-2.0-generate-001`).",
      "tags": ["models", "version", "identifiers"],
      "key_terms": ["veo-3.1-generate-preview", "veo-3.1-fast-generate-preview", "veo-3-generate", "veo-3-fast", "veo-2.0-generate-001"],
      "content": "Veo video generation is available through several model versions: \n- **Veo 3.1 Preview** (Gemini API model ID `veo-3.1-generate-preview`) and **Veo 3.1 Fast Preview** (`veo-3.1-fast-generate-preview`). These preview models support high‑resolution outputs, native audio and features such as reference images, first/last frames and video extension. \n- **Veo 3 & Veo 3 Fast** are stable models (IDs similar to `veo-3-generate` and `veo-3-fast-generate`) that support text‑to‑video and image‑to‑video but lack some preview features. \n- **Veo 2** (`veo-2.0-generate-001`) is an earlier stable model with lower resolution options and no native audio; it can generate one or two videos per request.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/video", "section": "Model versions table"}
      ]
    },
    {
      "chunk_id": "VIDGEN__003",
      "title": "Model features comparison",
      "category": "models",
      "summary": "Compares key features across Veo 3.1 (Preview/Fast), Veo 3 (Stable/Fast) and Veo 2 models, including audio support, input modalities, resolutions, frame rate, video duration, videos per request and status.",
      "tags": ["features", "comparison"],
      "key_terms": ["audio", "input modalities", "resolution", "frame rate", "duration", "videos per request"],
      "content": "The Veo models differ in several ways【491607075095337†screenshot】. \n- **Audio:** Veo 3.1 and Veo 3 generate videos with native audio by default. Veo 2 produces silent videos only. \n- **Input modalities:** Veo 3.1 accepts text, image, and video inputs (for extension); Veo 3 accepts text and image inputs; Veo 2 accepts text and image inputs. \n- **Resolution:** Veo 3.1 supports 720p, 1080p and 4K outputs (8‑second duration required for 1080p/4K). Veo 3 supports 720p and 1080p for 16:9 videos; Veo 2 supports 720p only. Video extension is limited to 720p. \n- **Frame rate:** All models produce 24 fps videos. \n- **Video duration:** Veo 3.1 allows 4‑, 6‑, or 8‑second videos (8 seconds required when using high resolutions, reference images or extension). Veo 3 produces 8‑second videos. Veo 2 supports 5–8‑second videos. \n- **Videos per request:** Veo 3.1 returns a single video per request; Veo 3 returns one video; Veo 2 can return one or two videos per request. \n- **Status:** Veo 3.1 models are preview; Veo 3 models are stable; Veo 2 is stable.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/video", "section": "Model features table"}
      ]
    },
    {
      "chunk_id": "VIDGEN__004",
      "title": "Model limits and data types",
      "category": "models",
      "summary": "Describes the supported input and output data types, token limits and output counts for different Veo model versions.",
      "tags": ["limits", "data types"],
      "key_terms": ["text input tokens", "image input size", "output videos"],
      "content": "Veo model versions have different input and output limits【545604046710969†screenshot】. \n- **Veo 3.1 Preview and Fast Preview:** The model code `veo-3.1-generate-preview` (and its fast variant) accepts text prompts up to 1,024 tokens and image inputs of any resolution and aspect ratio up to a 20 MB file size. It returns a single video with native audio. \n- **Veo 2:** Model `veo-2.0-generate-001` accepts text and image inputs. The image input can be any resolution and aspect ratio up to 20 MB. It can return one or two silent videos per request. The latest update noted on the page was April 2025【545604046710969†screenshot】.\nThese limits apply per request and help manage latency and resource usage.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/video", "section": "Model versions table"}
      ]
    },
    {
      "chunk_id": "VIDGEN__005",
      "title": "Endpoint and asynchronous workflow",
      "category": "endpoint",
      "summary": "Explains how to call the Gemini API to generate videos and the asynchronous nature of the operation.",
      "tags": ["generate_videos", "operation"],
      "key_terms": ["client.models.generate_videos", "operation", "client.operations.get", "client.files.download"],
      "content": "Videos are generated by calling the `generate_videos` method on a `models` client and specifying the model ID (for example, `veo-3.1-generate-preview`). The request returns an asynchronous `operation` object. You must poll the operation using `client.operations.get(operation)` until `operation.done` is true. Once the operation completes, download the video using `client.files.download` and save it locally【761280940192900†screenshot】. This pattern applies to text‑to‑video, image‑to‑video, reference image and extension requests.",
      "code_blocks": [
        {"language": "python", "code": "# Example for text‑to‑video generation\noperation = client.models.generate_videos(model=\"veo-3.1-generate-preview\", prompt=\"a red convertible driving along the coast\")\n# Poll until complete\nwhile not operation.done:\n    time.sleep(10)\n    operation = client.operations.get(operation.name)\n# Download the result\ngenerated_video = client.files.download(name=operation.response.generated_videos[0].video.uri)\ngenerated_video.video.save(\"generated_video.mp4\")" }
      ],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/video", "section": "Text to video generation"},
        {"url": "https://ai.google.dev/gemini-api/docs/video", "section": "Handling asynchronous operations"}
      ]
    },
    {
      "chunk_id": "VIDGEN__006",
      "title": "Request parameters overview",
      "category": "request_schema",
      "summary": "Lists the primary fields used when generating videos with Veo models and notes which models support each field.",
      "tags": ["parameters", "request"],
      "key_terms": ["prompt", "image", "lastFrame", "referenceImages", "video", "aspectRatio", "durationSeconds", "resolution", "personGeneration", "seed"],
      "content": "Veo requests accept several parameters【79797101204587†screenshot】【448419994498067†screenshot】. \n- **prompt (string):** Required for all models. The descriptive text used to generate the video. \n- **image (Image object):** Provides an initial frame for image‑to‑video generation and must be paired with `prompt`. Supported by all models; the image file can be any resolution and aspect ratio up to 20 MB. \n- **lastFrame (Image object):** A final image used for interpolation together with `image`. Supported only by Veo 3.1 models. \n- **referenceImages (array of `VideoGenerationReferenceImage`):** Up to three images to guide the subject or style of the generated video. Supported only by Veo 3.1 models. Each reference must specify a `reference_type` such as `asset` (for subject appearance). \n- **video (Video object):** A previously generated Veo video used for extension. Supported only by Veo 3.1 models. \n- **aspectRatio (string):** Chooses between `\"16:9\"` (widescreen) and `\"9:16\"` (portrait). 16:9 is the default. \n- **durationSeconds (integer):** Determines the length of the output video. Veo 3.1 supports values 4, 6 or 8. For Veo 2 the allowed values are 5, 6 or 8. When using reference images, 1080p/4K resolution or extension, the duration must be 8 seconds. \n- **resolution (string):** Sets the output resolution; valid options for Veo 3.1 are `\"720p\"`, `\"1080p\"` and `\"4k\"`. Video extension always uses `\"720p\"`. Veo 3 supports 720p and 1080p for 16:9 orientation; Veo 2 supports 720p. \n- **personGeneration (string):** Controls generation of people. For Veo 3.1 text‑to‑video and extension, only `allow_all` is permitted; for image‑to‑video `allow_adult` is required. Veo 3 models support `allow_all` or `allow_adult` depending on input type, while Veo 2 also allows `dont_allow`. Regional restrictions may override the default values. \n- **seed (integer):** Optional parameter for Veo 3 models to slightly improve determinism; it does not guarantee identical outputs.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/video", "section": "Veo API parameters and specifications"}
      ]
    },
    {
      "chunk_id": "VIDGEN__007",
      "title": "Response structure and downloading videos",
      "category": "response_schema",
      "summary": "Describes how generated videos are returned and how to extract the content.",
      "tags": ["response", "operation", "download"],
      "key_terms": ["generated_videos", "video", "uri", "audio"],
      "content": "A `generate_videos` call returns an asynchronous `operation` containing a `response` field once the operation is done. The response includes a `generated_videos` list. Each entry has a `video` object with a `uri` pointing to the video file. For Veo 3.1 and Veo 3, the video includes native audio. Download the file using `client.files.download(name=uri)` and save it as an MP4 or other supported format【761280940192900†screenshot】. When the model returns more than one video (only possible with Veo 2), multiple items appear in the list.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/video", "section": "Handling asynchronous operations"}
      ]
    },
    {
      "chunk_id": "VIDGEN__008",
      "title": "Prompt writing basics",
      "category": "parameters",
      "summary": "Outlines the key elements of an effective video prompt, focusing on clarity and descriptive detail.",
      "tags": ["prompt", "guidelines"],
      "key_terms": ["subject", "action", "style", "camera positioning", "composition", "focus", "ambiance"],
      "content": "Good prompts are descriptive and clear. The Veo prompt guide suggests identifying: \n1. **Subject:** the main object, person or scene. \n2. **Action:** what the subject is doing. \n3. **Style:** keywords such as cinematic, sci‑fi, horror, vintage, 3D, realistic or hand‑drawn. \n4. **Camera positioning and motion:** specify the viewpoint (e.g., close‑up, wide shot, aerial view) and camera movement (e.g., panning, dolly, zoom). \n5. **Composition:** how subjects are arranged (e.g., rule of thirds, symmetrical, establishing shot). \n6. **Focus and lens effects:** mention shallow depth of field, macro lens, or bokeh to influence focus. \n7. **Ambiance:** describe lighting, color palette and mood, using modifiers like warm, cool, moody, overcast, golden hour or neon lights. \nAdjectives and adverbs enrich the prompt, and emphasising facial features can enhance realism【912557339125341†screenshot】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/video", "section": "Prompt writing basics"}
      ]
    },
    {
      "chunk_id": "VIDGEN__009",
      "title": "Prompting for audio",
      "category": "parameters",
      "summary": "Provides guidelines for including audio in Veo prompts.",
      "tags": ["audio", "prompt"],
      "key_terms": ["dialogue", "sound effects", "ambient noise"],
      "content": "Veo 3.1 and Veo 3 generate audio alongside video. To include specific audio, incorporate it into the text prompt: \n- **Dialogue:** Use quotes and identify the speaker (e.g., ‘This must be the key,’ he murmured). \n- **Sound effects:** Explicitly describe sounds to be heard (e.g., tires screeching loudly, engine roaring). \n- **Ambient noise:** Describe the environmental soundscape, such as a faint hum or birds chirping【890118170830943†screenshot】. \nAudio cannot be effectively extended if it is not present in the last second of the original video when using the extension feature【901116331375751†screenshot】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/video", "section": "Prompting for audio"}
      ]
    },
    {
      "chunk_id": "VIDGEN__010",
      "title": "Prompting with reference images",
      "category": "parameters",
      "summary": "Explains how to use reference images to guide content and style in video generation.",
      "tags": ["reference images", "guidance"],
      "key_terms": ["referenceImages", "asset", "preserve appearance", "up to three"],
      "content": "Veo 3.1 models allow up to three reference images. Provide images that closely match the desired subject, character or product. Reference images act as anchors for content and style. When the images depict a single person, character or object, Veo preserves the subject’s appearance in the resulting video. A reference image can be a still generated by Nano Banana or any other source. The prompt should describe the scene and the reference images should be passed in the `referenceImages` field (each with `reference_type=\"asset\"`)【790540161119884†screenshot】. Multiple reference images can be combined to create a hybrid subject (e.g., mixing a fish and a costume)【193398159321245†screenshot】.",
      "code_blocks": [
        {"language": "python", "code": "# Use reference images for Veo 3.1\nrefs = [types.VideoGenerationReferenceImage(image=asset1, reference_type=\"asset\"),\n        types.VideoGenerationReferenceImage(image=asset2, reference_type=\"asset\"),\n        types.VideoGenerationReferenceImage(image=asset3, reference_type=\"asset\")]\noperation = client.models.generate_videos(\n    model=\"veo-3.1-generate-preview\",\n    prompt=\"A cinematic video combining attributes from the reference images\",\n    image=initial_image,\n    config=types.GenerateVideosConfig(reference_images=refs))" }
      ],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/video", "section": "Prompting with reference images"}
      ]
    },
    {
      "chunk_id": "VIDGEN__011",
      "title": "Prompting with first and last frames",
      "category": "parameters",
      "summary": "Shows how to guide the beginning and ending of a video by specifying both an initial image and a final frame.",
      "tags": ["first frame", "last frame", "interpolation"],
      "key_terms": ["image", "lastFrame", "interpolation"],
      "content": "For Veo 3.1, you can define both the starting frame (`image`) and the ending frame (`lastFrame`) to control how the model interpolates motion between them【193398159321245†screenshot】. The initial image sets the opening shot and the last frame defines the closing shot; the model animates the transition. Use generated or real images for these frames. This feature is especially useful for storyboard‑like control or ensuring a dramatic finish.",
      "code_blocks": [
        {"language": "python", "code": "# Specify both first and last frames\noperation = client.models.generate_videos(\n    model=\"veo-3.1-generate-preview\",\n    prompt=\"Show how the cat drives off a cliff\",\n    image=first_image,\n    config=types.GenerateVideosConfig(last_frame=last_image))" }
      ],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/video", "section": "Prompting with first and last frames"}
      ]
    },
    {
      "chunk_id": "VIDGEN__012",
      "title": "Prompting for video extension",
      "category": "parameters",
      "summary": "Describes how to extend an existing Veo video and the associated limitations.",
      "tags": ["extension", "video", "prompt"],
      "key_terms": ["video", "durationSeconds=8", "extension limit", "number_of_videos"],
      "content": "Veo 3.1 can extend previously generated Veo videos by adding up to seven seconds of footage. To extend a video, supply the existing video (a `Video` object from a prior generation) and an optional prompt describing the continuation. Extensions can be chained up to twenty times, but only videos up to 141 seconds can be extended. Extensions always use a 720p resolution and require the aspect ratio to remain 16:9 or 9:16. The original video must have been generated within the past two days; each extension resets this timer. Video audio cannot be extended unless it exists in the final second of the original clip【901116331375751†screenshot】. When using extension, the `durationSeconds` value must be 8 and `number_of_videos` must be 1【640496714350053†screenshot】. The code uses `video` in `generate_videos` and a `GenerateVideosConfig` with optional options【602159867340591†screenshot】.",
      "code_blocks": [
        {"language": "python", "code": "# Extend a Veo video\nprev_video = previous_operation.response.generated_videos[0].video\noperation = client.models.generate_videos(\n    model=\"veo-3.1-generate-preview\",\n    prompt=\"Extend this video with the paraglider soaring above the mountains\",\n    video=prev_video,\n    config=types.GenerateVideosConfig(duration_seconds=8, resolution=\"720p\", number_of_videos=1))" }
      ],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/video", "section": "Prompting for extension"},
        {"url": "https://ai.google.dev/gemini-api/docs/video", "section": "Extending Veo videos"}
      ]
    },
    {
      "chunk_id": "VIDGEN__013",
      "title": "Negative prompts",
      "category": "parameters",
      "summary": "Explains how to specify elements that should not appear in the video.",
      "tags": ["negative prompt", "prompt guidance"],
      "key_terms": ["negative prompts"],
      "content": "You can include a `negative_prompt` in the configuration to describe elements to avoid. Negative prompts list undesirable objects or attributes without using instructive phrases like ‘no’ or ‘don’t’【224751725226328†screenshot】. For example, to prevent an urban background, include ‘urban background, man‑made structures’ in the negative prompt. This helps the model omit unwanted features while preserving the rest of the scene【385730118906386†screenshot】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/video", "section": "Negative prompts"}
      ]
    },
    {
      "chunk_id": "VIDGEN__014",
      "title": "Aspect ratio choices",
      "category": "parameters",
      "summary": "Describes how to set the video’s aspect ratio and provides examples for widescreen and portrait formats.",
      "tags": ["aspect ratio", "format"],
      "key_terms": ["aspectRatio", "16:9", "9:16"],
      "content": "Veo supports two aspect ratios: `16:9` (widescreen) and `9:16` (portrait). Widescreen videos are well suited for landscape scenes and cinematic shots; portrait videos emphasise vertical content such as waterfalls or tall subjects. Specify the ratio using the `aspectRatio` field (e.g., `GenerateVideosConfig(aspect_ratio=\"9:16\")`)【456505805704996†screenshot】. The prompt should still describe the scene clearly; the aspect ratio does not alter content but changes framing.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/video", "section": "Aspect ratios"}
      ]
    },
    {
      "chunk_id": "VIDGEN__015",
      "title": "Prompt examples and best practices",
      "category": "examples",
      "summary": "Illustrates the difference between basic and detailed prompts and demonstrates how descriptive elements improve video quality.",
      "tags": ["examples", "prompt"],
      "key_terms": ["melting icicles", "man on the phone", "snow leopard", "writing elements"],
      "content": "The prompt guide offers several examples: \n- **Melting icicles:** A close‑up shot of melting icicles on a frozen rock wall with cool blue tones and water drips demonstrates how to combine composition (close up), subject (icicles), context (rock wall), ambiance (cool tones) and camera motion (zoom)【718706837767896†screenshot】. \n- **Man on the phone:** A comparison shows how a generic prompt (‘close‑up of a desperate man on a rotary phone’) yields a basic result, whereas a detailed prompt describing his trench coat, brick wall, green neon light, camera dolly and shallow depth of field produces a richer, more cinematic video【834071018032489†screenshot】. \n- **Snow leopard:** A detailed prompt for a 3D animated scene of a snow‑leopard‑like creature in a whimsical winter forest emphasises style, movement, lighting and tone, resulting in a joyful cartoon video【277309617018927†screenshot】. \nThese examples highlight the importance of specificity in subjects, actions, style, camera movement, composition and mood.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/video", "section": "Example prompts and output"}
      ]
    },
    {
      "chunk_id": "VIDGEN__016",
      "title": "Writing elements examples",
      "category": "examples",
      "summary": "Provides targeted examples illustrating individual writing elements such as action, style, camera motion and ambiance.",
      "tags": ["writing elements", "examples"],
      "key_terms": ["action", "style", "camera motion", "composition", "ambiance"],
      "content": "The guide supplies examples focusing on specific writing elements: \n- **Action:** A wide shot of a woman walking along the beach at sunset shows how to describe the subject’s movement and surroundings【490439455896944†screenshot】. \n- **Style:** Adding keywords such as ‘film noir’ directs the aesthetic of the generation; for instance, a man and woman walking on the street can be rendered in black and white with a mysterious vibe【798777389313287†screenshot】. \n- **Camera motion and composition:** Examples include a POV shot from a vintage car driving through a city at night, an extreme close‑up of an eye reflecting a cityscape, and other shots that emphasise lens choice and framing【559650837097209†screenshot】. \n- **Ambiance:** Describing lighting and colors—such as natural light, sunrise, cool blue tones or neon—sets the mood. A prompt like ‘a girl holding an adorable golden retriever puppy in the park, sunlight’ illustrates how ambiance influences the result【559650837097209†screenshot】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/video", "section": "Examples by writing elements"}
      ]
    },
    {
      "chunk_id": "VIDGEN__017",
      "title": "Limitations and safety considerations",
      "category": "limits",
      "summary": "Summarises latency, regional restrictions, retention policy, watermarking and safety filters applied to Veo.",
      "tags": ["limits", "safety", "retention"],
      "key_terms": ["latency", "regional limitations", "retention", "SynthID watermark", "safety filters"],
      "content": "Several important limitations apply to Veo【473122558967371†screenshot】. \n- **Latency:** Requests take at least 11 seconds and may take up to 6 minutes during peak hours. \n- **Regional restrictions:** In the EU, UK, Switzerland and MENA region, `personGeneration` defaults to `dont_allow` for Veo 2 and `allow_adult` for Veo 3.1; only the allowed values may be used. \n- **Retention:** Generated videos are stored on the server for two days. You must download the file within this window to keep a local copy; each extension resets the two‑day timer. \n- **Watermarking:** All Veo videos are watermarked using SynthID to indicate they were AI‑generated. The watermark can be verified using the SynthID verification platform. \n- **Safety filters:** The model uses safety and memorization checks to reduce privacy, copyright and bias risks. Requests that fail safety checks (including audio issues) return an error and are not billed【473122558967371†screenshot】. \nThese limitations affect how developers manage video lifecycles, region compliance and prompt content.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/video", "section": "Limitations"}
      ]
    },
    {
      "chunk_id": "VIDGEN__018",
      "title": "Image‑to‑video and reference workflow",
      "category": "workflows",
      "summary": "Describes the steps to generate a video from an image and use the result as a reference for video generation.",
      "tags": ["image-to-video", "reference workflow"],
      "key_terms": ["generate videos", "Nano Banana", "reference image workflow"],
      "content": "A common workflow is to first generate a still image using the Nano Banana image model (e.g., `gemini-2.5-flash-image`) and then use that image as input for Veo. The Python example uses `client.models.generate_content` to generate the image, then passes `image.parts[0].as_image()` as the `image` parameter to `generate_videos` with the Veo model. The response is polled asynchronously and downloaded once complete【611924109525223†screenshot】. This technique allows iterative refinement by creating reference images that convey the desired subject and style before animating them.",
      "code_blocks": [
        {"language": "python", "code": "# Generate an image using Nano Banana\nimage_operation = client.models.generate_content(model=\"gemini-2.5-flash-image\", contents=[{\"text\": \"A realistic cat driving a red convertible on the French Riviera\"}])\nimage = image_operation.response.parts[0].as_image()\n# Use the image as an initial frame for Veo\nvideo_operation = client.models.generate_videos(\n    model=\"veo-3.1-generate-preview\",\n    prompt=\"Animate the cat driving along the coast\",\n    image=image)" }
      ],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/video", "section": "Image to video generation"}
      ]
    },
    {
      "chunk_id": "VIDGEN__019",
      "title": "Regional and person generation policy",
      "category": "constraints",
      "summary": "Details how person generation policies vary by region and model.",
      "tags": ["personGeneration", "policy"],
      "key_terms": ["allow_all", "allow_adult", "dont_allow", "regional"],
      "content": "The `personGeneration` parameter controls whether people can appear in generated videos. For Veo 3.1 text‑to‑video and extension requests, the value must be `allow_all`; for image‑to‑video, `allow_adult` is required. Veo 3 models generally allow `allow_all` or `allow_adult` depending on input type. Veo 2 supports three values: `allow_all`, `allow_adult` and `dont_allow`. Regional regulations override these defaults: in the EU, UK, Switzerland and MENA, `dont_allow` is enforced for Veo 2 and `allow_adult` for Veo 3.1【448419994498067†screenshot】【473122558967371†screenshot】.",
      "code_blocks": [],
      "citations": [
        {"url": "https://ai.google.dev/gemini-api/docs/video", "section": "Veo API parameters and specifications"},
        {"url": "https://ai.google.dev/gemini-api/docs/video", "section": "Limitations"}
      ]
    }
  ],
  "index": {
    "by_category": {
      "overview": ["VIDGEN__001"],
      "models": ["VIDGEN__002", "VIDGEN__003", "VIDGEN__004"],
      "endpoint": ["VIDGEN__005"],
      "request_schema": ["VIDGEN__006"],
      "response_schema": ["VIDGEN__007"],
      "parameters": ["VIDGEN__006", "VIDGEN__008", "VIDGEN__009", "VIDGEN__010", "VIDGEN__011", "VIDGEN__012", "VIDGEN__013", "VIDGEN__014"],
      "formats": [],
      "constraints": ["VIDGEN__012", "VIDGEN__017", "VIDGEN__019"],
      "limits": ["VIDGEN__017"],
      "safety": ["VIDGEN__017"],
      "errors": [],
      "examples": ["VIDGEN__015", "VIDGEN__016"],
      "workflows": ["VIDGEN__005", "VIDGEN__018"]
    },
    "by_tag": {
      "veo": ["VIDGEN__001"],
      "overview": ["VIDGEN__001"],
      "features": ["VIDGEN__001"],
      "models": ["VIDGEN__002", "VIDGEN__003"],
      "version": ["VIDGEN__002"],
      "identifiers": ["VIDGEN__002"],
      "comparison": ["VIDGEN__003"],
      "limits": ["VIDGEN__004", "VIDGEN__017"],
      "data types": ["VIDGEN__004"],
      "generate_videos": ["VIDGEN__005"],
      "operation": ["VIDGEN__005"],
      "parameters": ["VIDGEN__006"],
      "request": ["VIDGEN__006"],
      "response": ["VIDGEN__007"],
      "prompt": ["VIDGEN__008", "VIDGEN__009", "VIDGEN__012", "VIDGEN__013", "VIDGEN__014", "VIDGEN__015"],
      "guidelines": ["VIDGEN__008"],
      "audio": ["VIDGEN__009"],
      "reference images": ["VIDGEN__010"],
      "guidance": ["VIDGEN__010"],
      "first frame": ["VIDGEN__011"],
      "last frame": ["VIDGEN__011"],
      "interpolation": ["VIDGEN__011"],
      "extension": ["VIDGEN__012"],
      "negative prompt": ["VIDGEN__013"],
      "aspect ratio": ["VIDGEN__014"],
      "format": ["VIDGEN__014"],
      "examples": ["VIDGEN__015", "VIDGEN__016"],
      "writing elements": ["VIDGEN__016"],
      "safety": ["VIDGEN__017"],
      "retention": ["VIDGEN__017"],
      "image-to-video": ["VIDGEN__018"],
      "reference workflow": ["VIDGEN__018"],
      "personGeneration": ["VIDGEN__019"],
      "policy": ["VIDGEN__019"]
    },
    "by_key_term": {
      "Veo 3.1": ["VIDGEN__001", "VIDGEN__002", "VIDGEN__003", "VIDGEN__004", "VIDGEN__006", "VIDGEN__008", "VIDGEN__009", "VIDGEN__010", "VIDGEN__011", "VIDGEN__012", "VIDGEN__019"],
      "portrait video": ["VIDGEN__001"],
      "video extension": ["VIDGEN__001", "VIDGEN__012"],
      "first frame": ["VIDGEN__001", "VIDGEN__011"],
      "last frame": ["VIDGEN__001", "VIDGEN__011"],
      "reference images": ["VIDGEN__001", "VIDGEN__006", "VIDGEN__010"],
      "veo-3.1-generate-preview": ["VIDGEN__002", "VIDGEN__005", "VIDGEN__018"],
      "veo-3.1-fast-generate-preview": ["VIDGEN__002"],
      "veo-3-generate": ["VIDGEN__002"],
      "veo-2.0-generate-001": ["VIDGEN__002", "VIDGEN__004"],
      "generate_videos": ["VIDGEN__005"],
      "client.operations.get": ["VIDGEN__005"],
      "client.files.download": ["VIDGEN__005"],
      "prompt": ["VIDGEN__006", "VIDGEN__008", "VIDGEN__009", "VIDGEN__010", "VIDGEN__012", "VIDGEN__013", "VIDGEN__014", "VIDGEN__015"],
      "image": ["VIDGEN__006", "VIDGEN__011", "VIDGEN__018"],
      "lastFrame": ["VIDGEN__006", "VIDGEN__011"],
      "referenceImages": ["VIDGEN__006", "VIDGEN__010"],
      "video": ["VIDGEN__006", "VIDGEN__012"],
      "aspectRatio": ["VIDGEN__006", "VIDGEN__014"],
      "durationSeconds": ["VIDGEN__006", "VIDGEN__012"],
      "resolution": ["VIDGEN__006"],
      "personGeneration": ["VIDGEN__006", "VIDGEN__019"],
      "seed": ["VIDGEN__006"],
      "generated_videos": ["VIDGEN__007"],
      "video with audio": ["VIDGEN__007", "VIDGEN__009"],
      "subject": ["VIDGEN__008", "VIDGEN__015", "VIDGEN__016"],
      "action": ["VIDGEN__008", "VIDGEN__016"],
      "style": ["VIDGEN__008", "VIDGEN__016"],
      "camera positioning": ["VIDGEN__008", "VIDGEN__016"],
      "composition": ["VIDGEN__008", "VIDGEN__016"],
      "focus": ["VIDGEN__008", "VIDGEN__016"],
      "ambiance": ["VIDGEN__008", "VIDGEN__016"],
      "dialogue": ["VIDGEN__009"],
      "sound effects": ["VIDGEN__009"],
      "ambient noise": ["VIDGEN__009"],
      "asset": ["VIDGEN__010"],
      "interpolation": ["VIDGEN__011"],
      "negative prompts": ["VIDGEN__013"],
      "16:9": ["VIDGEN__014"],
      "9:16": ["VIDGEN__014"],
      "latency": ["VIDGEN__017"],
      "regional limitations": ["VIDGEN__017", "VIDGEN__019"],
      "retention": ["VIDGEN__017"],
      "SynthID watermark": ["VIDGEN__017"],
      "safety filters": ["VIDGEN__017"],
      "Nano Banana": ["VIDGEN__018"],
      "allow_all": ["VIDGEN__019"],
      "allow_adult": ["VIDGEN__019"],
      "dont_allow": ["VIDGEN__019"]
    }
  }
}
```

## C) METADATA CATEGORIZATION BLUEPRINT (IA)

The following information architecture (IA) decisions govern how chunks are organized and retrieved.

### Category definitions

- **overview:** High‑level description of Veo video generation, model capabilities and overall context.
- **models:** Information about model identifiers, versions, feature comparisons and limits.
- **endpoint:** Details about API methods and how to call them.
- **request_schema:** Parameters and fields used in requests, including optional/required status.
- **response_schema:** Structure of the response and how to extract generated content.
- **parameters:** Deeper guidance on specific request fields (prompt writing, audio, reference images, first/last frames, extension, negative prompts, aspect ratios, person generation policies).
- **formats:** Reserved for any file‑format specifics (not used here because the docs do not define custom file formats).
- **constraints:** Conditions or policies that restrict usage (e.g., extension rules, region policies).
- **limits:** Quantitative limits such as latency, storage, file size and counts.
- **safety:** Safety‑related notes, including watermarking and filters. Safety is combined with limits because the docs overlap these topics.
- **errors:** Reserved for error handling; no explicit error codes were described, so this category remains empty.
- **examples:** Illustrative prompts and outputs to help users craft better prompts.
- **workflows:** Step‑by‑step sequences for common tasks (e.g., generating a video, using an image as a reference).

### Tagging rules

Tags are deterministic keywords used to aid retrieval. They include:
- **Model tags** such as `veo`, `models`, `version`, `identifiers`, `features`, `comparison`, `data types`.
- **Operation tags** like `generate_videos`, `operation`, `response`, `download` for call flow.
- **Parameter tags** (e.g., `prompt`, `audio`, `reference images`, `first frame`, `last frame`, `extension`, `negative prompt`, `aspect ratio`, `personGeneration`).
- **Example tags** (e.g., `examples`, `writing elements`).
- **Constraint and policy tags** (e.g., `limits`, `safety`, `retention`, `personGeneration`).

Rules:
1. Use the singular form (e.g., `example`) only when the concept appears as a tag; however, for clarity we used plural for categories like `examples`.
2. Always include at least one tag per chunk; include multiple tags when a chunk covers multiple aspects.
3. Tags correspond to recurring themes and user‑query terms; they should not include generic adjectives.

### Key term rules

Key terms capture exact identifiers, field names, model codes, enumerated values and other searchable phrases. Rules:
1. Include every API field (`prompt`, `image`, `lastFrame`, `referenceImages`, `video`, `aspectRatio`, `durationSeconds`, `resolution`, `personGeneration`, `seed`), method name (`generate_videos`), and response key (`generated_videos`).
2. Include model identifiers and version names (e.g., `veo-3.1-generate-preview`).
3. Include controlled vocabulary enumerations such as `16:9`, `9:16`, `allow_all`, etc.
4. Do not include explanatory phrases or synonyms.

### Chunk sizing rules (IA DECISION)

To support efficient retrieval, chunks are kept small and atomic:
1. Each chunk focuses on a single concept (one parameter, feature comparison, limitation, example category, etc.) and does not exceed approximately 2–3 paragraphs. This improves recall and avoids mixing unrelated information.
2. Code examples are kept within their related chunk and not separated unless they illustrate a different concept.
3. If a section contains both conceptual guidance and enumeration, split into separate chunks (e.g., prompt basics vs. examples).
4. When possible, group similar items (e.g., writing elements examples) to avoid creating too many tiny chunks.

### Retrieval patterns (IA DECISION)

When a user asks a question, the assistant should:
1. Identify the relevant category based on the query. For example, a request about allowed resolutions maps to the `parameters` or `limits` category.
2. Use tags and key terms to narrow down the chunks. If the question includes a specific field name or model ID, search the `by_key_term` index first; otherwise search by tags.
3. Retrieve all chunks whose tags and key terms match the query context. Combine information from multiple chunks if necessary.
4. Prefer chunks with specific citations when answering; avoid inventing information not present in the knowledge base.


## D) DOWNSTREAM ASSISTANT SPEC — “Video Prompt Refiner + Generator”

This specification defines an assistant that refines user intent into a Veo video generation request using the knowledge base above.

### 1) Input intake

The assistant accepts a natural‑language request describing the desired video. It should only ask follow‑up questions when essential details are missing and their absence would prevent assembling a valid Veo request. Required inputs include:
1. **Description (prompt):** A clear narrative of the desired video. If the description lacks critical elements such as subject, action or style, ask one concise clarifying question.
2. **Orientation and duration preferences:** If the user does not specify orientation (widescreen vs. portrait) or length, assume widescreen (`16:9`) and 6 seconds (the mid value) for Veo 3.1. Ask only when orientation or length is vital for the use case.
3. **Reference media:** When the user wants to preserve a particular subject or style, ask whether they can supply reference images or an initial frame. If they have an existing Veo video they wish to extend, ask for the video file.
4. **Region restrictions and person generation:** If generating videos containing people, verify whether restrictions apply (e.g., region or adult content) and set `personGeneration` accordingly.

### 2) Prompt refinement (doc‑anchored)

The assistant refines the user’s raw description into a detailed `refined_prompt` by:
1. **Identifying core elements:** Extract subject, action, style, camera positioning, composition, focus and ambiance from the user’s description. If any element is missing but important for visual clarity, augment it with generic yet vivid descriptors (e.g., specify lighting or camera motion) based on the guidance in the prompt writing basics【912557339125341†screenshot】.
2. **Respecting user intent:** Do not introduce new subjects or narrative elements. Only add descriptors that clarify the existing intent (IA DECISION).
3. **Audio specification:** Include dialogue, sound effects or ambient noise only if the user mentions them. Do not assume audio otherwise【890118170830943†screenshot】.
4. **Orientation and length:** Ensure the refined prompt is consistent with the chosen aspect ratio and duration; adjust composition descriptors accordingly (e.g., emphasize vertical elements for 9:16).
5. **Negative prompts:** If the user specifies undesired elements, add them to a `negative_prompt` list without using instructive language (‘no’, ‘don’t’)【224751725226328†screenshot】.

### 3) Request assembly (doc‑anchored)

Use the refined prompt and additional inputs to construct a valid request object as follows:

- **model:** Choose `veo-3.1-generate-preview` for preview features unless the user explicitly requests a different model or resolution/responsiveness trade‑off. If low latency is critical and high resolution isn’t required, use the fast model (`veo-3.1-fast-generate-preview`).
- **prompt:** Set to the `refined_prompt` string.
- **image (optional):** If the user provides an initial frame, include it here; otherwise omit.
- **lastFrame (optional):** Include when the user provides a final frame for interpolation.
- **referenceImages (optional):** Pass up to three reference images with `reference_type` set to `asset` for each【790540161119884†screenshot】.
- **video (optional):** If extending a Veo video, include the existing `video` object.
- **config:** Construct a `GenerateVideosConfig` with:  
  – `aspect_ratio`: either `"16:9"` or `"9:16"`.  
  – `duration_seconds`: 4, 6 or 8. Use 8 when using reference images, high resolutions (1080p/4K) or extension【79797101204587†screenshot】.  
  – `resolution`: choose `720p`, `1080p` or `4k` (for preview models) according to user needs; default to `720p`.  
  – `person_generation`: assign `allow_all`, `allow_adult` or `dont_allow` based on user preference and region【448419994498067†screenshot】.  
  – `number_of_videos`: set to 1; for Veo 2 the assistant may set 2 if multiple videos are desired.  
  – `negative_prompt`: include the list from the refinement step if any【224751725226328†screenshot】.  
  – `seed` (optional): provide if the user requests more deterministic outputs【448419994498067†screenshot】.

### 4) Response handling (doc‑anchored)

After submitting the request:
1. **Poll the operation:** Use `client.operations.get(operation)` until `operation.done` becomes true【761280940192900†screenshot】.
2. **Handle success:** Extract the first `video` from `operation.response.generated_videos`. Download the file using `client.files.download` with the video’s `uri` and save it locally【761280940192900†screenshot】. If the model returns multiple videos (Veo 2), loop through them.
3. **Handle audio:** When using preview models with audio, the downloaded file contains audio automatically. If the generation fails due to safety filters (for example, audio issues), return an error message to the user and note that the request was not billed【473122558967371†screenshot】.
4. **Store or extend video:** Remind the user that videos are stored on the server for only two days; encourage saving a local copy【473122558967371†screenshot】. If the user wants to extend the video further, the assistant should reuse the downloaded video as input for a subsequent request.

### 5) Output format

The assistant should output a structured object with the following keys:
```
{
  "original_prompt": <string from user>,
  "refined_prompt": <refined descriptive prompt>,
  "generation_request": {
    "model": <model ID>,
    "prompt": <refined_prompt>,
    "image": <optional image object>,
    "lastFrame": <optional image object>,
    "referenceImages": <list of reference image objects>,
    "video": <optional video object>,
    "config": {
      "aspect_ratio": <\"16:9\" or \"9:16\">,
      "duration_seconds": <integer>,
      "resolution": <\"720p\", \"1080p\" or \"4k\">,
      "person_generation": <\"allow_all\"|\"allow_adult\"|\"dont_allow\">,
      "number_of_videos": <integer>,
      "negative_prompt": <optional string>,
      "seed": <optional integer>
    }
  },
  "generation_response_handling": "Poll the operation until done; download the video(s) via client.files.download using the provided URI; handle safety errors appropriately; store locally within two days.",
  "final_video": "A handle or URI to the downloaded video file, included in the response"
}
```

## E) STOP CONDITIONS

Stop when: all sections of the seed page have been converted into atomic chunks; the knowledge pack JSON is complete and indexed; the metadata blueprint and downstream assistant spec are fully defined; and no off‑domain content has been included.