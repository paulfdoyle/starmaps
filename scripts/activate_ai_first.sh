#!/usr/bin/env bash
set -euo pipefail

# Copy or print the AI_first context launch prompt for quick activation.
prompt_path="$(dirname "$0")/../AI_first/context_launch_prompt.txt"

if [ ! -f "$prompt_path" ]; then
  echo "Prompt file not found at $prompt_path" >&2
  exit 1
fi

if command -v pbcopy >/dev/null 2>&1; then
  pbcopy < "$prompt_path"
  echo "AI_first context prompt copied to clipboard."
elif command -v xclip >/dev/null 2>&1; then
  xclip -selection clipboard < "$prompt_path"
  echo "AI_first context prompt copied to clipboard (xclip)."
elif command -v wl-copy >/dev/null 2>&1; then
  wl-copy < "$prompt_path"
  echo "AI_first context prompt copied to clipboard (wl-copy)."
else
  echo "Clipboard tool not found; printing prompt below:" >&2
  cat "$prompt_path"
fi
