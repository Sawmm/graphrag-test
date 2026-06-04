# Running on a VU CUDA cluster (DAS-5/6, Ada, Snellius)

Run **every document in `inputs/` through one model**, both pipeline modes
(graphrag + bypass), on a GPU node. No Neo4j and no containers required — the
KG is cached to JSON and SHACL runs from memory, so the GPU job only needs
Ollama (`--no-neo4j`).

## 1. Log in (jump host)

```bash
# DAS-6
ssh -J <vunetid>@ssh.data.vu.nl <dasid>@fs0.das6.cs.vu.nl
# DAS-5 : fs0.das5.cs.vu.nl   ·   Ada : ada.labs.vu.nl   ·   Snellius : snellius.surf.nl
```

## 2. Get the repo + one-time setup (on the LOGIN node — it has internet)

```bash
git clone <your-repo-url> graphrag-test && cd graphrag-test
bash cluster/setup_env.sh qwen2.5:7b
```

This installs `uv`, builds the venv from `uv.lock`, drops a local `ollama`
binary in `/var/scratch/$USER/bin`, and **pre-pulls the model** (compute nodes
often have no internet, so pulling here matters).

## 3. Submit the job

```bash
sbatch cluster/slurm_job.sh qwen2.5:7b           # all docs, both modes, 1 model
MODE=bypass sbatch cluster/slurm_job.sh qwen2.5:14b
```

**DAS daytime rule:** jobs over 15 min only run nights/weekends. Queue overnight:

```bash
sbatch --begin=20:00 cluster/slurm_job.sh qwen2.5:7b
```

Check / cancel:

```bash
squeue -u $USER
scancel <JOBID>
tail -f cluster/logs/graphrag-<JOBID>.out
```

## 4. Get results back (run locally)

```bash
rsync -av <dasid>@fs0.das6.cs.vu.nl:graphrag-test/outputs/ ./outputs/
rsync -av <dasid>@fs0.das6.cs.vu.nl:graphrag-test/cache/   ./cache/
# add  -e 'ssh -J <vunetid>@ssh.data.vu.nl'  when off the VU network
```

## Knobs

| Var          | Default                  | Meaning                                  |
|--------------|--------------------------|------------------------------------------|
| `MODE`       | `both`                   | `both` \| `graphrag` \| `bypass`         |
| `FORCE`      | `0`                      | `1` re-extracts even if cache exists     |
| `NO_NEO4J`   | `1`                      | `0` to also write to a running Neo4j     |
| `INPUT_GLOB` | `inputs/*.md`            | which documents to run                   |
| `SCRATCH_DIR`| `/var/scratch/$USER`     | where models/uv-cache live               |
| `EXTRA_ARGS` | —                        | extra `run.py` flags, e.g. `--judge`     |

Edit the `#SBATCH` partition / `module load` lines at the top of
`slurm_job.sh` for your cluster (`sinfo` lists partitions).

## Run several models

`run_all.sh` does **all documents for one model**. For multiple models, submit
one job each (they queue independently and reuse the same scratch cache):

```bash
for m in qwen2.5:7b qwen2.5:14b llama3.1:8b; do
  sbatch --begin=20:00 cluster/slurm_job.sh "$m"
done
```

## Without a scheduler (plain SSH / interactive node)

Grab an interactive GPU node, then run the batch directly:

```bash
salloc --partition=defq --gres=gpu:1 -t 02:00:00      # DAS
# ssh to the granted node, then:
ollama serve & ollama pull qwen2.5:7b
bash cluster/run_all.sh qwen2.5:7b
```

## Local use (Mac, with Neo4j for graph browsing)

```bash
NO_NEO4J=0 MODE=both bash cluster/run_all.sh qwen2.5:7b
```
