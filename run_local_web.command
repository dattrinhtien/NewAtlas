#!/usr/bin/env bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR/web" || exit 1

clear
echo "=========================================================="
echo "      🚀 KHỞI ĐỘNG NEWATLAS 3D LOCAL SERVER              "
echo "=========================================================="
echo ""
python3 server.py 8080
