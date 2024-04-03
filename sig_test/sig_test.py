
'''
Significance test routine to compare the results from different systems

'''

import pandas as pd
import pickle
import json
from collections import defaultdict
import random
import numpy as np
import tqdm

import sig_data_preprocess

import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--predictions_path', type=str, required=True, help="path to the tabulated document wise results file")
parser.add_argument('--output_path', type=str, required=True, help="path to save the output")
args = parser.parse_args()


def compute_f1(count_json, initial = False):
  """
  Helper function to compute the F1 scores during the parametric testing
  Args:
    count_json: dict containing the metrics required to compute F1
    initial: Boolean
      set this to True only when computing the initial delta
  """

  f1_collector = {}
  total_NT = 0
  total_NP = 0
  total_TP = 0

  trigger_NT = 0
  trigger_NP = 0
  trigger_TP = 0

  arguments_NT = 0
  arguments_NP = 0
  arguments_TP = 0

  overall_dict = {}

  for doc_id, doc_triggers in count_json.items():
    for trig, doc_trigger in doc_triggers.items():
      if trig in ['Alcohol', 'Tobacco', 'Drug']:
        trig = "Substance_use"
      if trig not in overall_dict:
        overall_dict[trig] = {}
      for arg, arg_counts in doc_trigger.items():
        if arg not in overall_dict[trig]:
          overall_dict[trig][arg] = {'NT': 0, 'NP': 0, 'TP':0, 'p':0, 'r':0, 'f1':0}
        if 'NT' in arg_counts:
          overall_dict[trig][arg]['NT'] += arg_counts['NT']
          overall_dict[trig][arg]['NP'] += arg_counts['NP']
          overall_dict[trig][arg]['TP'] += arg_counts['TP']
          if arg == 'Trigger':
            trigger_NT += arg_counts['NT']
            trigger_NP += arg_counts['NP']
            trigger_TP += arg_counts['TP']
          else:
            arguments_NT += arg_counts['NT']
            arguments_NP += arg_counts['NP']
            arguments_TP += arg_counts['TP']
        
          total_NT += arg_counts['NT']
          total_NP += arg_counts['NP']
          total_TP += arg_counts['TP']
        else:
          print(arg_counts)


  for event, event_info in overall_dict.items():
    for arg, arg_info in event_info.items():
      p = overall_dict[event][arg]['TP'] /overall_dict[event][arg]['NP'] if overall_dict[event][arg]['NP'] > 0 else 0
      r = overall_dict[event][arg]['TP'] /overall_dict[event][arg]['NT'] if overall_dict[event][arg]['NT'] > 0 else 0
      f1 = (2*p*r)/(p+r) if (p*r) > 0 else 0
      overall_dict[event][arg]['p'] = np.round(p, 3)
      overall_dict[event][arg]['r'] = np.round(r, 3)
      overall_dict[event][arg]['f1'] = np.round(f1, 3)

  for event, event_info in overall_dict.items(): 
    for arg, arg_info in event_info.items():
      key = event + "-" + arg
      f1_collector[key] = arg_info['f1']
    
  #compute overall trigger performance
  trigger_p = trigger_TP/trigger_NP
  trigger_r = trigger_TP/trigger_NT
  trigger_f1 = np.round((2*trigger_p*trigger_r)/(trigger_p+trigger_r), 3)
  if initial:
    print(f"trigger-overall : NT = {trigger_NT} NP = {trigger_NP} TP = {trigger_TP} P = {np.round(trigger_p, 3)} R = {np.round(trigger_r, 3)} F1 = ", trigger_f1)
  f1_collector['trigger'] = trigger_f1

  #compute overall arguments performance
  arguments_p = arguments_TP/arguments_NP
  arguments_r = arguments_TP/arguments_NT
  arguments_f1 = np.round((2*arguments_p*arguments_r)/(arguments_p+arguments_r), 3)
  if initial:
    print(f"arguments-overall : NT = {arguments_NT} NP = {arguments_NP} TP = {arguments_TP}  P = {np.round(arguments_p, 3)} R = {np.round(arguments_r, 3)} F1 = ", arguments_f1)
  f1_collector['arguments'] = arguments_f1
  
  #compute overall performance
  total_p = total_TP/total_NP
  total_r = total_TP/total_NT
  f1 = np.round((2*total_p*total_r)/(total_p+total_r), 3)
  if initial:
    print(f"overall : NT = {total_NT} NP = {total_NP} TP = {total_TP}  P = {np.round(total_p, 3)} R = {np.round(total_r, 3)} F1 = ", f1)
  f1_collector['overall'] = f1
  return f1_collector


