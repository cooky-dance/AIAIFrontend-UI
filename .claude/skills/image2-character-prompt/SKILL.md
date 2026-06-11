---
name: image2-character-prompt
description: Create stable Image API prompts for character reference images, preserving identity, clothing, proportions, lighting, and background control.
---

# Image2 Character Prompt

Use this Skill when generating or refining character reference images for the AI short-film workflow.

## Goal

Create stable character prompts that can be reused across projects and providers without losing core identity.

## Required Fields

- Subject
- Appearance
- Clothing
- Pose
- Expression
- Camera
- Lighting
- Background
- Rendering style
- Negative constraints

## Rules

1. Fix the character's core traits: hair, eyes, face shape, age range, body silhouette, clothing, and temperament.
2. Keep clothing and accessories stable unless the user explicitly asks for variants.
3. State the aspect ratio and framing clearly.
4. Specify shot distance such as bust shot, half body, full body, or character sheet.
5. Define lighting direction and intensity.
6. Keep the background simple when the purpose is character consistency.
7. Avoid long abstract adjective chains that make the subject drift.
8. Prevent background elements from competing with the character.
9. Include negative constraints for text, watermark, logo, face distortion, hand errors, clothing drift, and unwanted extra characters.

## Output Template

```text
Subject:

Appearance:

Clothing:

Pose:

Expression:

Camera:

Lighting:

Background:

Rendering style:

Negative constraints:
```

## Reuse Policy

Only mark a character prompt reusable after it appears in a reviewed `GenerationRun` with high identity and style scores. Preserve the source `run_id` whenever the prompt is reused.
