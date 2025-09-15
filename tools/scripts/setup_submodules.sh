#!/bin/bash

# Setup submodules script
# This script helps set up the TTA.dev and TTA.prototype repositories as submodules

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}TTA Submodules Setup Script${NC}"
echo "=============================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: git is not installed. Please install git and try again.${NC}"
    exit 1
fi

# Function to create a repository if it doesn't exist
create_repo_if_needed() {
    local repo_name=$1
    local repo_url="https://github.com/theinterneti/$repo_name"

    # Check if the repository exists
    status_code=$(curl -s -o /dev/null -w "%{http_code}" $repo_url)

    if [ "$status_code" == "404" ]; then
        echo -e "${YELLOW}Repository $repo_name doesn't exist on GitHub.${NC}"
        echo "Would you like to create it? (y/n)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            echo "Creating repository $repo_name..."
            # You'll need to use GitHub API or gh CLI to create the repository
            # For now, we'll provide instructions
            echo -e "${YELLOW}Please create the repository manually at:${NC}"
            echo "https://github.com/new"
            echo "Repository name: $repo_name"
            echo "Press Enter when done..."
            read -r
        else
            echo "Skipping repository creation for $repo_name."
            return 1
        fi
    else
        echo -e "${GREEN}Repository $repo_name exists on GitHub.${NC}"
    fi

    return 0
}

# Setup tta.dev submodule
setup_submodule() {
    local repo_name=$1
    local local_path=$2

    echo -e "${GREEN}Setting up $repo_name submodule...${NC}"

    # Check if the repository exists on GitHub
    if create_repo_if_needed "$repo_name"; then
        # Check if the directory exists
        if [ -d "$local_path" ]; then
            echo "$local_path directory exists."

            # Check if it's already a git repository
            if [ -d "$local_path/.git" ]; then
                echo "$local_path is already a git repository."

                # Check if it has a remote
                if git -C "$local_path" remote -v | grep -q origin; then
                    echo "$local_path already has a remote."
                else
                    echo "Adding remote to $local_path..."
                    git -C "$local_path" remote add origin "https://github.com/theinterneti/$repo_name.git"
                fi

                # Push to GitHub if needed
                echo "Would you like to push $local_path to GitHub? (y/n)"
                read -r response
                if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                    echo "Pushing $local_path to GitHub..."
                    git -C "$local_path" push -u origin main || git -C "$local_path" push -u origin master
                fi
            else
                echo "Initializing git repository in $local_path..."
                git -C "$local_path" init
                git -C "$local_path" add .
                git -C "$local_path" commit -m "Initial commit"
                git -C "$local_path" remote add origin "https://github.com/theinterneti/$repo_name.git"
                git -C "$local_path" push -u origin main
            fi
        else
            echo "$local_path directory doesn't exist. Creating it..."
            mkdir -p "$local_path"

            # Copy template files
            echo "Copying template files to $local_path..."
            cp -r "templates/$repo_name/." "$local_path/"

            # Initialize git repository
            git -C "$local_path" init
            git -C "$local_path" add .
            git -C "$local_path" commit -m "Initial commit"
            git -C "$local_path" remote add origin "https://github.com/theinterneti/$repo_name.git"
            git -C "$local_path" push -u origin main
        fi

        # Add as submodule
        echo "Adding $repo_name as submodule..."
        git submodule add "https://github.com/theinterneti/$repo_name.git" "$local_path"
        git add .gitmodules "$local_path"
        git commit -m "Add $repo_name as submodule"
        git push
    else
        echo -e "${YELLOW}Skipping $repo_name submodule setup.${NC}"
    fi
}

# Setup submodules
setup_submodule "tta.dev" "tta.dev"
setup_submodule "TTA.prototype" "TTA.prototype"

echo -e "${GREEN}Submodules setup complete!${NC}"
echo "You can now use the TTA environment with Docker."
