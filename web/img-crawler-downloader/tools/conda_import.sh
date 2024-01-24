#!/bin/bash
# From within sub module
# Usage: source conda_import.sh

if conda env list | grep img-crawler-downloader >/dev/null 2>&1; then
    echo Conda environment exists
    source activate && conda activate img-crawler-downloader
    poetry install
else
    conda env create --name img-crawler-downloader --file environment.yml
fi
