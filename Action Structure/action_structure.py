"""
action_structure.py

Action Structure module for VisualStructure.

Treats motion not as raw high-dimensional trajectories,
but as structural action events observed through a two-layer model:

  Frame Layer           — skeletal posture transitions (reach, approach, withdraw)
  Functional Endpoint   — discrete state changes at terminal nodes (grasp, release, contact)

The human body's skeleton is treated as a structural frame.
Most of the body is observed at the Frame Layer (posture transitions).
Hands (and other terminal nodes) are observed at the Functional Endpoint Layer,
because their operational modes (grasp, release, pinch, hold, rotate)
cannot be captured by frame transitions alone.

Design Principle:
  Structure before trajectory. Function before full reconstruction.
  Observe at the layer appropriate to the function.

Status: proposed / experimental
"""

from typing import List, Optional, Dict, Any

# Schema types — when used inside the visual_structure package:
#   from .schema import ActionElement, ActionRelation, ActionMetrics, ActionStructureData
#
# For standalone use (testing / development), copy schema.py alongside this file
# or use the inline definitions below.

try:
    from .schema import ActionElement, ActionRelation, ActionMetrics, ActionStructureData
except ImportError:
    from schema import ActionElement, ActionRelation, ActionMetrics, ActionStructureData


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LAYER_FRAME = "frame"
LAYER_ENDPOINT = "functional_endpoint"
LAYER_BOUNDARY = "boundary"


# ---------------------------------------------------------------------------
# Action sequence
# ---------------------------------------------------------------------------

class ActionSequence:
    """
    An ordered chain of ActionElements.

    Captures layer transitions within a single task unit.
    Example:
        reach (Frame) → contact (Boundary) → grasp (Endpoint)
        → move (Frame) → release (Endpoint)
    """

    def __init__(
        self,
        events: Optional[List[ActionElement]] = None,
        label: Optional[str] = None,
    ):
        self.events = events or []
        self.label = label

    def append(self, event: ActionElement) -> None:
        self.events.append(event)

    def layer_transitions(self) -> List[Dict[str, str]]:
        """
        Return list of layer transitions in the sequence.
        Each transition is {"from": layer, "to": layer}.
        """
        transitions = []
        for i in range(1, len(self.events)):
            prev = self.events[i - 1].layer
            curr = self.events[i].layer
            if prev != curr:
                transitions.append({"from": prev, "to": curr})
        return transitions

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "events": [e.to_dict() for e in self.events],
            "layer_transitions": self.layer_transitions(),
        }
        if self.label is not None:
            d["label"] = self.label
        return d


# ---------------------------------------------------------------------------
# Action metrics — individual compute functions
# ---------------------------------------------------------------------------
# Pattern follows metrics.py: one function per metric,
# then compute_action_metrics() calls them all.
# ---------------------------------------------------------------------------


def compute_grip_transition_signal(events: List[ActionElement]) -> float:
    """
    GTS — Grip Transition Signal.

    State change frequency at functional endpoints.
    Higher values indicate more complex manipulation.
    """
    if not events:
        return 0.0

    endpoint_count = sum(
        1 for e in events
        if e.layer == LAYER_ENDPOINT
    )
    return endpoint_count / len(events)


def compute_action_flow_stability(sequence: ActionSequence) -> float:
    """
    AFS — Action Flow Stability.

    Measures smoothness of layer transitions.
    1.0 = all adjacent events share the same layer (no transitions).
    Lower values = more frequent layer switching.
    """
    n = len(sequence.events)
    if n <= 1:
        return 1.0

    transitions = sequence.layer_transitions()
    max_possible = n - 1
    return 1.0 - (len(transitions) / max_possible)


def compute_manipulation_friction(events: List[ActionElement]) -> float:
    """
    MF — Manipulation Friction.

    Proportion of functional endpoint events in the sequence.
    Higher values indicate manipulation-heavy tasks
    (more hand/tool state changes relative to body movement).
    """
    if not events:
        return 0.0

    endpoint_count = sum(
        1 for e in events
        if e.layer == LAYER_ENDPOINT
    )
    return endpoint_count / len(events)


def compute_action_branching_signal(
    sequence: ActionSequence,
) -> Optional[float]:
    """
    ABS — Action Branching Signal.

    Decision density at branching points in action flow.
    Requires branching annotation in ActionElement.metadata["branches"].

    Returns None until branching metadata is available.
    """
    branching_events = [
        e for e in sequence.events
        if e.metadata.get("branches") is not None
    ]

    if not branching_events:
        return None

    total_branches = sum(
        len(e.metadata["branches"]) for e in branching_events
    )
    return total_branches / len(sequence.events)


