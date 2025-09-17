#!/usr/bin/env bash
# Install Python deps
pip install -r requirements.txt

# Build frontend
cd public-health-chatbot
npm install
npm run build
cd ..

# Replace static with fresh build
rm -rf static
mkdir static
cp -r public-health-chatbot/build/* static/