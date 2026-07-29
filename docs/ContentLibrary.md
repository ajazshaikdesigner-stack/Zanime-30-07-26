# Content Library

The Content Ecosystem manages thousands of pre-loaded assets (Characters, Props, Environments, and SFX) ensuring creators can build movies without leaving the Zanime application.

## Asset Manager
The `AssetManager` acts as the central in-memory registry. It parses the default payloads upon boot (currently mocked at ~4000 assets). 
To prevent UI lag, the Manager implements an internal `SearchEngine` featuring Lazy Loading.

## UI Integration
- **AssetCategoriesDock**: Navigates hierarchical trees of Asset Types (e.g. Characters, Audio) and customized user Collections (Favorites).
- **AssetBrowserWidget**: A highly optimized QListWidget configured as an IconMode grid.
- **AssetInformationDock**: Inspector displaying UUID, Authorship, Dependencies, and Licensing metadata.
