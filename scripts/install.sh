#!/usr/bin/env bash
set -euo pipefail

echo "📦 Installing root deps (concurrently)..."
npm install

echo "📦 Installing backend + agent + frontend..."
npm run install:all
