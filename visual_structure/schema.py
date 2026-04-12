# visual_structure/schema.py

from typing import List, Dict, Any, Optional


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


class VisualStructureOutput:
    """
    Final output structure.
    """

    def __init__(
        self,
        elements: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        visual_metrics: Dict[str, Any],
        meta: Optional[Dict[str, Any]] = None,
    ):
        self.elements = elements
        self.relations = relations
        self.visual_metrics = visual_metrics
        self.meta = meta or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "elements": self.elements,
            "relations": self.relations,
            "visual_metrics": self.visual_metrics,
            "meta": self.meta,
        }
