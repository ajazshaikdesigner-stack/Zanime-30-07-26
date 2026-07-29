import pytest
import os
from src.models.world_model import EnvironmentDNA, PropModel
from src.core.services.asset_validator import AssetValidator
from src.core.services.world_io import WorldIO

def test_asset_validator_environment():
    env = EnvironmentDNA()
    warnings = AssetValidator.validate_environment(env)
    assert len(warnings) >= 2  # Missing name and image
    
    env.name = "My Forest"
    env.image_path = "path.png"
    env.resolution = "1920x1080"
    
    warnings = AssetValidator.validate_environment(env)
    assert len(warnings) == 0
    
def test_asset_validator_prop():
    prop = PropModel()
    warnings = AssetValidator.validate_prop(prop)
    assert len(warnings) >= 2
    
    prop.name = "Sword"
    prop.image_path = "sword.png"
    warnings = AssetValidator.validate_prop(prop)
    assert len(warnings) == 0

def test_world_io(tmp_path):
    env = EnvironmentDNA(name="SaveEnv", style="Realistic")
    env_file = os.path.join(tmp_path, "env.json")
    assert WorldIO.export_environment_json(env, env_file) is True
    assert os.path.exists(env_file)
    
    prop = PropModel(name="SaveProp", material="Metal")
    prop_file = os.path.join(tmp_path, "prop.json")
    assert WorldIO.export_prop_json(prop, prop_file) is True
    assert os.path.exists(prop_file)
