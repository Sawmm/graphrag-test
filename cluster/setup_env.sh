#!/usr/bin/env bash
# setup_env.sh — one-time setup on a VU cluster LOGIN node (has internet).
#
# Installs uv, the project venv, and a local Ollama binary into scratch, then
# pre-pulls a model so the compute node (which often has NO internet) can run
# straight from the shared scratch cache.
#
# Run once after cloning the repo on the cluster:
#   bash cluster/setup_env.sh qwen2.5:7b          # also pre-pulls this model
#   bash cluster/setup_env.sh                     # env only, no model
set -euo pipefail

MODEL="${1:-}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# DAS: /var/scratch/$USER (shared)  ·  Snellius: use a persistent scratch path
SCRATCH="${SCRATCH_DIR:-/var/scratch/$USER}"
[[ -d "$(dirname "$SCRATCH")" ]] || SCRATCH="${TMPDIR:-/tmp}/$USER"
mkdir -p "$SCRATCH/bin"
export PATH="$HOME/.local/bin:$SCRATCH/bin:$PATH"
export UV_CACHE_DIR="$SCRATCH/uv-cache"
export OLLAMA_MODELS="$SCRATCH/ollama-models"
mkdir -p "$OLLAMA_MODELS"

echo "[1/4] scratch = $SCRATCH"

# --- uv (manages Python + deps; no conda needed) ---------------------------
if ! command -v uv >/dev/null; then
  echo "[2/4] installing uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh
else
  echo "[2/4] uv already installed: $(uv --version)"
fi

# --- project deps ----------------------------------------------------------
echo "[3/4] uv sync (creates .venv from uv.lock)"
uv sync

# --- ollama binary (no root, extracted into scratch) -----------------------
if ! command -v ollama >/dev/null && [[ ! -x "$SCRATCH/bin/ollama" ]]; then
  echo "[4/4] downloading ollama linux-amd64 into $SCRATCH/bin"
  tmp="$(mktemp -d)"
  curl -L https://ollama.com/download/ollama-linux-amd64.tgz -o "$tmp/ollama.tgz"
  tar -xzf "$tmp/ollama.tgz" -C "$tmp"
  # tarball lays out bin/ollama and lib/ — keep them together under scratch
  cp -r "$tmp"/bin/* "$SCRATCH/bin/" 2>/dev/null || true
  [[ -d "$tmp/lib" ]] && cp -r "$tmp/lib" "$SCRATCH/" 2>/dev/null || true
  rm -rf "$tmp"
  chmod +x "$SCRATCH/bin/ollama"
else
  echo "[4/4] ollama already available"
fi

# --- pre-pull the model on the login node ----------------------------------
if [[ -n "$MODEL" ]]; then
  echo "[+] pre-pulling $MODEL into $OLLAMA_MODELS"
  OLLAMA_HOST="127.0.0.1:11434" ollama serve >/tmp/ollama-setup.log 2>&1 &
  pid=$!
  for i in $(seq 1 30); do curl -sf http://127.0.0.1:11434/api/tags >/dev/null && break; sleep 2; done
  OLLAMA_HOST="127.0.0.1:11434" ollama pull "$MODEL"
  kill $pid 2>/dev/null || true
fi

echo
echo "Done. Now submit a job:"
echo "  sbatch cluster/slurm_job.sh ${MODEL:-qwen2.5:7b}"
echo "(DAS daytime: add --begin=20:00 for long overnight runs)"
