# tests/test_metrics.py

from visual_structure.metrics import (
    compute_layout_entropy,
    compute_attention_gradient,
    compute_element_density,
    compute_contrast_signal,
    compute_hierarchy_clarity,
    compute_occlusion_risk,
    compute_friction_signal,
)


def sample_elements_simple():
    return [
        {"id": "el1", "x": 0.1, "y": 0.1, "w": 0.2, "h": 0.2, "salience": 0.5},
        {"id": "el2", "x": 0.7, "y": 0.1, "w": 0.2, "h": 0.2, "salience": 1.0},
        {"id": "el3", "x": 0.5, "y": 0.7, "w": 0.2, "h": 0.2, "salience": 0.2},
    ]


def sample_elements_overlap():
    return [
        {"id": "a", "x": 0.1, "y": 0.1, "w": 0.5, "h": 0.5, "salience": 0.5},
        {"id": "b", "x": 0.3, "y": 0.3, "w": 0.5, "h": 0.5, "salience": 0.5},
    ]


def test_layout_entropy_range():
    elements = sample_elements_simple()
    le = compute_layout_entropy(elements)

    assert 0.0 <= le <= 1.0


def test_attention_gradient_positive():
    elements = sample_elements_simple()
    ag = compute_attention_gradient(elements)

    assert ag >= 0.0


def test_element_density():
    elements = sample_elements_simple()
    ed = compute_element_density(elements)

    assert ed == len(elements)


def test_contrast_signal_non_negative():
    elements = sample_elements_simple()
    cs = compute_contrast_signal(elements)

    assert cs >= 0.0


def test_hierarchy_clarity_non_negative():
    elements = sample_elements_simple()
    hc = compute_hierarchy_clarity(elements)

    assert hc >= 0.0


def test_occlusion_detected():
    elements = sample_elements_overlap()
    oc = compute_occlusion_risk(elements)

    assert oc > 0.0


def test_occlusion_zero_when_no_overlap():
    elements = sample_elements_simple()
    oc = compute_occlusion_risk(elements)

    assert oc == 0.0


def test_friction_signal_non_negative():
    elements = sample_elements_simple()
    fr = compute_friction_signal(elements, relations=[])

    assert fr >= 0.0
