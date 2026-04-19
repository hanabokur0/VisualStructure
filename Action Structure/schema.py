# visual_structure/schema.py

from typing import List, Dict, Any, Optional


# ===========================================================================
# Visual Structure
# ===========================================================================


class VisualElement:
    """
    Represents a single detected visual element.
    """

    def __init__(
        self,
        id: str,
        type: str,
        x: float,
        y: float,
        w: float,
        h: float,
        salience: float = 0.0,
        label: Optional[str] = None,
    ):
        self.id = id
        self.type = type
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.salience = salience
        self.label = label

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "x": self.x,
            "y": self.y,
            "w": self.w,
            "h": self.h,
            "salience": self.salience,
            "label": self.label,
        }


class VisualRelation:
    """
    Represents relationship between two elements.
    """

    def __init__(
        self,
        from_id: str,
        to_id: str,
        relation_type: str,
    ):
        self.from_id = from_id
        self.to_id = to_id
        self.relation_type = relation_type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from": self.from_id,
            "to": self.to_id,
            "relation_type": self.relation_type,
        }


class VisualMetrics:
    """
    Container for all computed visual metrics.
    """

    def __init__(
        self,
        layout_entropy: float = 0.0,
        attention_gradient: float = 0.0,
        element_density: float = 0.0,
        contrast_signal: float = 0.0,
        hierarchy_clarity: float = 0.0,
        flow_directionality: float = 0.0,
        occlusion_risk: float = 0.0,
        friction_signal: float = 0.0,
    ):
        self.layout_entropy = layout_entropy
        self.attention_gradient = attention_gradient
        self.element_density = element_density
        self.contrast_signal = contrast_signal
        self.hierarchy_clarity = hierarchy_clarity
        self.flow_directionality = flow_directionality
        self.occlusion_risk = occlusion_risk
        self.friction_signal = friction_signal

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layout_entropy": self.layout_entropy,
            "attention_gradient": self.attention_gradient,
            "element_density": self.element_density,
            "contrast_signal": self.contrast_signal,
            "hierarchy_clarity": self.hierarchy_clarity,
            "flow_directionality": self.flow_directionality,
            "occlusion_risk": self.occlusion_risk,
            "friction_signal": self.friction_signal,
        }


# ===========================================================================
# Action Structure (Proposed)
# ===========================================================================


class ActionElement:
    """
    A single structural action event.

    This is NOT a kinematic sample.
    It is a discrete functional state observed at the appropriate layer.

    Layers:
        "frame"                — skeletal posture transition (reach, approach, withdraw)
        "functional_endpoint"  — terminal node state change (grasp, release, contact)
        "boundary"             — transition point between layers (contact)
    """

    def __init__(
        self,
        id: str,
        name: str,
        layer: str,
        target: Optional[str] = None,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.id = id
        self.name = name
        self.layer = layer
        self.target = target
        self.timestamp = timestamp
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "id": self.id,
            "name": self.name,
            "layer": self.layer,
        }
        if self.target is not None:
            d["target"] = self.target
        if self.timestamp is not None:
            d["timestamp"] = self.timestamp
        if self.metadata:
            d["metadata"] = self.metadata
        return d


class ActionRelation:
    """
    Relationship between two action elements.

    Relation types:
        "temporal"    — sequential ordering
        "dependency"  — one action requires another to complete first
        "branch"      — conditional fork in action flow
        "layer_transition" — observation layer changes between events
    """

    def __init__(
        self,
        from_id: str,
        to_id: str,
        relation_type: str,
    ):
        self.from_id = from_id
        self.to_id = to_id
        self.relation_type = relation_type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from": self.from_id,
            "to": self.to_id,
            "relation_type": self.relation_type,
        }


class ActionMetrics:
    """
    Container for all computed action metrics (proposed).
    """

    def __init__(
        self,
        grip_transition_signal: float = 0.0,
        action_flow_stability: float = 0.0,
        manipulation_friction: float = 0.0,
        action_branching_signal: Optional[float] = None,
    ):
        self.grip_transition_signal = grip_transition_signal
        self.action_flow_stability = action_flow_stability
        self.manipulation_friction = manipulation_friction
        self.action_branching_signal = action_branching_signal

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grip_transition_signal": self.grip_transition_signal,
            "action_flow_stability": self.action_flow_stability,
            "manipulation_friction": self.manipulation_friction,
            "action_branching_signal": self.action_branching_signal,
        }


class ActionStructureData:
    """
    Container for action structure within VisualStructureOutput.

    Holds frame events, endpoint events, the full sequence,
    and computed action metrics.
    """

    def __init__(
        self,
        frame_events: Optional[List[Dict[str, Any]]] = None,
        endpoint_events: Optional[List[Dict[str, Any]]] = None,
        action_sequence: Optional[List[Dict[str, Any]]] = None,
        action_metrics: Optional[Dict[str, Any]] = None,
    ):
        self.frame_events = frame_events or []
        self.endpoint_events = endpoint_events or []
        self.action_sequence = action_sequence or []
        self.action_metrics = action_metrics or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_events": self.frame_events,
            "endpoint_events": self.endpoint_events,
            "action_sequence": self.action_sequence,
            "action_metrics": self.action_metrics,
        }


# ===========================================================================
# Combined Output
# ===========================================================================


class VisualStructureOutput:
    """
    Final output structure.

    Combines visual structure and action structure (when present)
    into a single structured dict.
    """

    def __init__(
        self,
        elements: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        visual_metrics: Dict[str, Any],
        action_structure: Optional[Dict[str, Any]] = None,
        meta: Optional[Dict[str, Any]] = None,
    ):
        self.elements = elements
        self.relations = relations
        self.visual_metrics = visual_metrics
        self.action_structure = action_structure
        self.meta = meta or {}

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "elements": self.elements,
            "relations": self.relations,
            "visual_metrics": self.visual_metrics,
            "meta": self.meta,
        }
        if self.action_structure is not None:
            d["action_structure"] = self.action_structure
        return d
