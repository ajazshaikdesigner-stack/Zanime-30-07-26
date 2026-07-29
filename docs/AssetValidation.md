# Environment & Prop Validation

To maintain strict project integrity, the `AssetValidator` enforces the following rules on Backgrounds and Props before they can be saved into a Package:

1. **Missing Name**: The asset must not be named "New Environment" or "New Prop".
2. **Missing Asset**: The AI generation must have successfully linked an `image_path`.
3. **Invalid Resolution**: Environments must conform to standard target constraints (e.g. 1920x1080).
