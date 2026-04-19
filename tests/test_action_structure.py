"""
test_action_structure.py

Tests for the Action Structure module.

Run:
    python -m pytest tests/test_action_structure.py -v

Or standalone:
    python tests/test_action_structure.py
"""

import sys
import os
import unittest

# ---------------------------------------------------------------------------
# Path setup — allow running from project root or tests/ directory
# ---------------------------------------------------------------------------

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from action_structure.schema import (
    ActionElement,
    ActionRelation,
    ActionMetrics,
    ActionStructureData,
)
from action_structure.action_structure import (
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


# ===========================================================================
# Schema Tests
# ===========================================================================


class TestActionElement(unittest.TestCase):
    """Test ActionElement creation and serialization."""

    def test_minimal(self):
        e = ActionElement(id="e1", name="reach", layer=LAYER_FRAME)
        d = e.to_dict()
        self.assertEqual(d["id"], "e1")
        self.assertEqual(d["name"], "reach")
        self.assertEqual(d["layer"], "frame")
        self.assertNotIn("target", d)
        self.assertNotIn("timestamp", d)

    def test_full(self):
        e = ActionElement(
            id="e2", name="grasp", layer=LAYER_ENDPOINT,
            target="cup", timestamp=2.5, metadata={"force": 0.8},
        )
        d = e.to_dict()
        self.assertEqual(d["target"], "cup")
        self.assertEqual(d["timestamp"], 2.5)
        self.assertEqual(d["metadata"]["force"], 0.8)


class TestActionRelation(unittest.TestCase):
    """Test ActionRelation creation and serialization."""

    def test_basic(self):
        r = ActionRelation(from_id="a1", to_id="a2", relation_type="temporal")
        d = r.to_dict()
        self.assertEqual(d["from"], "a1")
        self.assertEqual(d["to"], "a2")
        self.assertEqual(d["relation_type"], "temporal")


class TestActionMetrics(unittest.TestCase):
    """Test ActionMetrics container."""

    def test_defaults(self):
        m = ActionMetrics()
        d = m.to_dict()
        self.assertEqual(d["grip_transition_signal"], 0.0)
        self.assertEqual(d["action_flow_stability"], 0.0)
        self.assertEqual(d["manipulation_friction"], 0.0)
        self.assertIsNone(d["action_branching_signal"])

    def test_custom_values(self):
        m = ActionMetrics(
            grip_transition_signal=0.4,
            action_flow_stability=0.0,
            manipulation_friction=0.4,
            action_branching_signal=1.5,
        )
        d = m.to_dict()
        self.assertEqual(d["grip_transition_signal"], 0.4)
        self.assertEqual(d["action_branching_signal"], 1.5)


class TestActionStructureData(unittest.TestCase):
    """Test ActionStructureData container."""

    def test_empty(self):
        data = ActionStructureData()
        d = data.to_dict()
        self.assertEqual(d["frame_events"], [])
        self.assertEqual(d["endpoint_events"], [])
        self.assertEqual(d["action_sequence"], [])
        self.assertEqual(d["action_metrics"], {})


# ===========================================================================
# Sequence Tests
# ===========================================================================


class TestActionSequence(unittest.TestCase):
    """Test ActionSequence operations."""

    def _make_events(self):
        return [
            ActionElement(id="s1", name="reach",   layer=LAYER_FRAME),
            ActionElement(id="s2", name="contact", layer=LAYER_BOUNDARY),
            ActionElement(id="s3", name="grasp",   layer=LAYER_ENDPOINT),
        ]

    def test_creation(self):
        seq = ActionSequence(events=self._make_events(), label="test")
        self.assertEqual(len(seq.events), 3)
        self.assertEqual(seq.label, "test")

    def test_append(self):
        seq = ActionSequence()
        seq.append(ActionElement(id="x1", name="reach", layer=LAYER_FRAME))
        self.assertEqual(len(seq.events), 1)

    def test_layer_transitions(self):
        seq = ActionSequence(events=self._make_events())
        transitions = seq.layer_transitions()
        self.assertEqual(len(transitions), 2)
        self.assertEqual(transitions[0]["from"], "frame")
        self.assertEqual(transitions[0]["to"], "boundary")
        self.assertEqual(transitions[1]["from"], "boundary")
        self.assertEqual(transitions[1]["to"], "functional_endpoint")

    def test_no_transitions_same_layer(self):
        """Events in same layer produce no transitions."""
        events = [
            ActionElement(id="f1", name="reach",    layer=LAYER_FRAME),
            ActionElement(id="f2", name="approach", layer=LAYER_FRAME),
            ActionElement(id="f3", name="withdraw", layer=LAYER_FRAME),
        ]
        seq = ActionSequence(events=events)
        self.assertEqual(seq.layer_transitions(), [])

    def test_to_dict(self):
        seq = ActionSequence(events=self._make_events(), label="test")
        d = seq.to_dict()
        self.assertIn("events", d)
        self.assertIn("layer_transitions", d)
        self.assertEqual(d["label"], "test")


# ===========================================================================
# Metrics Tests
# ===========================================================================


class TestIndividualMetrics(unittest.TestCase):
    """Test individual compute functions."""

    def test_gts_empty(self):
        self.assertEqual(compute_grip_transition_signal([]), 0.0)

    def test_gts_pick_and_place(self):
        seq = make_pick_and_place("cup")
        gts = compute_grip_transition_signal(seq.events)
        # 2 endpoint events out of 5 total
        self.assertAlmostEqual(gts, 0.4)

    def test_gts_all_endpoints(self):
        events = [
            ActionElement(id="e1", name="grasp",   layer=LAYER_ENDPOINT),
            ActionElement(id="e2", name="hold",    layer=LAYER_ENDPOINT),
            ActionElement(id="e3", name="release", layer=LAYER_ENDPOINT),
        ]
        self.assertAlmostEqual(compute_grip_transition_signal(events), 1.0)

    def test_afs_single_event(self):
        seq = ActionSequence(events=[
            ActionElement(id="x1", name="reach", layer=LAYER_FRAME),
        ])
        self.assertEqual(compute_action_flow_stability(seq), 1.0)

    def test_afs_no_transitions(self):
        """All same layer → AFS = 1.0 (maximum stability)."""
        seq = ActionSequence(events=[
            ActionElement(id="f1", name="reach",    layer=LAYER_FRAME),
            ActionElement(id="f2", name="approach", layer=LAYER_FRAME),
            ActionElement(id="f3", name="move",     layer=LAYER_FRAME),
        ])
        self.assertAlmostEqual(compute_action_flow_stability(seq), 1.0)

    def test_afs_all_transitions(self):
        """Every pair changes layer → AFS = 0.0."""
        seq = make_pick_and_place("cup")
        afs = compute_action_flow_stability(seq)
        # 4 transitions out of 4 possible → 0.0
        self.assertAlmostEqual(afs, 0.0)

    def test_mf_empty(self):
        self.assertEqual(compute_manipulation_friction([]), 0.0)

    def test_mf_desk_task(self):
        seq = make_desk_task("pen")
        mf = compute_manipulation_friction(seq.events)
        # 3 endpoint events out of 6 total
        self.assertAlmostEqual(mf, 0.5)

    def test_abs_no_annotation(self):
        seq = make_pick_and_place("cup")
        self.assertIsNone(compute_action_branching_signal(seq))

    def test_abs_with_annotation(self):
        """When branching metadata is present, ABS should compute."""
        events = [
            ActionElement(
                id="b1", name="reach", layer=LAYER_FRAME,
                metadata={"branches": ["path_a", "path_b"]},
            ),
            ActionElement(id="b2", name="grasp", layer=LAYER_ENDPOINT),
            ActionElement(id="b3", name="move",  layer=LAYER_FRAME),
        ]
        seq = ActionSequence(events=events)
        abs_val = compute_action_branching_signal(seq)
        # 1 event with 2 branches, 3 total events → 2/3
        self.assertIsNotNone(abs_val)
        self.assertAlmostEqual(abs_val, 2 / 3)


class TestComputeActionMetrics(unittest.TestCase):
    """Test the aggregate compute_action_metrics function."""

    def test_pick_and_place(self):
        seq = make_pick_and_place("cup")
        m = compute_action_metrics(seq)
        self.assertAlmostEqual(m["grip_transition_signal"], 0.4)
        self.assertAlmostEqual(m["action_flow_stability"], 0.0)
        self.assertAlmostEqual(m["manipulation_friction"], 0.4)
        self.assertIsNone(m["action_branching_signal"])

    def test_desk_task(self):
        seq = make_desk_task("pen")
        m = compute_action_metrics(seq)
        self.assertAlmostEqual(m["grip_transition_signal"], 0.5)
        self.assertAlmostEqual(m["action_flow_stability"], 0.2)
        self.assertAlmostEqual(m["manipulation_friction"], 0.5)

    def test_empty_sequence(self):
        seq = ActionSequence()
        m = compute_action_metrics(seq)
        self.assertEqual(m["grip_transition_signal"], 0.0)
        self.assertEqual(m["action_flow_stability"], 1.0)
        self.assertEqual(m["manipulation_friction"], 0.0)


# ===========================================================================
# Analyzer Tests
# ===========================================================================


class TestActionStructureAnalyzer(unittest.TestCase):
    """Test the main analyzer."""

    def setUp(self):
        self.analyzer = ActionStructureAnalyzer()

    def test_pick_and_place_output_structure(self):
        seq = make_pick_and_place("cup")
        result = self.analyzer.analyze(seq.events, label="pick_and_place:cup")

        # Top-level keys
        self.assertIn("frame_events", result)
        self.assertIn("endpoint_events", result)
        self.assertIn("action_sequence", result)
        self.assertIn("action_metrics", result)

    def test_frame_endpoint_separation(self):
        seq = make_pick_and_place("cup")
        result = self.analyzer.analyze(seq.events)

        # 2 frame events: reach, move
        self.assertEqual(len(result["frame_events"]), 2)
        frame_names = [e["name"] for e in result["frame_events"]]
        self.assertIn("reach", frame_names)
        self.assertIn("move", frame_names)

        # 2 endpoint events: grasp, release
        self.assertEqual(len(result["endpoint_events"]), 2)
        endpoint_names = [e["name"] for e in result["endpoint_events"]]
        self.assertIn("grasp", endpoint_names)
        self.assertIn("release", endpoint_names)

    def test_boundary_not_in_frame_or_endpoint(self):
        """Boundary events should not appear in frame or endpoint lists."""
        seq = make_pick_and_place("cup")
        result = self.analyzer.analyze(seq.events)

        all_separated = result["frame_events"] + result["endpoint_events"]
        layers = [e["layer"] for e in all_separated]
        self.assertNotIn("boundary", layers)

    def test_sequence_preserved(self):
        seq = make_pick_and_place("cup")
        result = self.analyzer.analyze(seq.events, label="test_label")

        self.assertEqual(result["action_sequence"]["label"], "test_label")
        self.assertEqual(len(result["action_sequence"]["events"]), 5)

    def test_metrics_present(self):
        seq = make_pick_and_place("cup")
        result = self.analyzer.analyze(seq.events)
        m = result["action_metrics"]

        self.assertIn("grip_transition_signal", m)
        self.assertIn("action_flow_stability", m)
        self.assertIn("manipulation_friction", m)
        self.assertIn("action_branching_signal", m)

    def test_empty_events(self):
        result = self.analyzer.analyze([])
        self.assertEqual(result["frame_events"], [])
        self.assertEqual(result["endpoint_events"], [])
        self.assertEqual(result["action_metrics"]["grip_transition_signal"], 0.0)

    def test_desk_task_has_hold(self):
        """Desk task should include hold in endpoint events."""
        seq = make_desk_task("pen")
        result = self.analyzer.analyze(seq.events)

        endpoint_names = [e["name"] for e in result["endpoint_events"]]
        self.assertIn("hold", endpoint_names)
        self.assertEqual(len(result["endpoint_events"]), 3)


# ===========================================================================
# Convenience Function Tests
# ===========================================================================


class TestConvenienceFunctions(unittest.TestCase):
    """Test make_pick_and_place and make_desk_task."""

    def test_pick_and_place_structure(self):
        seq = make_pick_and_place("bottle")
        self.assertEqual(seq.label, "pick_and_place:bottle")
        self.assertEqual(len(seq.events), 5)

        names = [e.name for e in seq.events]
        self.assertEqual(names, ["reach", "contact", "grasp", "move", "release"])

        layers = [e.layer for e in seq.events]
        self.assertEqual(layers, [
            LAYER_FRAME, LAYER_BOUNDARY, LAYER_ENDPOINT,
            LAYER_FRAME, LAYER_ENDPOINT,
        ])

    def test_desk_task_structure(self):
        seq = make_desk_task("pen")
        self.assertEqual(seq.label, "desk_task:pen")
        self.assertEqual(len(seq.events), 6)

        names = [e.name for e in seq.events]
        self.assertEqual(names, ["reach", "contact", "grasp", "move", "hold", "release"])

    def test_default_target(self):
        seq1 = make_pick_and_place()
        self.assertTrue(all(e.target == "object" for e in seq1.events))

        seq2 = make_desk_task()
        self.assertTrue(all(e.target == "pen" for e in seq2.events))

    def test_timestamps_ordered(self):
        for seq in [make_pick_and_place(), make_desk_task()]:
            timestamps = [e.timestamp for e in seq.events]
            self.assertEqual(timestamps, sorted(timestamps))


# ===========================================================================
# Integration: Metrics Comparison Between Sequences
# ===========================================================================


class TestMetricsComparison(unittest.TestCase):
    """
    Verify that metrics correctly distinguish
    different task structures.
    """

    def test_desk_task_more_manipulation_than_pick_place(self):
        """Desk task has more endpoint events → higher MF."""
        m_pick = compute_action_metrics(make_pick_and_place())
        m_desk = compute_action_metrics(make_desk_task())
        self.assertGreater(
            m_desk["manipulation_friction"],
            m_pick["manipulation_friction"],
        )

    def test_desk_task_more_stable_than_pick_place(self):
        """Desk task has consecutive endpoint events → higher AFS."""
        m_pick = compute_action_metrics(make_pick_and_place())
        m_desk = compute_action_metrics(make_desk_task())
        self.assertGreater(
            m_desk["action_flow_stability"],
            m_pick["action_flow_stability"],
        )

    def test_pure_frame_sequence_maximum_stability(self):
        """A sequence with only frame events has AFS = 1.0."""
        events = [
            ActionElement(id=f"f{i}", name="step", layer=LAYER_FRAME)
            for i in range(5)
        ]
        seq = ActionSequence(events=events)
        m = compute_action_metrics(seq)
        self.assertAlmostEqual(m["action_flow_stability"], 1.0)
        self.assertAlmostEqual(m["grip_transition_signal"], 0.0)
        self.assertAlmostEqual(m["manipulation_friction"], 0.0)


# ===========================================================================
# Run
# ===========================================================================

if __name__ == "__main__":
    unittest.main()
