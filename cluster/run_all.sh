#!/usr/bin/env bash
# run_all.sh — run EVERY document in inputs/ through run.py for ONE model.
#
# Runs both pipeline modes per document (graphrag + bypass) by default.
# Reuses the JSON cache, so re-runs are cheap unless FORCE=1.
#
# Usage:
#   ./cluster/run_all.sh qwen2.5:7b
#   MODE=bypass ./cluster/run_all.sh qwen2.5:14b
#   FORCE=1 MODE=both ./cluster/run_all.sh qwen2.5:7b
#
# Env vars:
#   MODE         both | graphrag | bypass     (default: both)
#   FORCE        1 to re-extract (graphrag)    (default: 0)
#   INPUT_GLOB   files to run                  (default: inputs/*.md)
#   OLLAMA_URL   ollama endpoint              (default: http://localhost:11434)
#   NO_NEO4J     1 to skip Neo4j write        (default: 1 — cluster-friendly)
#   NEO4J_URI    bolt uri (only if NO_NEO4J=0)(default: bolt://localhost:7687)
#   NEO4J_PASSWORD                            (default: password)
#   EXTRA_ARGS   passed straight to run.py    (e.g. "--judge")
set -euo pipefail

MODEL="${1:?usage: run_all.sh <model>   e.g. qwen2.5:7b}"
MODE="${MODE:-both}"
FORCE="${FORCE:-0}"
NO_NEO4J="${NO_NEO4J:-1}"
INPUT_GLOB="${INPUT_GLOB:-inputs/*.md}"
OUTPUTS_DIR="${OUTPUTS_DIR:-outputs}"
CACHE_DIR="${CACHE_DIR:-cache}"
OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
NEO4J_URI="${NEO4J_URI:-bolt://localhost:7687}"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-password}"
EXTRA_ARGS="${EXTRA_ARGS:-}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

force_flag=""
[[ "$FORCE" == "1" ]] && force_flag="--force"
neo4j_flag=""
[[ "$NO_NEO4J" == "1" ]] && neo4j_flag="--no-neo4j"

# Build mode list
modes=()
case "$MODE" in
  all)      modes=(graphrag bypass zeroshot) ;;
  both)     modes=(graphrag bypass) ;;
  graphrag) modes=(graphrag) ;;
  bypass)   modes=(bypass) ;;
  zeroshot) modes=(zeroshot) ;;
  *) echo "MODE must be all|both|graphrag|bypass|zeroshot" >&2; exit 1 ;;
esac

shopt -s nullglob
files=( $INPUT_GLOB )
shopt -u nullglob
if [[ ${#files[@]} -eq 0 ]]; then
  echo "No input files match: $INPUT_GLOB" >&2
  exit 1
fi

echo "=================================================="
echo " model : $MODEL"
echo " modes : ${modes[*]}"
echo " docs  : ${#files[@]}"
echo "=================================================="

fail=0
for f in "${files[@]}"; do
  for m in "${modes[@]}"; do
    echo
    echo ">>> [$m] $f"
    mode_flag=""
    [[ "$m" == "bypass" ]]   && mode_flag="--bypass"
    [[ "$m" == "zeroshot" ]] && mode_flag="--zeroshot"
    if uv run python run.py \
        --input "$f" \
        --model "$MODEL" \
        --ollama-url "$OLLAMA_URL" \
        --neo4j-uri "$NEO4J_URI" \
        --neo4j-password "$NEO4J_PASSWORD" \
        --outputs-dir "$OUTPUTS_DIR" \
        --cache-dir "$CACHE_DIR" \
        $mode_flag $neo4j_flag $force_flag $EXTRA_ARGS; then
      echo "<<< OK   [$m] $f"
    else
      echo "<<< FAIL [$m] $f" >&2
      fail=1
    fi
  done
done

echo
echo "All done. exit=$fail (outputs/ + cache/ updated)"
exit $fail
