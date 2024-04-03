'''
Parses the results from t5 experiments and produces tabulated results

'''

import json
import re
import pandas as pd
import numpy as np
import math
import os


import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--gt_json', type=str, required=True, help="path to ground truth json")
parser.add_argument('--pred_json', type=str, required=True, help="path to prediction json")
parser.add_argument('--path_to_txtfiles', type=str, required=True, help="path to input txt files")
parser.add_argument('--output_path', type=str, required=True, help="path to store tabulated and file-level results ")
args = parser.parse_args()

remove_ids = ['22296', '14292', '34005', '14357', '34102', '14357', '22296', '34005', '25343', '30765', '4403', '27382', '17039', '14357', '30711', '34102', '4403', '14357', '22660', '27382', '34102', '14357', '4403', '14357', '36184', '25343', '34005', '34102', '34102', '22021', '35914', '25343', '27382', '22021', '22021']


#change it to 'json' if the prediction is in json format
output_type = 'colondelimited' 

gt_file = args.gt_json
path_to_txtfiles = args.path_to_txtfiles
pred_file = args.pred_json
out_path = args.output_path
error_log_file = args.output_path + "t5_invalid_cases.log"

gt_prefixes = ['\u00ab', '\u00bb', '\u00ac', '\u0020', '\u20ac']
pred_prefixes = ['\\\\u00ab', '\\\\u00bb', '\\\\u00ac', '\\\\u0020', '\\\\u20ac']

#Initialize these templates that are used for parsing and validation of event and argument types
entity_argument_map = {'Adoption': {"Trigger": ""},
          'Alcohol' : {"Trigger": "", "Substance_Experiencer": "", "Substance_Status": ""},
          'Drug' : {"Trigger": "", "Substance_Experiencer":"", "Substance_Status" : ""},
          'Education_access' : {"Trigger": "", "Education_Status" : ""}, 
          'Employment' : {"Trigger": "", "Employment_Status" : ""},
          'Food_insecurity' : {"Trigger": "", "Food_Status" : ""},           
          'Living_arrangement': {"Trigger": "", "Living_Status": "", "Living_Type": "", "Residence" : ""}, 
          'Mental_health' : {"Trigger": "", "Mental_Status": "", "Mental_Experiencer": ""},
          'Prior_trauma': {"Trigger": "", "Prior_Status": "", "Prior_Type" : ""},
          'Tobacco' : {"Trigger": "", "Substance_Experiencer":"", "Substance_Status" : ""}}

valid_argtypes_map = {'Alcohol' : {'Substance_Experiencer':['parent_caregiver', 'patient'], 'Substance_Status': ['current', 'none', 'past']},
          'Drug' : {'Substance_Experiencer':['parent_caregiver', 'patient'], 'Substance_Status': ['current', 'none', 'past']},
          'Education_access' :{'Education_Status': ['yes', 'no']}, 
          'Employment' : {'Employment_Status': ['employed','homemaker','on_disability','retired','student','unemployed']},
          'Food_insecurity' : {'Food_Status' : ['current','past','none']},           
          'Living_arrangement': {'Living_Status':['current','past','future'],
                                'Living_Type' : ['with_both_parents','with_foster','with_other_relatives','with_single_parent','with_strangers'], 
                                'Residence':['institution','home','homeless']},
          'Mental_health' : {'Mental_Status':['current','past','none'],
                             'Mental_Experiencer':['patient','parent_caregiver']},
          'Prior_trauma': {'Prior_Status': ['yes','no'], 
                           'Prior_Type': ['divorce_separation','loss','physical','psychological','domestic_violence','sexual']},
          'Tobacco' : {'Substance_Experiencer':['parent_caregiver', 'patient'], 'Substance_Status': ['current', 'none', 'past']}}

optional_args = {'Alcohol' : ["Amount", "Frequency", "Substance_Type"],
                 'Tobacco': ["Amount", "Frequency", "Substance_Type"],
                 'Drug':["Amount", "Frequency", "Substance_Type"]}

