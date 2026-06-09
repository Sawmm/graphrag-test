# Thesis report — Article 10 compliance pipeline

- Documents scored against ground truth: **21**
- Models: **5**  (gemma4-e4b, llama3.1-8b, mistral-7b, qwen2.5-14b, qwen2.5-7b)
- Modes: **3**   (bypass, graphrag, zeroshot)

## Headline — macro F1 per (mode, model)

    mode       model  precision_mean  precision_std  recall_mean  recall_std  f1_mean  f1_std
  bypass qwen2.5-14b           0.828          0.350        0.776       0.367    0.789   0.351
  bypass llama3.1-8b           0.857          0.359        0.677       0.361    0.738   0.348
  bypass  qwen2.5-7b           0.796          0.360        0.589       0.350    0.652   0.335
  bypass  mistral-7b           0.697          0.436        0.494       0.351    0.554   0.366
  bypass  gemma4-e4b           0.476          0.512        0.442       0.499    0.450   0.497
graphrag llama3.1-8b           0.377          0.280        0.656       0.279    0.444   0.243
graphrag  mistral-7b           0.334          0.304        0.945       0.110    0.426   0.254
graphrag  qwen2.5-7b           0.315          0.301        0.936       0.114    0.411   0.257
graphrag  gemma4-e4b           0.331          0.308        0.459       0.270    0.337   0.241
graphrag qwen2.5-14b           0.437          0.365        0.325       0.320    0.315   0.269
zeroshot qwen2.5-14b           0.834          0.321        0.692       0.335    0.741   0.312
zeroshot  qwen2.5-7b           0.798          0.329        0.692       0.320    0.724   0.304
zeroshot llama3.1-8b           0.826          0.316        0.628       0.347    0.684   0.315
zeroshot  gemma4-e4b           0.588          0.467        0.571       0.460    0.556   0.441
zeroshot  mistral-7b           0.391          0.368        0.625       0.378    0.423   0.327

## Per-mode (averaged over models)

    mode  precision  recall    f1
graphrag      0.359   0.664 0.386
  bypass      0.731   0.596 0.636
zeroshot      0.688   0.642 0.626

## Per-model (averaged over modes)

      model  precision  recall    f1
llama3.1-8b      0.687   0.654 0.622
qwen2.5-14b      0.700   0.597 0.615
 qwen2.5-7b      0.637   0.739 0.596
 mistral-7b      0.474   0.688 0.468
 gemma4-e4b      0.465   0.491 0.448

## SHACL verdict accuracy on synthetic test cards

mode
bypass      0.667
graphrag    0.667
zeroshot    0.667