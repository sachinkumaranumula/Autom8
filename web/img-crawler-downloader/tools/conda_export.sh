#!/bin/bash
# From within sub module

conda env export --from-history | grep -v "^prefix: " > environment.yml
