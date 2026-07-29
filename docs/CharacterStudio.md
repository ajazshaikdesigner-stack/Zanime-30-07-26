# Character Studio

The Character Studio is a massive management module for configuring character metadata, testing poses, and generating models.

## Data Structures
- **CharacterDNA**: Stores biographical metadata (age, weight, height, ethnicity).
- **Outfits**: Characters can have unlimited outfits, which bundle clothing, shoes, props, and hairstyles.
- **ModelSheet**: Stores path bindings to the 8 standard rotation angles for a character.

## Core UI
- `CharactersWorkspace`: The main central container for the Character Studio.
- `CharacterLibraryDock`: Provides a grid/list to select active characters. Supports Search and Categories.
- `CharacterPropertiesDock`: The main editor. It utilizes QTabWidget to segment DNA, Outfits, and Accessories.
- `CharacterPreview`: A QGraphicsView capable of simulating rotations and loading specific Expression/Pose overlays.
