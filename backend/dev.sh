#!/usr/bin/env bash
set -euo pipefail

# dev.sh - Convenience launcher for FitPlanner MVP
# Usage:
#   ./dev.sh backend   # Run FastAPI locally with venv
#   ./dev.sh docker    # Run backend via docker compose
#   ./dev.sh ios       # Generate and open Xcode project
#   ./dev.sh help      # Show help

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"
IOS_DIR="$REPO_ROOT/ios"

function usage() {
  cat <<EOF
FitPlanner dev helper

Commands:
  backend   Create venv, install deps, run uvicorn on :8000
  docker    docker compose up --build -d (backend)
  ios       Install xcodegen (if missing), generate Xcode project, open it
  help      Show this help
EOF
}

cmd=${1:-help}
case "$cmd" in
  backend)
    bash "$BACKEND_DIR/run.sh"
    ;;
  docker)
    pushd "$BACKEND_DIR" >/dev/null
    cp -n .env.example .env 2>/dev/null || true
    docker compose up --build -d
    popd >/dev/null
    echo "Backend is starting in Docker. Visit http://localhost:8000/health"
    ;;
  ios)
    bash "$IOS_DIR/bootstrap.sh"
    ;;
  help|--help|-h)
    usage
    ;;
  *)
    echo "Unknown command: $cmd" >&2
    usage
    exit 1
    ;;
 esac
