"""
Action Structure

A proposed extension to VisualStructure for dynamic behavior observation.

Treats motion as structural action events observed through a two-layer model:
  Frame Layer           — skeletal posture transitions
  Functional Endpoint   — discrete state changes at terminal nodes

Design Principle:
  Structure before trajectory. Function before full reconstruction.
  Observe at the layer appropriate to the function.

Status: proposed / experimental
"""

from .schema import (
    ActionElement,
    ActionRelation,
    ActionMetrics,
    ActionStructureData,
)

from .action_structure import (
    LAYER_FRAME,
    LAYER_ENDPOINT,
    LAYER_BOUNDARY,
    ActionSequence,
    ActionStructureAnalyzer,
    compute_grip_transition_signal,
    compute_action_flow_stability,
    compute_manipulation_friction,
    compute_action_branching_signal,
    compute_action_metrics,
    make_pick_and_place,
    make_desk_task,
)
