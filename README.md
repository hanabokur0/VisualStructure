# VisualStructure

VisualStructure is a layer that extracts measurable structure from visual inputs.

It is designed to operate before any Markdown translation layer.

---

## Purpose

Visual inputs (UI, charts, documents, whiteboards) contain structure that is lost when converted directly into text.

This repository defines a method to:

- extract visual structure
- represent it as structured data
- preserve it through downstream processing (e.g. Markdown, LLM)

---

## Layer Position

VisualStructure is not a translation tool.

It is a pre-translation observation layer.

```
Reality (Image / UI / Chart)
  ↓
VisualStructure        ← this repository
  ↓
Markdown
  ↓
LLM / RAG / Analysis
```

---

## Scope

This project focuses on:

- element extraction
- layout structure
- visual hierarchy
- attention distribution
- density and friction signals

It does NOT aim to:

- generate captions
- describe images for humans
- replace OCR or vision models

---

## Core Concepts

### Elements

Basic units detected in an image.

Examples:

- text
- button
- chart element
- icon
- node

---

### Structure

Relationships between elements.

Examples:

- grouping
- hierarchy
- adjacency
- flow

---

### Signals

Quantifiable properties derived from structure.

---

## Action Structure (Proposed)

VisualStructure may be extended to include Action Structure:

Action Structure treats motion not as raw high-dimensional trajectories,
but as structural action events observed through a two-layer model.

### Design Principle

Do not model all degrees of freedom when functional structure is sufficient.

**Structure before trajectory. Function before full reconstruction.**

This extends the existing VisualStructure principles
(separation of observation and interpretation; structure before language;
metrics over description; minimal assumptions)
into dynamic behavior.

---

### Two-Layer Model

Human action is observed through two distinct layers:

**Frame Layer** — The skeletal frame as a structural graph.
Posture transitions of the whole body are observed here.
Actions at this layer describe spatial movement of the frame,
not individual joint kinematics.

Examples: reach, approach, withdraw, lean, step

**Functional Endpoint Layer** — Terminal nodes (hands, feet, gaze)
where functional state matters more than frame posture.
These endpoints have discrete operational modes
that cannot be captured by frame transitions alone.

Examples: grasp, release, pinch, hold, rotate, contact, fixate

---

### Layer Interaction

An action sequence crosses between layers:

```
reach    → Frame Layer           (arm frame posture transition)
contact  → Boundary              (frame arrives at target)
grasp    → Functional Endpoint   (hand state change)
move     → Frame Layer           (frame transition; hand state held)
release  → Functional Endpoint   (hand state change)
```

The observation target shifts between layers during a single action chain.
This is the core structural insight:
the same sequence requires different observation modes at different phases.

---

### Action Elements

Frame Layer:

- reach
- approach
- withdraw
- lean
- step

Functional Endpoint Layer:

- contact
- grasp
- hold
- release
- pinch
- rotate

---

### Action Relations

- temporal sequence
- dependency
- branching conditions
- action flow transitions
- layer transitions (Frame ↔ Functional Endpoint)

---

### Action Metrics (Proposed)

- Grip Transition Signal (GTS) — state change frequency at functional endpoints
- Action Flow Stability (AFS) — smoothness of layer transitions in a sequence
- Manipulation Friction (MF) — resistance or complexity at functional endpoint operations
- Action Branching Signal (ABS) — decision density at branching points in action flow

---

### Relation to VisualStructure

```
Reality (Image / Motion / UI)
  ↓
VisualStructure
  - visual elements
  - structural relations
  - visual metrics
  - action structure (proposed)
    - frame layer
    - functional endpoint layer
    - action metrics
  ↓
Markdown / Protocol / LLM / Control
```

---

### Why This Fits Existing Scope

This extends, rather than changes, existing principles:

- Separation of observation and interpretation
- Structure before language
- Metrics over description
- Minimal assumptions

Action Structure applies those same principles to dynamic behavior,
with the added constraint: observe at the layer appropriate to the function.

---

### Potential Relevance

- imitation learning
- robotics abstraction
- task representation
- deskwork automation
- protocol extraction

---

## Metrics (v0.1)

### Visual Metrics

- Layout Entropy (LE)
- Attention Gradient (AG)
- Element Density (ED)
- Contrast Signal (CS)
- Hierarchy Clarity (HC)
- Flow Directionality (FD)
- Occlusion Risk (OR)
- Friction Signal (FS)

### Action Metrics (Proposed)

- Grip Transition Signal (GTS)
- Action Flow Stability (AFS)
- Manipulation Friction (MF)
- Action Branching Signal (ABS)

---

## Output Format

VisualStructure produces structured data:

```json
{
  "elements": [],
  "relations": [],
  "visual_metrics": {},
  "action_structure": {
    "frame_events": [],
    "endpoint_events": [],
    "action_sequence": [],
    "action_metrics": {}
  }
}
```

---

## Example

See `examples/ui_example.png`

Planned output:

- detected UI elements
- layout structure
- friction estimation

---

## Directory Structure

```
visual-structure/
├── visual_structure/
│   ├── analyzer.py
│   ├── metrics.py
│   ├── schema.py
│   └── action_structure.py   ← optional future module
├── examples/
│   └── ui_example.png
├── tests/
├── README.md
```

---

## Design Principles

- Separation of observation and interpretation
- Structure before language
- Metrics over description
- Minimal assumptions
- Structure before trajectory (Action Structure)
- Observe at the layer appropriate to the function (Action Structure)

---

## Status

- Specification: defined
- Visual Metrics: partially implemented
- Extraction: minimal / experimental
- Action Structure: proposed

---

## Next Steps

- implement basic element detection
- compute initial metrics (LE, ED, AG)
- validate against simple UI samples
- define action_structure schema (proposed)

---

## Relation to Other Layers

VisualStructure is intended to connect with:

- Markdown translation layers (e.g. MarkItDown)
- TranslatedVoice (translation quality evaluation)
- LoPAS (structural meaning analysis)

---

## License

TBD
