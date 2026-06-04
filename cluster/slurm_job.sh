#!/bin/bash
#SBATCH --job-name=graphrag
#SBATCH --partition=defq            # DAS5/6: defq | Snellius: gpu   (check `sinfo`)
#SBATCH -C A4000                    # DAS-6 GPU type: A4000 (16GB) | A5000 (24GB) | A6000 (48GB)
#SBATCH --gres=gpu:1                # 1 GPU; Ollama uses CUDA automatically
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --time=08:00:00             # DAS daytime cap is 15 min — see note below
#SBATCH --output=cluster/logs/%x-%j.out
#SBATCH --error=cluster/logs/%x-%j.err
#
# Run EVERY document in inputs/ through run.py for ONE model on a GPU node.
# Tuned for the VU clusters (DAS-5, DAS-6, Ada, Snellius). No containers and
# no Neo4j: both pipeline modes need only Ollama on the GPU (--no-neo4j).
#
# Submit (from the repo root on the cluster):
#   sbatch cluster/slurm_job.sh qwen2.5:7b
#   MODE=bypass sbatch cluster/slurm_job.sh qwen2.5:14b
#
# DAS daytime rule: jobs >15 min are only allowed at night/weekends. Queue an
# overnight run with:
#   sbatch --begin=20:00 cluster/slurm_job.sh qwen2.5:7b
#
set -euo pipefail

MODEL="${1:?usage: sbatch cluster/slurm_job.sh <model>}"
export MODE="${MODE:-both}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
mkdir -p cluster/logs

# ---------------------------------------------------------------------------
# 1. GPU drivers  — EDIT per cluster
# ---------------------------------------------------------------------------
# DAS-5 / DAS-6: module loads enabled.
# Snellius: comment them out (modules not usually needed).
. /etc/bashrc
. /etc/profile.d/lmod.sh
module load cuda12.6/toolkit
module load cuDNN/cuda12.6
command -v nvidia-smi >/dev/null && nvidia-smi --query-gpu=name,memory.total --format=csv || true

# ---------------------------------------------------------------------------
# 2. Scratch — keep models + uv cache off the small home quota
# ---------------------------------------------------------------------------
# DAS: /var/scratch/$USER   Snellius: $TMPDIR (node-local) or scratch-shared.
SCRATCH="${SCRATCH_DIR:-/var/scratch/$USER}"
[[ -d "$SCRATCH" ]] || SCRATCH="${TMPDIR:-/tmp}/$USER"
mkdir -p "$SCRATCH"

export OLLAMA_MODELS="$SCRATCH/ollama-models"      # big model blobs live here
export UV_CACHE_DIR="$SCRATCH/uv-cache"
export OLLAMA_HOST="127.0.0.1:11434"
OLLAMA_URL="http://${OLLAMA_HOST}"
mkdir -p "$OLLAMA_MODELS"

# uv must be on PATH (setup_env.sh installs it to ~/.local/bin)
export PATH="$HOME/.local/bin:$SCRATCH/bin:$PATH"
command -v uv >/dev/null || { echo "uv not found — run cluster/setup_env.sh first"; exit 1; }
command -v ollama >/dev/null || { echo "ollama not found — run cluster/setup_env.sh first"; exit 1; }

# ---------------------------------------------------------------------------
# 3. Start a private Ollama server on this node (binds to the allocated GPU)
# ---------------------------------------------------------------------------
echo "[setup] starting ollama on $OLLAMA_HOST (models: $OLLAMA_MODELS)"
ollama serve >"cluster/logs/ollama-${SLURM_JOB_ID:-local}.log" 2>&1 &
OLLAMA_PID=$!
trap 'kill $OLLAMA_PID 2>/dev/null || true' EXIT

for i in $(seq 1 60); do
  curl -sf "$OLLAMA_URL/api/tags" >/dev/null && break
  sleep 2
  [[ $i -eq 60 ]] && { echo "ollama did not start; see log"; exit 1; }
done

echo "[setup] pulling $MODEL"
ollama pull "$MODEL"

# ---------------------------------------------------------------------------
# 4. Run all documents for this model (both modes, no Neo4j)
# ---------------------------------------------------------------------------
MODE="$MODE" \
NO_NEO4J=1 \
OLLAMA_URL="$OLLAMA_URL" \
FORCE="${FORCE:-0}" \
EXTRA_ARGS="${EXTRA_ARGS:-}" \
  bash cluster/run_all.sh "$MODEL"

echo "[done] results in outputs/ and cache/. Copy them back with scp/rsync."
