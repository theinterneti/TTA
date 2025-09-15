# GitHub Repository Setup Instructions

Follow these steps to push this repository to GitHub:

1. Create a new repository on GitHub:
   - Go to https://github.com/new
   - Name: `TTA`
   - Description: `TTA meta-repository for managing tta.dev and TTA.prototype`
   - Choose public or private as needed
   - Do NOT initialize with README, .gitignore, or license
   - Click "Create repository"

2. Add the remote and push:
   ```bash
   git remote add origin https://github.com/theinterneti/TTA.git
   git push -u origin main
   ```

3. Initialize the submodules:
   ```bash
   ./setup.sh
   ```

4. Push the submodules:
   ```bash
   git push --recurse-submodules=on-demand
   ```

## Working with Submodules

### Cloning the Repository with Submodules

To clone this repository with all submodules:

```bash
git clone --recurse-submodules https://github.com/theinterneti/TTA.git
```

### Updating Submodules

To update all submodules to their latest versions:

```bash
git submodule update --remote --merge
git add .
git commit -m "Update submodules"
git push
```

### Making Changes to Submodules

1. Navigate to the submodule directory:
   ```bash
   cd tta.dev  # or TTA.prototype
   ```

2. Make your changes and commit them:
   ```bash
   git add .
   git commit -m "Your commit message"
   git push
   ```

3. Return to the parent repository and update the submodule reference:
   ```bash
   cd ..
   git add tta.dev  # or TTA.prototype
   git commit -m "Update tta.dev submodule reference"
   git push
   ```
