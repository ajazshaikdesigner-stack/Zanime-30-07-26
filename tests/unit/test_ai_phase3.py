"""
Unit tests for Phase 3 AI subsystems.
Tests: OllamaProvider, AIHistoryManager, ConsistencyManager, PromptEngine.
"""

import json
import os
import tempfile
import time
import unittest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Prompt Engine Tests
# ---------------------------------------------------------------------------

class TestPromptEngine(unittest.TestCase):
    def setUp(self):
        from src.core.ai.prompt_engine import PromptEngine, PROMPT_TEMPLATES, STYLE_SUFFIXES
        self.engine = PromptEngine
        self.templates = PROMPT_TEMPLATES
        self.styles = STYLE_SUFFIXES

    def test_list_templates_returns_nonempty(self):
        templates = self.engine.list_templates()
        self.assertGreater(len(templates), 10, "Should have 10+ templates")

    def test_list_templates_by_category(self):
        char_templates = self.engine.list_templates(category="character")
        self.assertTrue(all(t["category"] == "character" for t in char_templates))

    def test_fill_template_substitutes_variables(self):
        result = self.engine.fill_template(
            "character_portrait",
            {"character_name": "Hana", "expression": "happy", "eye_color": "blue", "hair_color": "black"}
        )
        self.assertIn("Hana", result["positive"])
        self.assertIn("happy", result["positive"])
        self.assertNotIn("{character_name}", result["positive"])

    def test_fill_template_unknown_key_raises(self):
        with self.assertRaises(KeyError):
            self.engine.fill_template("nonexistent_template", {})

    def test_apply_style_appends_suffix(self):
        result = self.engine.apply_style("anime girl", "zanime_default")
        self.assertIn("ZANIME production art", result)

    def test_apply_style_no_duplicate(self):
        from src.core.ai.prompt_engine import STYLE_SUFFIXES
        suffix = STYLE_SUFFIXES["zanime_default"]
        already_styled = f"anime girl, {suffix}"
        result = self.engine.apply_style(already_styled, "zanime_default")
        # Should not double-add the suffix
        count = result.count(suffix)
        self.assertEqual(count, 1)

    def test_get_negative_returns_string(self):
        neg = self.engine.get_negative("standard")
        self.assertIsInstance(neg, str)
        self.assertGreater(len(neg), 5)

    def test_assemble_returns_positive_and_negative(self):
        result = self.engine.assemble("cute anime character", "zanime_default", "portrait")
        self.assertIn("positive", result)
        self.assertIn("negative", result)
        self.assertIn("ZANIME production art", result["positive"])

    def test_extract_variables(self):
        vars_ = self.engine.extract_variables("character_full_body")
        self.assertIn("character_name", vars_)
        self.assertIn("outfit", vars_)

    def test_background_template_wide_format(self):
        result = self.engine.fill_template(
            "background_exterior_day",
            {"location": "Tokyo street", "weather": "rainy", "season": "autumn"}
        )
        self.assertIn("Tokyo street", result["positive"])


# ---------------------------------------------------------------------------
# AI History Manager Tests
# ---------------------------------------------------------------------------