def compute_action_metrics(sequence: ActionSequence) -> Dict[str, Any]:
    """
    Compute all proposed action metrics from a sequence.

    Follows the same aggregation pattern as metrics.compute_metrics().
    """
    events = sequence.events

    return {
        "grip_transition_signal": round(compute_grip_transition_signal(events), 4),
        "action_flow_stability": round(compute_action_flow_stability(sequence), 4),
        "manipulation_friction": round(compute_manipulation_friction(events), 4),
        "action_branching_signal": compute_action_branching_signal(sequence),
    }


# ---------------------------------------------------------------------------
# Analyzer
# ---------------------------------------------------------------------------

class ActionStructureAnalyzer:
    """
    Analyzer for extracting action structure from event sequences.

    Responsibilities:
    - receive pre-classified action events
    - separate into frame and functional endpoint layers
    - build action relations (temporal + layer transitions)
    - compute action metrics
    - return structured output

    This layer does NOT:
    - perform pose estimation
    - track joint kinematics
    - reconstruct full motion trajectories
    """

    def __init__(self):
        pass

    def analyze(
        self,
        events: List[ActionElement],
        label: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Main entry point.

        Args:
            events: list of ActionElement instances (pre-classified by layer)
            label:  optional label for the action sequence

        Returns:
            dict: structured action representation
        """
        # Build sequence
        sequence = ActionSequence(events=events, label=label)

        # Separate by layer
        frame_events = [e for e in events if e.layer == LAYER_FRAME]
        endpoint_events = [e for e in events if e.layer == LAYER_ENDPOINT]

        # Build relations
        relations = self._build_relations(events, sequence)

        # Compute metrics
        metrics = compute_action_metrics(sequence)

        # Build output
        output = ActionStructureData(
            frame_events=[e.to_dict() for e in frame_events],
            endpoint_events=[e.to_dict() for e in endpoint_events],
            action_sequence=sequence.to_dict(),
            action_metrics=metrics,
        )
        return output.to_dict()

    def _build_relations(
        self,
        events: List[ActionElement],
        sequence: ActionSequence,
    ) -> List[ActionRelation]:
        """
        Automatically generate relations from event order.

        Creates:
        - temporal relations between consecutive events
        - layer_transition relations where the layer changes
        """
        relations = []

        for i in range(1, len(events)):
            prev = events[i - 1]
            curr = events[i]

            # Temporal ordering
            relations.append(ActionRelation(
                from_id=prev.id,
                to_id=curr.id,
                relation_type="temporal",
            ))

            # Layer transition
            if prev.layer != curr.layer:
                relations.append(ActionRelation(
                    from_id=prev.id,
                    to_id=curr.id,
                    relation_type="layer_transition",
                ))

        return relations


# ---------------------------------------------------------------------------
# Convenience: canonical sequences
# ---------------------------------------------------------------------------

def make_pick_and_place(target: str = "object") -> ActionSequence:
    """
    Construct a canonical pick-and-place action sequence.

    This serves as both a test fixture and a reference pattern
    for the two-layer model.

    reach (Frame) → contact (Boundary) → grasp (Endpoint)
    → move (Frame) → release (Endpoint)
    """
    return ActionSequence(
        label=f"pick_and_place:{target}",
        events=[
            ActionElement(id="a1", name="reach",   layer=LAYER_FRAME,    target=target, timestamp=0.0),
            ActionElement(id="a2", name="contact", layer=LAYER_BOUNDARY, target=target, timestamp=1.0),
            ActionElement(id="a3", name="grasp",   layer=LAYER_ENDPOINT, target=target, timestamp=2.0),
            ActionElement(id="a4", name="move",    layer=LAYER_FRAME,    target=target, timestamp=3.0),
            ActionElement(id="a5", name="release", layer=LAYER_ENDPOINT, target=target, timestamp=4.0),
        ],
    )


def make_desk_task(target: str = "pen") -> ActionSequence:
    """
    Construct a simple desk task sequence.

    reach → contact → grasp → move → hold → release

    Includes a 'hold' state to demonstrate
    sustained functional endpoint observation.
    """
    return ActionSequence(
        label=f"desk_task:{target}",
        events=[
            ActionElement(id="d1", name="reach",   layer=LAYER_FRAME,    target=target, timestamp=0.0),
            ActionElement(id="d2", name="contact", layer=LAYER_BOUNDARY, target=target, timestamp=1.0),
            ActionElement(id="d3", name="grasp",   layer=LAYER_ENDPOINT, target=target, timestamp=2.0),
            ActionElement(id="d4", name="move",    layer=LAYER_FRAME,    target=target, timestamp=3.0),
            ActionElement(id="d5", name="hold",    layer=LAYER_ENDPOINT, target=target, timestamp=4.0),
            ActionElement(id="d6", name="release", layer=LAYER_ENDPOINT, target=target, timestamp=5.0),
        ],
    )
