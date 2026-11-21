#!/bin/sh
# Installs the gevolve skill and its sub-agent for the current user (Claude Code).
set -eu
ICI="$(cd "$(dirname "$0")" && pwd)"
CIBLE="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
if [ -e "$CIBLE/skills/gevolve" ]; then
  echo "Already installed: $CIBLE/skills/gevolve. Move it away first, then run this script again." >&2
  exit 1
fi
mkdir -p "$CIBLE/skills" "$CIBLE/agents"
cp -R "$ICI/skills/gevolve" "$CIBLE/skills/gevolve"
cp "$ICI/agents/gevolve-mutateur.md" "$CIBLE/agents/gevolve-mutateur.md"
echo "Installed. Restart Claude Code, then type /gevolve."
