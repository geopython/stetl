#!/bin/bash
#
# Build Stetl Docker image

# Optional: build with custom/your timezone and forced via --no-cache
# sudo docker build -t --no-cache --build-arg IMAGE_TIMEZONE="Europe/Amsterdam" justb4/stetl:latest .

sudo docker build -t justb4/stetl:latest .

