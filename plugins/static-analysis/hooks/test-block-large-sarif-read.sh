#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
hook="$root/block-large-sarif-read.sh"
work=$(mktemp -d "${TMPDIR:-/tmp}/sarif-read-hook.XXXXXX")
trap 'rm -rf "$work"' EXIT
small="$work/small.sarif"
large="$work/large.sarif"
mixed_case="$work/large.SaRiF"
other="$work/large.json"
printf '{}' >"$small"
truncate -s 204801 "$large"
truncate -s 204801 "$mixed_case"
truncate -s 204801 "$other"

run_hook() { jq -n --arg path "$1" '{tool_input:{file_path:$path}}' | "$hook"; }

[[ -z $(run_hook "$small") ]]
[[ -z $(run_hook "$other") ]]
run_hook "$large" | jq -e '.hookSpecificOutput.permissionDecision == "deny" and (.hookSpecificOutput.permissionDecisionReason | contains("sarif-parsing helper"))' >/dev/null
run_hook "$mixed_case" | jq -e '.hookSpecificOutput.permissionDecision == "deny"' >/dev/null
printf 'PASS large SARIF Read gate\n'
