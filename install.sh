#!/usr/bin/env bash
set -e

echo "===== UPDATE SYSTEM ====="
sudo apt-get update

echo "===== INSTALL SYSTEM DEPENDENCIES ====="
sudo apt-get install -y \
  python3-venv \
  python3-pip \
  build-essential \
  python3-dev \
  libcairo2-dev \
  libpango1.0-dev \
  ffmpeg \
  sox \
  libsox-fmt-all \
  freeglut3-dev \
  pkg-config \
  libffi-dev \
  libxml2-dev \
  zlib1g-dev \
  texlive-latex-base \
  texlive-latex-extra \
  texlive-fonts-recommended \
  dvisvgm \
  cm-super

echo "===== CREATE PYTHON ENV ====="
rm -rf .venv
python3 -m venv .venv

echo "===== UPGRADE PIP ====="
.venv/bin/python -m pip install --upgrade pip setuptools wheel

echo "===== INSTALL MANIM ====="
.venv/bin/python -m pip install --no-cache-dir \
  "manim==0.20.1" \
  "manim-voiceover[gtts]"

echo "===== TEST INSTALLATION ====="
.venv/bin/python -c "import manim; print('Manim OK:', manim.__version__)"
.venv/bin/python -c "from manim_voiceover import VoiceoverScene; from manim_voiceover.services.gtts import GTTSService; print('Voiceover OK')"

echo "===== DONE ====="
