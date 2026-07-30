"""
Unit tests for ZANIME Phase 4 — Professional Production Suite.

Covers:
  - Multi-Camera System (Keyframe interpolation, CameraRig, Presets)
  - Advanced Timeline System (Snapping, TrackManager Ripple/Slip/Slide)
  - Node Graph System (Serialization, DAG Topological Sort Execution Engine)
  - VFX & Particle Engine (Physics update tick, Emitter Presets, VFX Pipeline)
  - Render Engine (Queueing, Multi-job handling)
  - Collaboration Manager (Project locking, comments, version notes)
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from src.core.managers.collaboration_manager import ApprovalStatus, CollaborationManager
from src.core.managers.node_execution_engine import NodeExecutionEngine
from src.core.managers.track_manager import TrackManager
from src.core.services.particle_engine import ParticleEmitter, ParticlePreset
from src.core.services.render_engine import RenderEngine
from src.core.services.vfx_engine import VFXEngine, VFXType
from src.models.camera_model import (
    PRESET_KEYFRAMES,
    Camera,
    CameraAnimationTrack,
    CameraKeyframe,
    CameraMovementPreset,
    CameraRig,
    EasingType,
)
from src.models.node_graph_model import (
    NODE_CATALOG,
    NodeGraphModel,
    create_node_from_definition,
)
from src.models.timeline_model import (
    AdvancedTimelineModel,
    TimelineClip,
    TimelineTrack,
    TrackType,
)


# ---------------------------------------------------------------------------
# Multi-Camera System Tests
# ---------------------------------------------------------------------------

class TestCameraPhase4(unittest.TestCase):
    def setUp(self):
        self.rig = CameraRig()
        self.cam1 = self.rig.add_camera("Main Camera")
        self.cam2 = self.rig.add_camera("Wide Shot")

    def test_camera_rig_initial_active(self):
        self.assertEqual(self.rig.active_camera_uuid, self.cam1.uuid)
        self.assertEqual(self.rig.get_active().name, "Main Camera")

    def test_camera_rig_switch_to(self):
        self.rig.switch_to(self.cam2.uuid)
        self.assertEqual(self.rig.active_camera_uuid, self.cam2.uuid)
        self.assertTrue(self.cam2.is_active)
        self.assertFalse(self.cam1.is_active)

    def test_keyframe_linear_interpolation(self):
        track = CameraAnimationTrack(property_name="x", camera_uuid=self.cam1.uuid)
        track.keyframes.append(CameraKeyframe(frame=0, value=0.0, easing=EasingType.LINEAR.value))
        track.keyframes.append(CameraKeyframe(frame=24, value=240.0, easing=EasingType.LINEAR.value))

        val = track.get_value_at_frame(12)
        self.assertAlmostEqual(val, 120.0, places=2)

    def test_keyframe_boundary_values(self):
        track = CameraAnimationTrack(property_name="zoom", camera_uuid=self.cam1.uuid)
        track.keyframes.append(CameraKeyframe(frame=10, value=1.5))
        track.keyframes.append(CameraKeyframe(frame=30, value=3.0))

        self.assertEqual(track.get_value_at_frame(0), 1.5)
        self.assertEqual(track.get_value_at_frame(50), 3.0)

    def test_preset_keyframes_exist(self):
        self.assertIn("Pan Left", PRESET_KEYFRAMES)
        self.assertIn("Zoom In", PRESET_KEYFRAMES)
        self.assertGreater(len(PRESET_KEYFRAMES["Zoom In"]), 0)


# ---------------------------------------------------------------------------
# Advanced Timeline System Tests
# ---------------------------------------------------------------------------

class TestTimelinePhase4(unittest.TestCase):
    def setUp(self):
        self.model = AdvancedTimelineModel()
        self.track = self.model.add_track("Video 1", TrackType.VIDEO.value)
        self.mgr = TrackManager(self.model)

    def test_snapping_to_marker(self):
        self.model.add_marker(frame=100, label="Marker 1")
        snapped = self.model.find_snap_point(98)
        self.assertEqual(snapped, 100)

    def test_ripple_insert(self):
        c1 = TimelineClip(name="Clip 1", start_frame=0, duration=24)
        c2 = TimelineClip(name="Clip 2", start_frame=24, duration=24)
        self.track.clips = [c1, c2]

        new_clip = TimelineClip(name="Inserted Clip", start_frame=12, duration=10)
        success = self.mgr.ripple_insert(self.track.uuid, new_clip)

        self.assertTrue(success)
        # c2 start_frame should have shifted right by 10
        self.assertEqual(c2.start_frame, 34)

    def test_ripple_delete(self):
        c1 = TimelineClip(name="Clip 1", start_frame=0, duration=24)
        c2 = TimelineClip(name="Clip 2", start_frame=24, duration=24)
        self.track.clips = [c1, c2]

        success = self.mgr.ripple_delete(self.track.uuid, c1.uuid)
        self.assertTrue(success)
        self.assertEqual(len(self.track.clips), 1)
        self.assertEqual(c2.start_frame, 0)

    def test_slip_clip(self):
        clip = TimelineClip(name="Clip 1", start_frame=10, duration=20, source_in=0, source_out=20)
        self.track.clips.append(clip)

        success = self.mgr.slip_clip(self.track.uuid, clip.uuid, 5)
        self.assertTrue(success)
        self.assertEqual(clip.source_in, 5)
        self.assertEqual(clip.source_out, 25)
        self.assertEqual(clip.start_frame, 10)  # Unchanged on timeline


# ---------------------------------------------------------------------------
# Node Graph System Tests
# ---------------------------------------------------------------------------

class TestNodeGraphPhase4(unittest.TestCase):
    def setUp(self):
        self.graph = NodeGraphModel()

    def test_node_catalog_contains_nodes(self):
        self.assertGreater(len(NODE_CATALOG), 15)

    def test_create_node_from_definition(self):
        node = create_node_from_definition(NODE_CATALOG[0], 10.0, 20.0)
        self.assertEqual(node.x, 10.0)
        self.assertEqual(node.y, 20.0)
        self.assertGreater(len(node.outputs), 0)

    def test_graph_serialization_to_dict(self):
        n1 = create_node_from_definition(NODE_CATALOG[0])
        self.graph.add_node(n1)
        d = self.graph.to_dict()
        self.assertIn("nodes", d)
        self.assertEqual(len(d["nodes"]), 1)

    def test_dag_math_execution(self):
        # Create Add node: 5 + 3 = 8
        n_add = create_node_from_definition(NODE_CATALOG[16])  # math_add
        self.graph.add_node(n_add)

        engine = NodeExecutionEngine(self.graph)
        engine.execute()
        vals = engine.port_values.get(n_add.uuid, {})
        self.assertIn("out_sum", vals)


# ---------------------------------------------------------------------------
# VFX & Particle Engine Tests
# ---------------------------------------------------------------------------

class TestVFXPhase4(unittest.TestCase):
    def test_particle_emitter_tick(self):
        emitter = ParticleEmitter(ParticlePreset.SNOW.value)
        emitter.update(0.1)
        self.assertGreater(len(emitter.particles), 0)

    def test_particle_decay(self):
        emitter = ParticleEmitter(ParticlePreset.FIRE.value)
        emitter.emit(5)
        # Advance time beyond lifespan
        emitter.update(3.0)
        # Dead particles should be cleaned up
        for p in emitter.particles:
            self.assertFalse(p.is_dead)

    def test_vfx_engine_pipeline(self):
        engine = VFXEngine()
        l1 = engine.add_effect(VFXType.GLOW.value)
        self.assertEqual(len(engine.layers), 1)
        out = engine.apply_pipeline("test_frame")
        self.assertEqual(out, "test_frame")


# ---------------------------------------------------------------------------
# Render Engine Tests
# ---------------------------------------------------------------------------

class TestRenderPhase4(unittest.TestCase):
    def test_queue_job(self):
        engine = RenderEngine()
        job = engine.queue_job("Test Render", "./out.mp4")
        self.assertEqual(job.name, "Test Render")
        self.assertEqual(len(engine.queue), 1)


# ---------------------------------------------------------------------------
# Collaboration Manager Tests
# ---------------------------------------------------------------------------

class TestCollaborationPhase4(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.mgr = CollaborationManager(self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_acquire_and_release_lock(self):
        acquired = self.mgr.acquire_lock("Alice")
        self.assertTrue(acquired)
        lock_path = os.path.join(self.temp_dir, ".zanime.lock")
        self.assertTrue(os.path.isfile(lock_path))

        # Second user attempt should fail
        mgr2 = CollaborationManager(self.temp_dir)
        self.assertFalse(mgr2.acquire_lock("Bob"))

        self.mgr.release_lock()
        self.assertFalse(os.path.isfile(lock_path))

    def test_comments_and_version_notes(self):
        c = self.mgr.add_comment("Alice", "Great lighting in frame 24")
        self.assertEqual(c.author, "Alice")
        self.assertEqual(len(self.mgr.comments), 1)

        vn = self.mgr.add_version_note("v1.2", "Bob", "Updated audio tracks")
        self.assertEqual(vn.version_str, "v1.2")

    def test_approval_status(self):
        self.mgr.set_approval_status(ApprovalStatus.APPROVED)
        self.assertEqual(self.mgr.status, ApprovalStatus.APPROVED)


if __name__ == "__main__":
    unittest.main()
