import pytest
from src.core.managers.asset_manager import AssetManager
from src.models.asset_model import AssetType

def test_asset_manager_search():
    manager = AssetManager()
    
    # Test broad search
    results = manager.search(asset_type=AssetType.CHARACTER)
    assert len(results) > 0
    assert results[0].asset_type == AssetType.CHARACTER
    
    # Test tag search
    results_tag = manager.search(query="warrior")
    assert len(results_tag) > 0
    assert any("warrior" in a.tags for a in results_tag)
    
    # Test favorite toggle
    asset_uuid = results[0].uuid
    manager.toggle_favorite(asset_uuid)
    assert manager._assets[asset_uuid].is_favorite == True
    
    fav_col = next((c for c in manager.collections if c.name == "Favorites"), None)
    assert asset_uuid in fav_col.asset_uuids
    
    manager.toggle_favorite(asset_uuid)
    assert manager._assets[asset_uuid].is_favorite == False
    assert asset_uuid not in fav_col.asset_uuids
