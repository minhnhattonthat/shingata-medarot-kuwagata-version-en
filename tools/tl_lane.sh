#!/bin/sh
# tl_lane.sh "b008 b009 b010" "b011 b012" ...: one lane of translator runs; each argument is one codex session
# (tools/codex_tl.py tl ...), run one after another. Start several lanes as background jobs to run them in parallel.
cd "$(dirname "$0")/.." || exit 1
for group in "$@"; do
    python -X utf8 tools/codex_tl.py tl $group
done
