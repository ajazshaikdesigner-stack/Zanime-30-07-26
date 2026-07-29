# Story Validation Engine

The `StoryValidator` constantly scans the active `StoryModel.content` to prevent the user from passing defective data into the subsequent Screenplay Studio phase.

## Validation Checks
1. **Incomplete Checks**: Flags if the text is under 50 words.
2. **Missing Ending**: Flags if the final character lacks proper punctuation (`.`, `?`, `!`, `"`, `'`).
3. **Empty Characters**: Alerts if the AI failed to extract any characters from the text payload.

Warnings are pushed directly to the `StoryAnalysisDock`.