def generate_result_table():
  """
  Generates result table format based on annotation schema.

  returns: dataframe with tabular format to populate results 
  """
  events= []
  arguments =[]
  subtypes =[]

  for k in entity_argument_map:
    event = k
    args = entity_argument_map[k]
    for arg in args:
      if arg == "Trigger":
        sub = [""]
      else:
        sub = valid_argtypes_map[k][arg]
      subtypes.extend(sub)
      events.extend([event]*len(sub))
      arguments.extend([arg]*len(sub))

    if event in optional_args:
      arguments.extend(optional_args[event])
      events.extend([event]*len(optional_args[event]))
      subtypes.extend([""]*len(optional_args[event]))

  
  table_format= pd.DataFrame(list(zip(events,arguments,subtypes)), columns= ["Event", "Argument", "Subtype"])
  table_format.to_csv(out_path+ "annschema.csv")
  return table_format
  

def is_trigger(ele):
  """
  Validates if the input key is a trigger
  """
  if ele.split(" ")[0] in entity_argument_map.keys():
    return True
  return False


def is_valid_span(span, doc_id):
  """ 
  checks if a predicted trigger span is valid or not

  Args:
    span: predicted span: type(str)
    doc_id: file name/id of the original text file
  Returns:
    Boolean value if the span is valid or not
  """

  with open(f"{path_to_txtfiles}/{doc_id}.txt", "r") as f:
    file_contents = f.read()
    if span not in file_contents:
      with open(error_log_file, "a+") as ef:
        ef.write(f"{doc_id} :: Not a valid span {span}\n")
      return False
    return True


def match_trigger(gt_val: str, pred: str):
  """
  performs trigger span overlap match between true span and predicted span

  Returns:
    Boolean based on the match
  """

  return pred in gt_val or gt_val in pred


def parse_content(content, type_set, doc_id):
  """
  Parses the input contents and returns a dictionary
    
  Args: 
    content: prediction to be parsed. This is a string with specific delimiters.
    type_set: [gt/pred] the prefixes vary based on the type
    doc_id: file name/id of the original text file
  Returns:
    a dictionary that has the structure of entity_argument_map
  """
  
  if type_set == 'gt':
    prefixes = gt_prefixes
  elif type_set == 'pred':
    prefixes = pred_prefixes
    
  parsed_content ={x:[] for x in entity_argument_map.keys()}

  prefixes_str = "| ".join(prefixes)
  content = re.split(prefixes_str, content)

  i = 0
  content = [x.strip() for x in content if x.strip() != ""]

  prev_trigger = False
  #identify and fill the triggers first
  for c in content:
    if is_trigger(c):
      parsed_content[c.split(" ")[0]].append({"Trigger" : " ".join(c.split(" ")[1:])})
    
  prev_line = ""

  #this parsing logic is based on the assumption that the event/argument key is at the position 0 followed by their corresponding value at position 1
  for tag_id, c in enumerate(content): 
    if c.lower() in ["", 'and']: #proceed if invalid trigger or arguments
      continue
    
    if c in argument_entity_map:
      try:
        arg_val, trig_val = content[tag_id+1].split(' ', 1)
      except:
        continue #argument predicted but not associated with any trigger
      trig_key = argument_entity_map[c]
      matchfound = False
      if isinstance(trig_key, list): #in case if the trigger is one of alcohol, tobacco and drug
        for trig_key_ele in trig_key:        
          for ent_info in parsed_content[trig_key_ele]:
            if ent_info['Trigger'] == trig_val:
              if c in ent_info:
                continue #This avoids double counting
              ent_info[c] = arg_val
              prev_line = content[tag_id]
              del content[tag_id]
              matchfound = True
              break
          if matchfound:
            break
      else:
        for ent_info in parsed_content[trig_key]:
          if ent_info['Trigger'] == trig_val:
            if c in ent_info:
              continue #This avoids double counting
            ent_info[c] = arg_val
            prev_line = content[tag_id]
            del content[tag_id]
            matchfound = True
            break
      if not matchfound:
        #log error in case of a no match
        with open(error_log_file, "a+") as ef:
          ef.write(f"{doc_id} :: No trigger match found: {c} - {content[tag_id+1]}\n")
    else:
      if (prev_line != "") and (prev_line not in argument_entity_map):
        #log error in case of invalid argument type
        with open(error_log_file, "a+") as ef:
          ef.write(f"{doc_id} :: Not a valid argument type: {c} - {content[tag_id]}\n")
    
  return parsed_content