def sig_test(modelA, modelB, all_ids, run_name, n = 100, b= 10000):
  """
  Non-parametric significance test routine

  Args:
    modelA: dict
      system A results at the document level
    modelB: dict
      system B results at document level
    run_name: str
      unique run name. usually in the format systemA-Vs-SystemB 
  """

  print("######################################################################") 
  print("*** system A ***")
  f1_A = compute_f1(modelA, True)
  print(f1_A)
  modelA_name, modelB_name = run_name.split("-Vs-")
  pd.DataFrame(f1_A.items()).to_csv(f"{args.output_path}/{modelA_name}.csv")
  print("######################################################################") 
  print("*** system B ***")
  f1_B = compute_f1(modelB, True)
  print(f1_B)
  pd.DataFrame(f1_B.items()).to_csv(f"{args.output_path}/{modelB_name}.csv")
  
  delta = {}
  for event in f1_A:
    delta[event] = f1_A[event] - f1_B[event]
  print("######################################################################") 
  print("*** initial delta: ***")
  print(delta)

  significant = {x:0 for x in delta}                        
  for i_iter in tqdm.tqdm(range(b)):
    iter_ids = random.sample(all_ids, n)

    iter_sample_A = {}
    for docid, doc_contents in modelA.items():
      if docid in iter_ids:
        iter_sample_A[docid] = doc_contents
    
    iter_sample_B = {}
    for docid, doc_contents in modelB.items():
      if docid in iter_ids:
        iter_sample_B[docid] = doc_contents

    f1_A_b = compute_f1(iter_sample_A)
    f1_B_b = compute_f1(iter_sample_B)

    for event in f1_A_b:
      delta_b = f1_A_b[event] - f1_B_b[event]
      if delta_b > (2*delta[event]):
        significant[event] += 1    
  
  pvalue = {x:0 for x in delta}
  for event in significant:
    pvalue[event] = significant[event]/b
    if delta[event] < 0:
      pvalue[event] = 1-pvalue[event]

  print("######################################################################")     
  print("significant = \n \t ", significant)
  print("######################################################################") 
  print("p value = \n \t ", pvalue)
  print("######################################################################")

  event_keys = [x for x in pvalue]
  sig_result = pd.DataFrame(index = event_keys, columns = ['f1_A', 'f1_B', 'delta', 'significant-count', 'pvalue', 'significance'])
  
  for event in pvalue:
    sig_result.loc[event, 'f1_A'] = f1_A[event]
    sig_result.loc[event, 'f1_B'] = f1_B[event]
    sig_result.loc[event, 'delta'] = delta[event]
    sig_result.loc[event, 'significant-count'] = significant[event]
    sig_result.loc[event, 'pvalue'] = pvalue[event]
    sig_result['significance'] = [1 if x<0.05 else 0 for x in sig_result['pvalue']]

  sig_result.to_csv(f"{args.output_path}/{run_name}.csv")

        
  
if __name__ == '__main__':

  systems = [("t5-pipeline-trigger", "mspert", "t5pipeline-Vs-mspert"), 
                  ("t5-pipeline-trigger", "MS-t5", "t5pipeline-Vs-MSt5"),
                  ("t5-pipeline-trigger", "GPT-pipeline-guideline_few-shot", "t5pipeline-Vs-GPTfewshot"),
                  ("t5-pipeline-trigger", "GPT-pipeline-guideline", "t5pipeline-Vs-GPTguideline"),
                  ("t5-pipeline-trigger", "GPT-event", "t5pipeline-Vs-GPTevent"),
                  ("t5-pipeline-trigger", "GPT-pipeline", "t5pipeline-Vs-GPTpipeline"),
                  ("mspert","MS-t5", "mspert-Vs-MSt5"),
                  ("mspert", "GPT-pipeline-guideline_few-shot", "mspert-Vs-GPTfewshot"),
                  ("mspert", "GPT-pipeline-guideline", "mspert-Vs-GPTguideline"),
                  ("mspert", "GPT-pipeline", "mspert-Vs-GPTpipeline"), 
                  ("mspert", "GPT-event", "mspert-Vs-GPTevent"), 
                  ("MS-t5", "GPT-pipeline-guideline_few-shot", "MSt5-Vs-GPTfewshot"),
                  ("MS-t5", "GPT-pipeline-guideline", "MSt5-Vs-GPTguideline"),
                  ("MS-t5", "GPT-event", "MSt5-Vs-GPTevent"),
                  ("MS-t5", "GPT-pipeline", "MSt5-Vs-GPTpipeline"),
                  ("GPT-pipeline-guideline_few-shot", "GPT-pipeline-guideline", "GPTfewshot-Vs-GPTguideline"),
                  ("GPT-pipeline-guideline_few-shot", "GPT-event","GPTfewshot-Vs-GPTevent"),
                  ("GPT-pipeline-guideline_few-shot", "GPT-pipeline","GPTfewshot-Vs-GPTpipeline"),
                  ("GPT-pipeline-guideline", "GPT-event", "GPTguideline-Vs-GPTevent"),
                  ("GPT-pipeline-guideline", "GPT-pipeline", "GPTguideline-Vs-GPTpipeline"),
                  ("GPT-event", "GPT-pipeline", "GPTevent-Vs-GPTpipeline")
                  ]
  
  
  ids = []
  for system_pair in systems:
    print("***********************************************************************")
    print(f"{system_pair[0]} vs {system_pair[1]}")
    print("***********************************************************************")
    modelA_preds = sig_data_preprocess.doccsv_to_json(f"{args.predictions_path}/{system_pair[0]}.csv")
    
    modelB_preds = sig_data_preprocess.doccsv_to_json(f"{args.predictions_path}/{system_pair[1]}.csv")

    ids = [x for x in modelA_preds.keys()]

    sig_test(modelA_preds, modelB_preds, ids, system_pair[2])
    