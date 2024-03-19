# PedSHAC
Dataset, annotation guideline and baseline experiments for the PedSHAC corpora.


# Dataset
Dataset to be released, after the IRB approval from our home institution, and the de-identification step.


# Annotator agreement and evaluation
Annotator agreement is evaluated by Dr. Lybarger's [script](https://github.com/Lybarger/brat_scoring).
```ruby
from brat_scoring.scoring import score_brat_sdoh
from brat_scoring.constants import EXACT, LABEL, OVERLAP, PARTIAL, MIN_DIST

df = score_brat_sdoh( \
                gold_dir = "/home/gold/",
                predict_dir = "/home/predict/",
                output_path = "/home/scoring.csv",
                score_trig = OVERLAP,
                score_span = OVERLAP, 
                score_labeled = LABEL,
                )
```

Model predictions are converted to the BRAT .ann file, and evaluated using the same script above.

# baseline experiments:
1. mSpERT: please refer to the original project [github](https://github.com/uw-bionlp/mspert).
2. FLAN-T5: [huggingface peft package](https://www.philschmid.de/fine-tune-flan-t5-peft).