class TestAIHistoryManager(unittest.TestCase):
    def setUp(self):
        from src.core.events.event_bus import EventBus
        from src.core.ai.history_manager import AIHistoryManager

        self.event_bus = MagicMock(spec=EventBus)
        self.manager = AIHistoryManager(self.event_bus)
        self.temp_dir = tempfile.mkdtemp()
        self.manager.set_project_dir(self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_record_creates_entry(self):
        entry = self.manager.record(
            task_type="text",
            prompt="Write a story",
            output_path="",
            model_name="llama3:8b",
            provider="llm",
        )
        self.assertEqual(entry.task_type, "text")
        self.assertEqual(entry.prompt, "Write a story")
        self.assertIsNotNone(entry.entry_id)

    def test_get_all_returns_recorded(self):
        self.manager.record(task_type="text", prompt="p1", output_path="")
        self.manager.record(task_type="image", prompt="p2", output_path="")
        all_entries = self.manager.get_all()
        self.assertEqual(len(all_entries), 2)

    def test_filter_by_type(self):
        self.manager.record(task_type="text", prompt="text", output_path="")
        self.manager.record(task_type="image", prompt="img", output_path="")
        images = self.manager.get_all(task_type="image")
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0].task_type, "image")

    def test_get_recent_returns_last_n(self):
        for i in range(10):
            self.manager.record(task_type="text", prompt=f"p{i}", output_path="")
        recent = self.manager.get_recent(limit=3)
        self.assertEqual(len(recent), 3)

    def test_toggle_favorite(self):
        entry = self.manager.record(task_type="text", prompt="p", output_path="")
        result = self.manager.toggle_favorite(entry.entry_id)
        self.assertTrue(result)
        result2 = self.manager.toggle_favorite(entry.entry_id)
        self.assertFalse(result2)

    def test_delete_entry(self):
        entry = self.manager.record(task_type="text", prompt="p", output_path="")
        deleted = self.manager.delete(entry.entry_id)
        self.assertTrue(deleted)
        self.assertEqual(len(self.manager.get_all()), 0)

    def test_persistence_across_reload(self):
        self.manager.record(task_type="music", prompt="jazz", output_path="/music.wav")
        # Create new manager and load from same dir
        from src.core.ai.history_manager import AIHistoryManager
        new_manager = AIHistoryManager(self.event_bus)
        new_manager.set_project_dir(self.temp_dir)
        entries = new_manager.get_all()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].task_type, "music")
        self.assertEqual(entries[0].output_path, "/music.wav")

    def test_fifo_eviction_at_max(self):
        from src.core.ai.history_manager import _MAX_ENTRIES
        for i in range(_MAX_ENTRIES + 5):
            self.manager.record(task_type="text", prompt=f"p{i}", output_path="")
        self.assertEqual(len(self.manager.get_all()), _MAX_ENTRIES)

    def test_event_published_on_record(self):
        self.manager.record(task_type="text", prompt="p", output_path="")
        self.event_bus.publish.assert_called()


# ---------------------------------------------------------------------------
# Consistency Manager Tests
# ---------------------------------------------------------------------------

