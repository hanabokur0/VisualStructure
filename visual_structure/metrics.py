# visual_structure/metrics.py

import math
from typing import List, Dict, Any


def compute_metrics(elements: List[Dict[str, Any]], relations: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Compute all visual structure metrics.
    """

    return {
        "layout_entropy": compute_layout_entropy(elements),
        "attention_gradient": compute_attention_gradient(elements),
        "element_density": compute_element_density(elements),
        "contrast_signal": compute_contrast_signal(elements),
        "hierarchy_clarity": compute_hierarchy_clarity(elements),
        "flow_directionality": compute_flow_directionality(elements, relations),
        "occlusion_risk": compute_occlusion_risk(elements),
        "friction_signal": compute_friction_signal(elements, relations),
    }


# --------------------------------------------------
# Individual Metrics
# --------------------------------------------------

def compute_layout_entropy(elements: List[Dict[str, Any]]) -> float:
    """
    Measure spatial distribution entropy.
    """
    if not elements:
        return 0.0

    # Divide space into 4 regions (simple)
    regions = [0, 0, 0, 0]

    for el in elements:
        x, y = el["x"], el["y"]

        if x < 0.5 and y < 0.5:
            regions[0] += 1
        elif x >= 0.5 and y < 0.5:
            regions[1] += 1
        elif x < 0.5 and y >= 0.5:
            regions[2] += 1
        else:
            regions[3] += 1

    total = sum(regions)
    entropy = 0.0

    for r in regions:
        if r > 0:
            p = r / total
            entropy -= p * math.log(p)

    # Normalize (log(4))
    return entropy / math.log(4)


def compute_attention_gradient(elements: List[Dict[str, Any]]) -> float:
    """
    Measure focus intensity.
    """
    if not elements:
        return 0.0

    saliences = [el.get("salience", 0.0) for el in elements]

    max_s = max(saliences)
    mean_s = sum(saliences) / len(saliences)

    if mean_s == 0:
        return 0.0

    return max_s / mean_s


def compute_element_density(elements: List[Dict[str, Any]]) -> float:
    """
    Approximate density = number of elements.
    (Area is normalized, so just count)
    """
    return len(elements)


def compute_contrast_signal(elements: List[Dict[str, Any]]) -> float:
    """
    Simple proxy: variance of salience.
    """
    if not elements:
        return 0.0

    saliences = [el.get("salience", 0.0) for el in elements]
    mean_s = sum(saliences) / len(saliences)

    variance = sum((s - mean_s) ** 2 for s in saliences) / len(saliences)
    return variance


def compute_hierarchy_clarity(elements: List[Dict[str, Any]]) -> float:
    """
    Measure how distinguishable salience levels are.
    """
    if not elements:
        return 0.0

    saliences = sorted(el.get("salience", 0.0) for el in elements)

    # Differences between adjacent values
    diffs = [abs(saliences[i+1] - saliences[i]) for i in range(len(saliences)-1)]

    if not diffs:
        return 0.0

    return sum(diffs) / len(diffs)


def compute_flow_directionality(elements: List[Dict[str, Any]], relations: List[Dict[str, Any]]) -> float:
    """
    Simple proxy: count directional relations.
    """
    if not relations:
        return 0.0

    directional = 0

    for r in relations:
        if r.get("relation_type") in ["flow", "hierarchical"]:
            directional += 1

    return directional / len(relations)


def compute_occlusion_risk(elements: List[Dict[str, Any]]) -> float:
    """
    Measure overlap between elements.
    """
    if len(elements) < 2:
        return 0.0

    overlaps = 0
    total_pairs = 0

    for i in range(len(elements)):
        for j in range(i + 1, len(elements)):
            total_pairs += 1
            if is_overlap(elements[i], elements[j]):
                overlaps += 1

    if total_pairs == 0:
        return 0.0

    return overlaps / total_pairs


def compute_friction_signal(elements: List[Dict[str, Any]], relations: List[Dict[str, Any]]) -> float:
    """
    Composite signal.
    """
    density = compute_element_density(elements)
    hierarchy = compute_hierarchy_clarity(elements)
    flow = compute_flow_directionality(elements, relations)

    # Simple heuristic
    friction = (density * 0.1) + (1 - hierarchy) + (1 - flow)

    return friction


# --------------------------------------------------
# Helper
# --------------------------------------------------

def is_overlap(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    """
    Check bounding box overlap.
    """
    ax1, ay1 = a["x"], a["y"]
    ax2, ay2 = a["x"] + a["w"], a["y"] + a["h"]

    bx1, by1 = b["x"], b["y"]
    bx2, by2 = b["x"] + b["w"], b["y"] + b["h"]

    return not (ax2 < bx1 or ax1 > bx2 or ay2 < by1 or ay1 > by2)
