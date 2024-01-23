#!/bin/bash
# From within sub module

conda env create --name img-crawler-downloader --file environment.yml
conda activate img-crawler-downloader
poetry install
