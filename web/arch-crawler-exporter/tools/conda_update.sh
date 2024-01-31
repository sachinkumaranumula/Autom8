#!/bin/bash
# Usage: source conda_update.sh

# LOCK DID NOT WORK ON MACOSX DUE TO CASE INSENSITIVE FILESYSTEM
# Re-generate Conda lock file(s) based on environment.yml
# conda-lock -k explicit --conda mamba
# Update Conda packages based on re-generated lock file
# mamba update --file conda-linux-64.lock
# Update Conda
conda env update --file environment.yml --prune
# Update Poetry packages and re-generate poetry.lock
poetry update