class TestConsistencyManager(unittest.TestCase):
    def setUp(self):
        from src.core.ai.consistency_manager import ConsistencyManager
        self.manager = ConsistencyManager()
        self.temp_dir = tempfile.mkdtemp()
        self.manager.set_project_dir(self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_set_and_get_anchor(self):
        anchor = self.manager.set_anchor(
            character_uuid="uuid-001",
            character_name="Hana",
            locked_seed=42,
            dna_prompt="18-year-old female, oval face",
        )
        retrieved = self.manager.get_anchor("uuid-001")
        self.assertEqual(retrieved.character_name, "Hana")
        self.assertEqual(retrieved.locked_seed, 42)

    def test_apply_injects_dna_prompt(self):
        self.manager.set_anchor("u1", "Kenji", dna_prompt="young male, short hair")
        result = self.manager.apply("u1", "anime character portrait")
        self.assertIn("young male, short hair", result)
        self.assertIn("anime character portrait", result)

    def test_inject_params_sets_seed(self):
        self.manager.set_anchor("u1", "Aya", locked_seed=12345)
        params = self.manager.inject_params("u1", {"steps": 25})
        self.assertEqual(params["seed"], 12345)

    def test_apply_no_anchor_returns_original(self):
        result = self.manager.apply("nonexistent-uuid", "my prompt")
        self.assertEqual(result, "my prompt")

    def test_lock_and_unlock(self):
        self.manager.set_anchor("u1", "X")
        self.manager.lock_anchor("u1")
        self.assertTrue(self.manager.get_anchor("u1").is_locked)
        self.manager.unlock_anchor("u1")
        self.assertFalse(self.manager.get_anchor("u1").is_locked)

    def test_delete_anchor(self):
        self.manager.set_anchor("u1", "X")
        result = self.manager.delete_anchor("u1")
        self.assertTrue(result)
        self.assertIsNone(self.manager.get_anchor("u1"))

    def test_persistence(self):
        self.manager.set_anchor("u2", "Miko", locked_seed=99)
        from src.core.ai.consistency_manager import ConsistencyManager
        new_mgr = ConsistencyManager()
        new_mgr.set_project_dir(self.temp_dir)
        anchor = new_mgr.get_anchor("u2")
        self.assertEqual(anchor.character_name, "Miko")
        self.assertEqual(anchor.locked_seed, 99)

    def test_build_dna_prompt(self):
        from src.core.ai.consistency_manager import ConsistencyManager
        from src.models.character_model import CharacterDNA
        dna = CharacterDNA(age=18, gender="Female", face_shape="Oval",
                           eye_shape="Almond", eye_color="Blue",
                           hair_style="Long", hair_color="Black", skin_tone="Fair")
        prompt = ConsistencyManager.build_dna_prompt(dna)
        self.assertIn("female", prompt.lower())
        self.assertIn("blue", prompt.lower())
        self.assertIn("long black hair", prompt.lower())


# ---------------------------------------------------------------------------
# AI History Model Tests
# ---------------------------------------------------------------------------

class TestAIHistoryModel(unittest.TestCase):
    def test_to_dict_round_trip(self):
        from src.models.ai_history_model import AIHistoryEntry, AITaskType
        entry = AIHistoryEntry(
            task_type=AITaskType.IMAGE.value,
            prompt="test prompt",
            seed=42,
            model_name="sdxl",
        )
        d = entry.to_dict()
        restored = AIHistoryEntry.from_dict(d)
        self.assertEqual(restored.prompt, "test prompt")
        self.assertEqual(restored.seed, 42)
        self.assertEqual(restored.model_name, "sdxl")
        self.assertEqual(restored.task_type, AITaskType.IMAGE.value)

    def test_default_entry_id_is_unique(self):
        from src.models.ai_history_model import AIHistoryEntry
        e1 = AIHistoryEntry()
        e2 = AIHistoryEntry()
        self.assertNotEqual(e1.entry_id, e2.entry_id)


# ---------------------------------------------------------------------------
# OllamaProvider Connection Tests (mocked HTTP)
# ---------------------------------------------------------------------------

class TestOllamaProvider(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_load_success_when_model_listed(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "models": [{"name": "llama3:8b"}]
        }).encode()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        from src.core.ai.providers.ollama_provider import OllamaProvider
        provider = OllamaProvider()
        result = provider.load("llama3:8b", {})
        self.assertTrue(result)
        self.assertTrue(provider.is_loaded)

    @patch("urllib.request.urlopen")
    def test_load_fails_on_connection_error(self, mock_urlopen):
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        from src.core.ai.providers.ollama_provider import OllamaProvider
        provider = OllamaProvider()
        result = provider.load("llama3:8b", {})
        self.assertFalse(result)
        self.assertFalse(provider.is_loaded)

    @patch("urllib.request.urlopen")
    def test_execute_returns_text(self, mock_urlopen):
        # Load mock
        load_resp = MagicMock()
        load_resp.read.return_value = json.dumps({"models": [{"name": "llama3:8b"}]}).encode()
        load_resp.__enter__ = lambda s: s
        load_resp.__exit__ = MagicMock(return_value=False)

        # Execute mock
        exec_resp = MagicMock()
        exec_resp.read.return_value = json.dumps({
            "response": "Once upon a time in Tokyo...",
            "context": [1, 2, 3],
            "eval_count": 50,
            "prompt_eval_count": 10,
        }).encode()
        exec_resp.__enter__ = lambda s: s
        exec_resp.__exit__ = MagicMock(return_value=False)

        mock_urlopen.side_effect = [load_resp, exec_resp]

        from src.core.ai.providers.ollama_provider import OllamaProvider
        provider = OllamaProvider()
        provider.load("llama3:8b", {})
        result = provider.execute("Write a story", {})

        self.assertIn("text", result)
        self.assertEqual(result["text"], "Once upon a time in Tokyo...")
        self.assertEqual(result["tokens"], 50)

    def test_execute_raises_when_not_loaded(self):
        from src.core.ai.providers.ollama_provider import OllamaProvider
        provider = OllamaProvider()
        with self.assertRaises(RuntimeError):
            provider.execute("test", {})

    def test_unload_clears_state(self):
        from src.core.ai.providers.ollama_provider import OllamaProvider
        provider = OllamaProvider()
        provider.is_loaded = True
        provider._context_tokens = [1, 2, 3]
        provider.unload()
        self.assertFalse(provider.is_loaded)
        self.assertEqual(provider._context_tokens, [])

    def test_memory_footprint_known_model(self):
        from src.core.ai.providers.ollama_provider import OllamaProvider
        p = OllamaProvider()
        p._model_name = "llama3:8b"
        self.assertEqual(p.memory_footprint(), 5000)

    @patch("urllib.request.urlopen")
    def test_list_local_models(self, mock_urlopen):
        resp = MagicMock()
        resp.read.return_value = json.dumps({
            "models": [{"name": "llama3:8b"}, {"name": "mistral:7b"}]
        }).encode()
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = resp

        from src.core.ai.providers.ollama_provider import OllamaProvider
        p = OllamaProvider()
        models = p.list_local_models()
        self.assertIn("llama3:8b", models)
        self.assertIn("mistral:7b", models)


if __name__ == "__main__":
    unittest.main()
