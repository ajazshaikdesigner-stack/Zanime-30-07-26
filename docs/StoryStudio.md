# Story Studio

The Story Studio is Zanime's central hub for crafting the foundational narrative. It utilizes a split-pane layout to balance configurations with text processing.

## Components
- **StorySettingsDock**: Contains drop-downs for Language, Genre, Duration, Target Audience, Art Style, and Movie Style.
- **StoryEditor**: A rich text field for writing. Contains a "Story Tools" toolbar hooking directly into the `AIManager` queue to automatically *Rewrite, Expand, Shorten, Continue, Simplify, and Grammar Check* highlighted text blocks.
- **StoryAnalysisDock**: Displays real-time warnings from the `StoryValidator` engine alongside AI-extracted metadata.
- **StoryHistoryDock**: A continuous ledger of AI versions that can be reverted to.
