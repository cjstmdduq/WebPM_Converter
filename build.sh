#!/bin/bash
set -e

cd "$(dirname "$0")"
source venv/bin/activate

pyinstaller \
  --windowed \
  --name "WebPM Converter" \
  --icon icon.icns \
  --osx-bundle-identifier "com.internal.webpm-converter" \
  --noconfirm \
  app.py

echo ""
echo "빌드 완료: dist/WebPM Converter.app"