def compare_dicts(true_dict, pred_dict, consolidated_res, doc_id):
    """
    Compares the ground truth and prediction for each document. 
    Computes NT, NP, TP at the event and argument level

    Args: 
      true_dict: dict 
      pred_dcit: dict
      consolidated_res: pandas dataframe
        In addition to a document level metrics, we create a consolidated metrics sheet that keeps getting updated for each document
      doc_id: file name/id of the original text file

    Returns:
      Two dataframes - one contains metrics for the current processed document and the other is the updated consolidated metrics 
    """

    doc_wise_res = consolidated_res.copy()
    doc_wise_res['NT'] = 0
    doc_wise_res['NP'] = 0
    doc_wise_res['TP'] = 0
    doc_wise_res['gt_Trigger_values'] = ''
    doc_wise_res['pred_Trigger_values'] = ''

    #parse ground truth. Gather NT counts
    for trg_key in true_dict:
      for trig in true_dict[trg_key]:
        for arg, arg_value in trig.items():
          if arg == "Trigger":
            consolidated_res.loc[(consolidated_res['Event']==trg_key) & (consolidated_res['Argument']==arg), 'NT'] += 1
            doc_wise_res.loc[(doc_wise_res['Event']==trg_key) & (doc_wise_res['Argument']==arg), 'NT'] += 1
            doc_wise_res.loc[(doc_wise_res['Event']==trg_key) & (doc_wise_res['Argument']==arg), 'gt_Trigger_values'] += arg_value + "|"
          else:
            consolidated_res.loc[(consolidated_res['Event']==trg_key) & (consolidated_res['Argument']==arg) & (consolidated_res['Subtype'] == arg_value), 'NT'] += 1
            doc_wise_res.loc[(doc_wise_res['Event']==trg_key) & (doc_wise_res['Argument']==arg) & (doc_wise_res['Subtype'] == arg_value), 'NT'] += 1  
          
    
    #parse prediction file. Gather NP counts 
    for trg_key in pred_dict:
      for arg_item_id, trig in enumerate(pred_dict[trg_key]):
        for arg, arg_value in trig.items():
          if arg == "Trigger":
            #check if trigger span is valid. Else, skip the latter validation steps
            if not is_valid_span(arg_value, doc_id):
              pred_dict[trg_key][arg_item_id] = "INVALID"
              break

            consolidated_res.loc[(consolidated_res['Event']==trg_key) & (consolidated_res['Argument']==arg), 'NP'] += 1
            doc_wise_res.loc[(doc_wise_res['Event']==trg_key) & (doc_wise_res['Argument']==arg), 'NP'] += 1
            doc_wise_res.loc[(doc_wise_res['Event']==trg_key) & (doc_wise_res['Argument']==arg), 'pred_Trigger_values'] += arg_value + "|"
          
          else:
            if arg not in valid_argtypes_map[trg_key]:
              with open(error_log_file, "a+") as ef:
                ef.write(f"{doc_id} :: invalid argument type : arg = {arg} trig = {trg_key}")
            if arg_value.lower() not in valid_argtypes_map[trg_key][arg]:
              with open(error_log_file, "a+") as ef:
                ef.write(f"{doc_id} :: invalid argument Sub type : subtype = {arg_value} arg = {arg} trig = {trg_key}")

            consolidated_res.loc[(consolidated_res['Event']==trg_key) & (consolidated_res['Argument']==arg) & (consolidated_res['Subtype'] == arg_value.lower()), 'NP'] += 1
            doc_wise_res.loc[(doc_wise_res['Event']==trg_key) & (doc_wise_res['Argument']==arg) & (doc_wise_res['Subtype'] == arg_value.lower()), 'NP'] += 1

    for trg_key in pred_dict:
      pred_dict[trg_key] = [x for x in pred_dict[trg_key] if x != "INVALID"]
    
    #Compare and compute TP at the trigger and argument level
    
    for trg_key, gt_trig_args in true_dict.items():
      if gt_trig_args == []:
        continue
      pred_trig_args = pred_dict[trg_key]
      if pred_trig_args == []:
        continue

      for g_i, gt_item in enumerate(gt_trig_args):
        if gt_trig_args[g_i] == "gt_matched":
          continue
        assert(list(gt_item.keys())[0]=='Trigger')
        gt_trg_value = gt_item['Trigger']
        for p_i, pred_item in enumerate(pred_trig_args):
          if pred_trig_args[p_i] == "pred_matched":
            continue
          assert(list(pred_item.keys())[0]=='Trigger')
          pred_trg_value = pred_item['Trigger']
          if match_trigger(gt_trg_value.lower(), pred_trg_value.lower()):
            consolidated_res.loc[(consolidated_res['Event']==trg_key) & (consolidated_res['Argument']=='Trigger'), 'TP'] += 1
            doc_wise_res.loc[(doc_wise_res['Event']==trg_key) & (doc_wise_res['Argument']=='Trigger'), 'TP'] += 1

            for arg_key in list(gt_item.keys())[1:]:
              if arg_key in list(pred_item.keys())[1:]:
                if gt_item[arg_key] == pred_item[arg_key]:
                  consolidated_res.loc[(consolidated_res['Event']==trg_key) & (consolidated_res['Argument']==arg_key) & (consolidated_res['Subtype'] == gt_item[arg_key].lower()), 'TP'] += 1
                  doc_wise_res.loc[(doc_wise_res['Event']==trg_key) & (doc_wise_res['Argument']==arg_key) & (doc_wise_res['Subtype'] == gt_item[arg_key].lower()), 'TP'] += 1
            
            gt_trig_args[g_i] = "gt_matched"
            pred_trig_args[p_i] = "pred_matched"
            #to avoid matching the prediction that has already been matched before
            break

    return consolidated_res, doc_wise_res


