#!/bin/bash
# From within sub module
# Usage: source conda_import.sh

if conda env list | grep arch-crawler-exporter >/dev/null 2>&1; then
    echo Conda environment exists
    source activate && conda activate arch-crawler-exporter
    poetry install
else
    conda env create --name arch-crawler-exporter --file environment.yml
fi
