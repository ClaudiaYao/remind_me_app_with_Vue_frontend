#!/bin/bash
set -e  # exit immediately if any command fails

# Update
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install -y docker.io
sudo systemctl enable --now docker

# Install Docker Compose
sudo apt install -y docker-compose

echo "✅ Docker Compose installed."


# Step 2: Clone project repository
REPO_PATH="$HOME/remind_me_app_with_Vue_frontend/backend"

if [ -d "$REPO_PATH" ]; then
    cd "$REPO_PATH" || exit 1
else
    echo "Error: Repository path does not exist."
    exit 1
fi
echo "Current working directory: $(pwd)"

# Step 3: Create .env file
echo "🔑 Create your .env file. Enter contents and press Ctrl+D when done:"
cat > .env

echo "✅ Setup complete. .env file created and project cloned."