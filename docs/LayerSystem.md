# Layer System

Zanime implements a strict enum-based layering system to prevent messy rendering logic. 

## Z-Order Definition
0. `FAR_BACKGROUND` (Skyboxes)
1. `BACKGROUND` (Environments)
2. `MIDDLE_GROUND` (Distant Props)
3. `CHARACTERS` (Actors)
4. `FOREGROUND` (Close-up Props)
5. `EFFECTS` (Particles)
6. `CAMERA` (Lens flares)
7. `LIGHTING` (Global illumination maps)
8. `OVERLAY` (Color grading LUTs)
9. `UI` (Guides, Safe Areas)
