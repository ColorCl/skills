#!/usr/bin/env bash
# Deny only raw Read calls that would put more than 200 KiB of SARIF in context.
set -euo pipefail

input=$(cat)
path=$(jq -r '.tool_input.file_path // empty' <<<"$input") || exit 0
shopt -s nocasematch
case "$path" in
  *.sarif) ;;
  *) exit 0 ;;
esac
[[ -f "$path" ]] || exit 0

bytes=$(wc -c <"$path" | tr -d '[:space:]')
((bytes > 204800)) || exit 0

jq -n --arg path "$path" --argjson bytes "$bytes" \
  '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:("Do not Read " + $path + " (" + ($bytes|tostring) + " bytes). Use the sarif-parsing helper summary/filter/dedupe/diff commands for compact output; inspect a specific record only after narrowing it.")}}'
