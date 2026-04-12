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


Reality (Image / UI / Chart)
↓
VisualStructure ← this repository
↓
Markdown
↓
LLM / RAG / Analysis


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

## Metrics (v0.1)

- Layout Entropy (LE)
- Attention Gradient (AG)
- Element Density (ED)
- Contrast Signal (CS)
- Hierarchy Clarity (HC)
- Flow Directionality (FD)
- Occlusion Risk (OR)
- Friction Signal (FS)

---

## Output Format

VisualStructure produces structured data:

```json
{
  "elements": [],
  "relations": [],
  "visual_metrics": {}
}
Example

See examples/ui_example.png

Planned output:

detected UI elements
layout structure
friction estimation
Directory Structure
visual-structure/
├── visual_structure/
│   ├── analyzer.py
│   ├── metrics.py
│   └── schema.py
├── examples/
│   └── ui_example.png
├── tests/
├── README.md
Design Principles
Separation of observation and interpretation
Structure before language
Metrics over description
Minimal assumptions
Status
Specification: defined
Metrics: partially implemented
Extraction: minimal / experimental
Next Steps
implement basic element detection
compute initial metrics (LE, ED, AG)
validate against simple UI samples
Relation to Other Layers

VisualStructure is intended to connect with:

Markdown translation layers (e.g. MarkItDown)
TranslatedVoice (translation quality evaluation)
LoPAS (structural meaning analysis)
License

TBD

