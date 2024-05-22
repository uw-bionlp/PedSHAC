# PedSHAC
The dataset, annotation guideline, and baseline experiments for the PedSHAC corpora were published in the LREC-COLING 2024 paper, ['Extracting Social Determinants of Health from Pediatric Patient Notes Using Large Language Models: Novel Corpus and Methods.'](https://arxiv.org/abs/2404.00826)


# Dataset
Dataset to be released, after the IRB approval from our home institution, and the de-identification step. Thanks for your patience!

# Annotator agreement and evaluation
Annotator agreement is evaluated by Dr. Kevin Lybarger's [script](https://github.com/Lybarger/brat_scoring).
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
## Data pre- and post-processing

For the mSpERT model, we apply the score from Dr. Kevin Lybarger's code on [SDoH extraction](https://github.com/Lybarger/sdoh_extraction).

For T5-event model
1. Run T5-event/encode.py on BRAT files (txt and ann) to generate event-format json files. (Adapted from [Microsoft N2C2 T5 project](https://github.com/romanows/SDOH-n2c2/blob/main/scripts/extract-examples.py)).
2. Run T5-event/convert_to_t5_train_format.py to convert event-format files to peft train format (input-output)
3. Run T5-event/peft_t5.py to train the models on the generated input files from step 2
4. Run T5-event/decode.py to generate the scores at txt file level and summary statistics for the whole corpus provided for prediction

For T5-2sQA model
1. Run T5-2sQA/data_loader.py to convert the BRAT .ann files into the T5 input format
2. Run the T5-2sQA/evaluation.py to score the T5 output, by comparing with the BRAT .ann files.
# Baseline experiments
1. mSpERT: please refer to the original project [github](https://github.com/uw-bionlp/mspert).
2. FLAN-T5: _peft_t5.py_. The code deploys the huggingface peft package, and is adapted from this [post](https://www.philschmid.de/fine-tune-flan-t5-peft). 
```console
# training
# the experiment_type is the customized, and the trained models will  be stored under the folder models/{experiment_name}
python peft_t5.py \
                      --train_path ${path_for_the_train_set} \
                      --valid_path ${path_for_the_validation_set} \
                      --model_id ${model_name} \
                      --num_epoch ${num_epoch} \
                      --experiment_name ${experiment_type} \
                      --mode 'train'

# evaluation
# the predictions models will be stored under the folder models/{experiment_name}
python peft_t5.py \
                      --train_path ${path_for_the_train_set} \
                      --valid_path ${path_for_the_validation_set} \
                      --model_id ${model_name} \
                      --num_epoch ${num_epoch} \
                      --experiment_name ${experiment_type} \
                      --mode 'eval' 
```
4. GPT-4: GPT-4 with 32k token context and temperature 0, from the HIPPA-compliant OpenAI azure environment. _gpt4_prompts.txt_ includes prompts as the condensed annotation guideline.



Model predictions are converted to the BRAT .ann file, and evaluated using the same script above.

# Significance Tests
sig_test.py runs the non-parametric bootstrap tests for any two different models. The input is a file-level performance (step 4 in T5 event). 

# Contacts
For questions about accessing the data and code, please contact:
- Yujuan Fu (velvinfu@uw.edu)
- Giridhar Kaushik Ramachandran (gramacha@gmu.edu)

# Citation
```console
@inproceedings{fu-etal-2024-extracting-social,
    title = "Extracting Social Determinants of Health from Pediatric Patient Notes Using Large Language Models: Novel Corpus and Methods",
    author = {Fu, Yujuan  and
      Ramachandran, Giridhar Kaushik  and
      Dobbins, Nicholas J.  and
      Park, Namu  and
      Leu, Michael  and
      Rosenberg, Abby R.  and
      Lybarger, Kevin  and
      Xia, Fei  and
      Uzuner, {\"O}zlem  and
      Yetisgen, Meliha},
    editor = "Calzolari, Nicoletta  and
      Kan, Min-Yen  and
      Hoste, Veronique  and
      Lenci, Alessandro  and
      Sakti, Sakriani  and
      Xue, Nianwen",
    booktitle = "Proceedings of the 2024 Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING 2024)",
    month = may,
    year = "2024",
    address = "Torino, Italy",
    publisher = "ELRA and ICCL",
    url = "https://aclanthology.org/2024.lrec-main.618",
    pages = "7045--7056",
    
}
```
