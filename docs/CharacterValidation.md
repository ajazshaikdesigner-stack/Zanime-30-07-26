# Character Validation

The `CharacterValidator` ensures characters are ready for animation by verifying constraints:
1. Missing default Outfits.
2. Missing minimal Expressions or Poses.
3. Missing or default Names ("New Character").
4. Broken Asset paths in the Model Sheet.

Any broken rules should block the character from being imported into the Scene Composer.
