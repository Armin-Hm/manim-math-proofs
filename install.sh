#!/usr/bin/env bash
set -e

echo "===== INSTALL SYSTEM DEPENDENCIES ====="
sudo apt-get update
sudo apt-get install -y \
  pkg-config \
  libcairo2-dev \
  libpango1.0-dev \
  ffmpeg \
  sox

echo "===== CREATE VIRTUAL ENVIRONMENT ====="
python -m venv .venv

echo "===== UPGRADE PIP ====="
.venv/bin/python -m pip install --upgrade pip

echo "===== INSTALL MANIM AND VOICEOVER ====="
.venv/bin/python -m pip install --no-cache-dir \
  "manim==0.20.1" \
  "manim-voiceover[gtts]"

echo "===== TEST INSTALLATION ====="
.venv/bin/python -c "import manim; print('Manim OK:', manim.__version__)"
.venv/bin/python -c "from manim_voiceover import VoiceoverScene; from manim_voiceover.services.gtts import GTTSService; print('Voiceover OK')"
sox --version

echo "===== DONE ====="