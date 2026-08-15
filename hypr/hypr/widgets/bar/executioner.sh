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
  [k]="kdenlive.AppImage"
  [w]="~/Downloads/winboat-0.9.0-x86_64.AppImage"
  [f]="~/Downloads/Freeter-2.7.1-beta-linux-x64/Freeter-2.7.1-beta-linux-x64/freeter"
  [p]="~/Downloads/krita-5.3.2.1-x86_64\(1\).AppImage"


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

