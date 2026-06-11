---
name: seedance2-video-prompt
description: Convert image prompts or first-frame references into Seedance2-ready video prompts with duration, action, camera movement, rhythm, continuity, and negative constraints.
---

# Seedance2 Video Prompt

Use this Skill when converting a still image, image prompt, or scene idea into a Seedance2 video prompt.

## Required Prompt Elements

1. Duration.
2. Aspect ratio.
3. Character action.
4. Expression change.
5. Camera movement.
6. Lighting change.
7. Environment change.
8. Rhythm.
9. Negative constraints.

## Recommended Structure

```text
Duration / Aspect:

0-3s:
Establish the frame, character pose, environment, and lighting.

3-7s:
Begin the main character action and expression change.

7-11s:
Continue motion, camera movement, and environmental response.

11-15s:
Resolve motion and settle the camera.

Continuity constraints:

Negative constraints:
```

## Rules

1. Do not add too many characters.
2. Do not ask for frequent hard cuts unless the user explicitly wants editing.
3. Keep face, clothing, accessories, and body proportions stable.
4. Use smooth camera language: slow push-in, slight orbit, handheld drift, crane up, pan, tilt, or dolly.
5. Keep video prompts concrete: action, timing, camera, light, environment.
6. Include "no text, no watermark, no logo" unless the user asks for typography.
7. If using an input image, describe how the image should move rather than redesigning it.
8. For API integration, preserve `inputImageUrl`, `duration`, `aspectRatio`, and source `run_id` in metadata.

## Provider Notes

Seedance2 tasks are expected to be async. Provider adapters should expose `createTask` and `getTask`, with statuses `pending`, `running`, `succeeded`, and `failed`.
