#!/usr/bin/env bash
# Exit on error
set -o errexit

# Pip ni yangilash
pip install --upgrade pip

# Kutubxonalarni o'rnatish
pip install -r requirements.txt
