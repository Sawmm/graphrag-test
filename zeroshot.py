"""
zeroshot.py — Zero-shot LLM compliance baseline for EU AI Act Article 10.

Minimal prompt: hands the model card to the LLM and asks it to judge each
Article 10 obligation WITHOUT providing obligation definitions, hints, or
schema explanation. Tests whether the model inherently knows Article 10.

Output is the same JSON structure as bypass.py so the RDF / SHACL comparison
is apples-to-apples across pipelines.

Use with:  uv run python run.py --input model_card.md --model qwen2.5:7b --zeroshot
"""

from __future__ import annotations

import json
import logging
import re

import json_repair
from neo4j_graphrag.llm.ollama_llm import OllamaLLM
from neo4j_graphrag.types import LLMMessage

from bypass import _OBLIGATION_KEYS, judgments_to_rdf  # reuse output mapping

log = logging.getLogger(__name__)


_SYSTEM_PROMPT = """\
/no_think
You are assessing an AI system's documentation for compliance with \
Article 10 of the EU AI Act.

Return ONLY valid JSON with this exact structure (no prose):

{
  "has_training_dataset": true,
  "has_validation_dataset": true,
  "has_testing_dataset": false,
  "training":   {"design_choices": true, "provenance": true, "preprocessing": true, "assumptions": true, "suitability": true, "bias_examination": false, "bias_mitigation": false, "data_gaps": false, "relevance": true, "representativeness": false, "statistical_props": true, "quality_metrics": true, "contextual_characteristics": true},
  "validation": {"<same 13 keys>": true},
  "testing":    {"<same 13 keys>": true}
}

Use your own knowledge of Article 10 to decide what each key means.
"""


async def zeroshot_judge(text: str, llm: OllamaLLM) -> dict:
    """Send the document with a minimal prompt; return structured judgments."""
    messages = [
        LLMMessage(role="system", content=_SYSTEM_PROMPT),
        LLMMessage(role="user", content=f"Model card:\n\n{text}"),
    ]
    log.info("Zero-shot: sending document to LLM (%d chars)", len(text))
    result = await llm.ainvoke(messages)
    raw = result.content.strip()

    if raw.startswith("```"):
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)

    repaired = json_repair.repair_json(raw)
    try:
        judgments: dict = json.loads(repaired)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Zero-shot judge returned unparseable JSON: {e}\nRaw: {raw[:500]}"
        ) from e

    for ds in ("training", "validation", "testing"):
        judgments.setdefault(ds, {})
        for key in _OBLIGATION_KEYS:
            judgments[ds].setdefault(key, False)
    for key in ("has_training_dataset", "has_validation_dataset", "has_testing_dataset"):
        judgments.setdefault(key, False)

    log.info(
        "Zero-shot judgment — training: %s  validation: %s  testing: %s",
        judgments["has_training_dataset"],
        judgments["has_validation_dataset"],
        judgments["has_testing_dataset"],
    )
    return judgments


__all__ = ["zeroshot_judge", "judgments_to_rdf"]
