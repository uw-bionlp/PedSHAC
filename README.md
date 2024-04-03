# PedSHAC
The dataset, annotation guideline, and baseline experiments for the PedSHAC corpora were published in the LREC-COLING 2024 paper, 'Extracting Social Determinants of Health from Pediatric Patient Notes Using Large Language Models: Novel Corpus and Methods.' 


# Dataset
Dataset to be released, after the IRB approval from our home institution, and the de-identification step.

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
The pre-processing script processes the .ann files from the BRAT annotation tool. The post-processing script transforms the model predictions back to the BRAT. ann files for evaluation. 

Steps:
1. Clone the BRAT conversion from Dr. Kevin Lybarger's [script](https://github.com/Lybarger/brat_scoring), and store it under the same repository.
2. Conversion from BRAT to the mSpERT input format: _BRAT2json.py_. Please change the data_dir to the folder containing your BRAT .ann files.
3. Conversion from mSpERT input to T5 input, and from model predictions to BRAT. ann files: format_conversion.ipynb

For T5-event model
1. Run encode.py on BRAT files (txt and ann) to generate event-format json files. (Adapted from [Microsoft N2C2 T5 project](https://github.com/romanows/SDOH-n2c2/blob/main/scripts/extract-examples.py)).
2. Run convert_to_t5_train_format.py to convert event-format files to peft train format (input-output)
3. Run peft_t5.py to train the models on the generated input files from step 2
4. Run decode.py to generate the scores at txt file level and summary statistics for the whole corpus provided for prediction
   
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
