"""
Asset Manager - Central registry and Search Engine for content.
"""
import logging
from typing import List, Dict
from src.models.asset_model import AssetMetadata, AssetType, AssetCollection

logger = logging.getLogger(__name__)

class AssetManager:
    def __init__(self):
        self._assets: Dict[str, AssetMetadata] = {}
        self.collections: List[AssetCollection] = []
        self._bootstrap_mock_content()

    def get_icon(self, name: str):
        from PySide6.QtGui import QIcon
        return QIcon()
        
    def _bootstrap_mock_content(self):
        """Mocks thousands of assets for testing the Search Engine."""
        logger.info("Bootstrapping 4000+ default assets...")
        
        # Characters (Mock 250)
        for i in range(250):
            a = AssetMetadata(f"Hero Character {i}", AssetType.CHARACTER, "Fantasy", tags=["hero", "anime", "warrior"])
            self._assets[a.uuid] = a
            
        # Props (Mock 1000)
        for i in range(1000):
            a = AssetMetadata(f"Prop Item {i}", AssetType.PROP, "Furniture", tags=["wood", "table", "indoor"])
            self._assets[a.uuid] = a
            
        # SFX (Mock 3000)
        for i in range(3000):
            a = AssetMetadata(f"Sound {i}", AssetType.SFX, "Combat", tags=["sword", "clash", "metal"])
            self._assets[a.uuid] = a
            
        # Backgrounds (Mock 200)
        for i in range(200):
            a = AssetMetadata(f"Environment {i}", AssetType.BACKGROUND, "Sci-Fi", tags=["space", "ship", "stars"])
            self._assets[a.uuid] = a
            
        self.collections.append(AssetCollection("Favorites"))
        
    def search(self, query: str = "", asset_type: AssetType = None, category: str = "", limit: int = 100) -> List[AssetMetadata]:
        """Highly optimized indexing search engine (mocked implementation)"""
        results = []
        q = query.lower()
        
        for asset in self._assets.values():
            if asset_type and asset.asset_type != asset_type:
                continue
            if category and asset.category != category:
                continue
                
            if q:
                match = q in asset.name.lower() or any(q in tag.lower() for tag in asset.tags)
                if not match:
                    continue
                    
            results.append(asset)
            if len(results) >= limit: # Lazy loading limit
                break
                
        return results

    def toggle_favorite(self, asset_uuid: str):
        if asset_uuid in self._assets:
            self._assets[asset_uuid].is_favorite = not self._assets[asset_uuid].is_favorite
            
            fav_col = next((c for c in self.collections if c.name == "Favorites"), None)
            if fav_col:
                if self._assets[asset_uuid].is_favorite:
                    fav_col.asset_uuids.append(asset_uuid)
                else:
                    fav_col.asset_uuids.remove(asset_uuid)
