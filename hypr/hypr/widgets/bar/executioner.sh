#!/bin/sh

set -euo pipefail



declare -A COMMANDS=(

##########################################################
##    COMMAND SHORTCUTS HERE     #########################
##########################################################

  [oo]="obs"
  [or]="obs --startrecording"
  [ob]="obsidian"
  [d]="vesktop"
  [z]="zen-browser"
  [q]="qutebrowser"


##########################################################
##########################################################

  )



input="$*"
key="$1"

shift || true

cmd="${COMMANDS[$key]:-}"

if [[ -z "$cmd" ]]; then
  exec "$SHELL" -lc "$input"
else
  echo "${args[@]}" "$@"
  args=($cmd)
  exec "${args[@]}" "$@"
fi

