"""
action_structure.py

Action Structure module for VisualStructure.

Treats motion not as raw high-dimensional trajectories,
but as structural action events observed through a two-layer model:

  Frame Layer           — skeletal posture transitions (reach, approach, withdraw)
  Functional Endpoint   — discrete state changes at terminal nodes (grasp, release, contact)

Design Principle:
  Structure before trajectory. Function before full reconstruction.
  Observe at the layer appropriate to the function.

Status: proposed / experimental
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


# ---------------------------------------------------------------------------
# Layer definitions
# ---------------------------------------------------------------------------

class ActionLayer(Enum):
    """Which observation layer an action event belongs to."""
    FRAME = "frame"
    FUNCTIONAL_ENDPOINT = "functional_endpoint"
    BOUNDARY = "boundary"


# ---------------------------------------------------------------------------
# Action events
# ---------------------------------------------------------------------------

@dataclass
class ActionEvent:
    """
    A single structural action event.

    This is NOT a kinematic sample.
    It is a discrete functional state observed at the appropriate layer.

    Attributes:
        name:       action label (e.g. "reach", "grasp", "release")
        layer:      observation layer (Frame / Functional Endpoint / Boundary)
        target:     optional object or region the action is directed at
        timestamp:  optional temporal position (seconds, frame number, or ordinal)
        metadata:   any additional observations
    """
    name: str
    layer: ActionLayer
    target: Optional[str] = None
    timestamp: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "name": self.name,
            "layer": self.layer.value,
        }
        if self.target is not None:
            d["target"] = self.target
        if self.timestamp is not None:
            d["timestamp"] = self.timestamp
        if self.metadata:
            d["metadata"] = self.metadata
        return d


# ---------------------------------------------------------------------------
# Action sequence
# ---------------------------------------------------------------------------

@dataclass
class ActionSequence:
    """
    An ordered chain of ActionEvents.

    Captures layer transitions within a single task unit.
    Example:
        reach (Frame) → contact (Boundary) → grasp (Endpoint) → move (Frame) → release (Endpoint)
    """
    events: List[ActionEvent] = field(default_factory=list)
    label: Optional[str] = None

    def append(self, event: ActionEvent) -> None:
        self.events.append(event)

    def layer_transitions(self) -> List[tuple]:
        """
        Return list of (from_layer, to_layer) transitions in the sequence.
        """
        transitions = []
        for i in range(1, len(self.events)):
            prev = self.events[i - 1].layer
            curr = self.events[i].layer
            if prev != curr:
                transitions.append((prev.value, curr.value))
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
# Action metrics (proposed)
# ---------------------------------------------------------------------------

def compute_action_metrics(sequence: ActionSequence) -> Dict[str, Any]:
    """
    Compute proposed action metrics from a sequence.

    Metrics:
        GTS  — Grip Transition Signal
               State change frequency at functional endpoints.
               Higher values indicate more complex manipulation.

        AFS  — Action Flow Stability
               Ratio of expected layer transitions to actual.
               1.0 = perfectly smooth flow; <1.0 = unexpected transitions.

        MF   — Manipulation Friction
               Proportion of functional endpoint events in the sequence.
               Higher values indicate manipulation-heavy tasks.

        ABS  — Action Branching Signal
               Placeholder for decision density at branching points.
               Requires branching annotation (not yet implemented).

    Args:
        sequence: an ActionSequence

    Returns:
        dict of metric name → value
    """
    events = sequence.events
    n = len(events)

    if n == 0:
        return {
            "GTS": 0.0,
            "AFS": 0.0,
            "MF": 0.0,
            "ABS": None,
        }

    # GTS — count functional endpoint events
    endpoint_events = [
        e for e in events
        if e.layer == ActionLayer.FUNCTIONAL_ENDPOINT
    ]
    gts = len(endpoint_events) / n

    # AFS — layer transition smoothness
    transitions = sequence.layer_transitions()
    if n <= 1:
        afs = 1.0
    else:
        # expected transitions = every adjacent pair could transition
        max_possible = n - 1
        afs = 1.0 - (len(transitions) / max_possible) if max_possible > 0 else 1.0

    # MF — manipulation friction
    mf = len(endpoint_events) / n

    # ABS — placeholder (requires branching annotation)
    abs_signal = None

    return {
        "GTS": round(gts, 4),
        "AFS": round(afs, 4),
        "MF": round(mf, 4),
        "ABS": abs_signal,
    }


# ---------------------------------------------------------------------------
# Output structure
# ---------------------------------------------------------------------------

@dataclass
class ActionStructureOutput:
    """
    Structured output for action structure analysis.

    Follows the same pattern as VisualStructureOutput:
    data in, structured dict out.
    """
    frame_events: List[ActionEvent] = field(default_factory=list)
    endpoint_events: List[ActionEvent] = field(default_factory=list)
    action_sequence: Optional[ActionSequence] = None
    action_metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_events": [e.to_dict() for e in self.frame_events],
            "endpoint_events": [e.to_dict() for e in self.endpoint_events],
            "action_sequence": self.action_sequence.to_dict() if self.action_sequence else [],
            "action_metrics": self.action_metrics,
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
    - compute action metrics
    - return structured output

    This layer does NOT:
    - perform pose estimation
    - track joint kinematics
    - reconstruct full motion trajectories
    """

    def __init__(self):
        pass

    def analyze(self, events: List[ActionEvent], label: Optional[str] = None) -> Dict[str, Any]:
        """
        Main entry point.

        Args:
            events: list of ActionEvent instances (pre-classified by layer)
            label:  optional label for the action sequence

        Returns:
            dict: structured action representation
        """
        # Build sequence
        sequence = ActionSequence(events=events, label=label)

        # Separate by layer
        frame_events = [
            e for e in events
            if e.layer == ActionLayer.FRAME
        ]
        endpoint_events = [
            e for e in events
            if e.layer == ActionLayer.FUNCTIONAL_ENDPOINT
        ]

        # Compute metrics
        metrics = compute_action_metrics(sequence)

        # Build output
        output = ActionStructureOutput(
            frame_events=frame_events,
            endpoint_events=endpoint_events,
            action_sequence=sequence,
            action_metrics=metrics,
        )
        return output.to_dict()


# ---------------------------------------------------------------------------
# Convenience: build a standard pick-and-place sequence
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
            ActionEvent(name="reach",   layer=ActionLayer.FRAME,                target=target, timestamp=0.0),
            ActionEvent(name="contact", layer=ActionLayer.BOUNDARY,             target=target, timestamp=1.0),
            ActionEvent(name="grasp",   layer=ActionLayer.FUNCTIONAL_ENDPOINT,  target=target, timestamp=2.0),
            ActionEvent(name="move",    layer=ActionLayer.FRAME,                target=target, timestamp=3.0),
            ActionEvent(name="release", layer=ActionLayer.FUNCTIONAL_ENDPOINT,  target=target, timestamp=4.0),
        ]
    )
