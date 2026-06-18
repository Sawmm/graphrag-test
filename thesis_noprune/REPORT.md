# Thesis report — Article 10 compliance pipeline

- Documents scored against ground truth: **30**
- Models: **5**  (gemma4-e4b, llama3.1-8b, mistral-7b, qwen2.5-14b, qwen2.5-7b)
- Modes: **1**   (graphrag)

## Headline — macro F1 per (mode, model)

    mode       model  precision_mean  precision_std  recall_mean  recall_std  f1_mean  f1_std
graphrag qwen2.5-14b           0.436          0.352        0.982       0.070    0.533   0.315
graphrag  qwen2.5-7b           0.434          0.353        0.995       0.028    0.528   0.310
graphrag llama3.1-8b           0.435          0.353        0.954       0.154    0.511   0.304
graphrag  mistral-7b           0.402          0.348        0.936       0.194    0.488   0.305
graphrag  gemma4-e4b           0.438          0.368        0.657       0.272    0.468   0.313

## Per-mode (averaged over models)

    mode  precision  recall    f1
graphrag      0.429   0.905 0.506

## Per-model (averaged over modes)

      model  precision  recall    f1
qwen2.5-14b      0.436   0.982 0.533
 qwen2.5-7b      0.434   0.995 0.528
llama3.1-8b      0.435   0.954 0.511
 mistral-7b      0.402   0.936 0.488
 gemma4-e4b      0.438   0.657 0.468

## SHACL verdict accuracy on synthetic test cards

mode
graphrag    0.393