if __name__ == "__main__":    

  all_docs = {}

  #initiate error log
  with open(error_log_file, "w") as ef:
    ef.write("starting error log..\n")
  
  #initialize a data structure and read and save the truth and predictions to that
  with open(gt_file, "r") as fr:
    for line in fr:
      line = json.loads(line)
      all_docs[line['translation']['document_id']] = {'gt': line['translation']['n2c2'], 'pred' : ""}
  
  if output_type == 'json':
    with open(pred_file, "r") as fr:
      for line in fr:
        line = json.loads(line)
        all_docs[line['translation']['document_id']]['pred'] = line['translation']['n2c2']
  
  elif output_type == 'colondelimited':
    with open(pred_file, "r") as fr:
      for line in fr:
        if ":" in line:
          doc_id, prediction = line.split(":", 1)
          doc_id = str(doc_id.replace("\"", "").strip())
          prediction = str(prediction.replace("\"", "").strip())
          if prediction.endswith(","):
            prediction = prediction[:-1]
            
          all_docs[doc_id]['pred'] = prediction # line['translation']['n2c2']
        else:
          print(line)
    
  #create a reverse map for argument and entity. This is used in parsing the contents of the prediction
  argument_entity_map = {}
  for ent, arg_dict in entity_argument_map.items():
    for arg in arg_dict.keys():
      if arg in ["Amount", "Frequency", "Substance_Experiencer", "Substance_Status", "Substance_Type"]:
        if arg in argument_entity_map:
          argument_entity_map[arg].append(ent)
        else:
          argument_entity_map[arg] = [ent]
      else:
        argument_entity_map[arg] = ent
  
  all_gt_json = {}
  #document level metrics
  all_doc_result_df = pd.DataFrame()

  #consolidated/summary metrics for all the docs
  # result_df = pd.read_csv(result_file)
  result_df = generate_result_table()
  
  result_df['NT'] = 0
  result_df['NP'] = 0
  result_df['TP'] = 0
  
  #process for each doc
  for doc_id, doc_contents in all_docs.items():
    if doc_id in remove_ids:
      continue
       
    gt_content = parse_content(all_docs[doc_id]['gt'], 'gt', doc_id)
    with open(f"{out_path}/gt_test.json", "a+") as f:
      json.dump({doc_id:gt_content}, f)
      f.write("\n")

    all_gt_json[doc_id] = gt_content.copy()
    
    pred_content = parse_content(all_docs[doc_id]['pred'], 'pred', doc_id)

    result_df, doc_result_df = compare_dicts(gt_content, pred_content, result_df, doc_id)
    doc_result_df['doc_id'] = doc_id
    all_doc_result_df= pd.concat([all_doc_result_df, doc_result_df])

  #compute P, R, F1 based on the NT, NP and TP
  result_df['precision'] = [np.round(x/y, 4) if y > 0 else 0 for x, y in zip(result_df['TP'], result_df['NP'])]
  result_df['recall'] = [np.round(x/y, 4) if y > 0 else 0 for x, y in zip(result_df['TP'], result_df['NT'])]
  result_df['f1'] = [np.round((2*x*y)/(x+y), 4) if (x*y) > 0 else 0 for x, y in zip(result_df['precision'], result_df['recall'])]

  #save the results
  result_df.to_csv(out_path + "t5_results.csv", index=False)

  all_doc_result_df.to_csv(out_path + 't5_all_docs.csv', index=False)

