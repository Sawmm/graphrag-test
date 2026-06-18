# Thesis report — Article 10 compliance pipeline

- Documents scored against ground truth: **30**
- Models: **6**  (baseline-keyword, gemma4-e4b, llama3.1-8b, mistral-7b, qwen2.5-14b, qwen2.5-7b)
- Modes: **4**   (bypass, graphrag, graphrag_stripped, zeroshot)

## Headline — macro F1 per (mode, model)

             mode            model  precision_mean  precision_std  recall_mean  recall_std  f1_mean  f1_std
           bypass      llama3.1-8b           0.958          0.123        0.808       0.182    0.862   0.149
           bypass      qwen2.5-14b           0.824          0.347        0.735       0.356    0.756   0.339
           bypass       qwen2.5-7b           0.800          0.357        0.681       0.337    0.721   0.332
           bypass       mistral-7b           0.700          0.437        0.496       0.364    0.564   0.375
           bypass       gemma4-e4b           0.367          0.490        0.308       0.445    0.324   0.451
         graphrag baseline-keyword           0.416          0.344        0.954       0.185    0.514   0.315
         graphrag       qwen2.5-7b           0.464          0.341        0.704       0.213    0.458   0.196
         graphrag      llama3.1-8b           0.553          0.314        0.450       0.217    0.422   0.157
         graphrag       mistral-7b           0.431          0.369        0.559       0.237    0.407   0.241
         graphrag       gemma4-e4b           0.477          0.401        0.214       0.153    0.254   0.176
         graphrag      qwen2.5-14b           0.634          0.405        0.197       0.219    0.237   0.180
graphrag_stripped       mistral-7b           1.000            NaN        0.718         NaN    0.836     NaN
graphrag_stripped       gemma4-e4b           1.000            NaN        0.513         NaN    0.678     NaN
graphrag_stripped       qwen2.5-7b           0.692          0.435        0.731       0.380    0.594   0.054
graphrag_stripped      llama3.1-8b           1.000            NaN        0.333         NaN    0.500     NaN
graphrag_stripped      qwen2.5-14b           0.000            NaN        0.000         NaN    0.000     NaN
         zeroshot      llama3.1-8b           0.937          0.137        0.767       0.174    0.827   0.125
         zeroshot       qwen2.5-7b           0.824          0.317        0.735       0.307    0.763   0.296
         zeroshot      qwen2.5-14b           0.821          0.319        0.681       0.323    0.726   0.305
         zeroshot       mistral-7b           0.492          0.397        0.613       0.346    0.487   0.327
         zeroshot       gemma4-e4b           0.478          0.491        0.473       0.484    0.462   0.476

## Per-mode (averaged over models)

             mode  precision  recall    f1
         graphrag      0.496   0.513 0.382
graphrag_stripped      0.731   0.504 0.534
           bypass      0.730   0.606 0.645
         zeroshot      0.710   0.654 0.653

## Per-model (averaged over modes)

           model  precision  recall    f1
     llama3.1-8b      0.818   0.671 0.702
      qwen2.5-7b      0.696   0.707 0.646
     qwen2.5-14b      0.751   0.532 0.567
baseline-keyword      0.416   0.954 0.514
      mistral-7b      0.546   0.558 0.490
      gemma4-e4b      0.446   0.334 0.350

## SHACL verdict accuracy on synthetic test cards

mode
bypass               0.847
graphrag             0.828
graphrag_stripped    0.000
zeroshot             0.833