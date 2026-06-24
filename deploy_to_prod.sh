#!/bin/bash

echo "Packing and deploying code to Production..."

# Define directories
DEV_DIR="$HOME/Projects/pokemon-index/dev/"
PROD_DIR="$HOME/Projects/pokemon-index/prod/"

# Rsync copies everything OVER, but EXCLUDES your Git history, dev database, and secrets
rsync -av --delete \
    --exclude='.git/' \
    --exclude='.gitignore' \
    --exclude='deploy_to_prod.sh' \
    --exclude='pokemon_index.db' \
    --exclude='state.json' \
    --exclude='.env' \
    --exclude='venv/' \
    --exclude='__pycache__/' \
    --exclude='logs/' \
    "$DEV_DIR" "$PROD_DIR"

echo "Deployment complete! Production is now running the latest code."