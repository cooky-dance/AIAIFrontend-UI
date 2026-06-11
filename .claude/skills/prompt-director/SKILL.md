---
name: prompt-director
description: Generate stable image and video prompts from project, character, scene, style, usage, camera, action, emotion, lighting, and aspect ratio inputs for the AI short-film creative console.
---

# Prompt Director

Use this Skill when the user needs a reusable prompt package for image generation, video generation, or storyboard planning.

## Inputs

- `project`: project name, worldbuilding, goal, target ratio, and visual style.
- `character`: name, appearance, clothing, personality, keywords, forbidden traits, and reference image notes.
- `scene`: setting, action context, props, and environment.
- `style`: visual style, colors, lighting, composition, rendering type, and constraints.
- `usage`: `image`, `video`, or `storyboard`.
- `aspectRatio`: for example `9:16`, `16:9`, `21:9`, or `1:1`.
- `emotion`: expression and mood.
- `action`: body movement or dramatic action.
- `camera`: shot size, angle, lens feeling, and camera movement.
- `lighting`: time of day, source direction, contrast, atmosphere, and color temperature.

## Outputs

- `imagePrompt`: image-generation prompt.
- `videoPrompt`: video-generation prompt.
- `negativePrompt`: constraints and failure prevention terms.
- `styleTags`: compact reusable style tags.
- `providerSuggestion`: suggested provider such as `manual`, `openai-image`, `seedance2`, or `browser`.

## Rules

1. Preserve character identity before adding style flourishes.
2. Describe visible entities, camera, composition, lighting, and action before abstract mood words.
3. Keep role identity, clothing, face traits, and forbidden changes explicit.
4. Avoid mixing too many styles in one prompt.
5. For image prompts, prioritize subject clarity, composition, lighting, and background complexity.
6. For video prompts, include action, camera movement, rhythm, continuity, and negative constraints.
7. When reusing a high-scoring prompt, preserve the source `run_id`.
8. If a prompt is based on a failed run, mark it as an avoidance pattern, not a reusable template.

## Prompt Package Template

```text
Image Prompt:
[subject and identity], [appearance], [clothing], [pose/action], [scene], [camera], [lighting], [style], [aspect ratio]

Video Prompt:
[duration and aspect ratio]. [opening frame]. [character action]. [camera movement]. [lighting/environment change]. [rhythm]. Keep [identity/clothing/style] consistent.

Negative Prompt:
text, watermark, logo, distorted face, extra limbs, inconsistent clothing, style drift, unwanted character changes

Style Tags:
[style keyword], [color], [lighting], [composition]

Provider Suggestion:
[manual | openai-image | seedance2 | browser]
```
