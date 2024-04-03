'''
Helper function to preprocess the data for the significant testing

'''

import pandas as pd
import numpy as np
import tqdm
import pickle
import json

def doccsv_to_json(results_file_path):

  result_json = {}

  schema = {'Adoption': {"Trigger": {}},
          'Alcohol' : {"Trigger": {}, "Substance_Experiencer": {}, "Substance_Status": {}},
          'Drug' : {"Trigger": {}, "Substance_Experiencer":{}, "Substance_Status" : {}},
          'Education_access' : {"Trigger": {}, "Education_Status" : {}}, 
          'Employment' : {"Trigger": {}, "Employment_Status" : {}},
          'Food_insecurity' : {"Trigger": {}, "Food_Status" : {}},           
          'Living_arrangement': {"Trigger": {}, "Living_Status": {}, "Living_Type": {}, "Residence" : {}}, 
          'Mental_health' : {"Trigger": {}, "Mental_Status": {}, "Mental_Experiencer": {}},
          'Prior_trauma': {"Trigger": {}, "Prior_Status": {}, "Prior_Type" : {}},
          'Tobacco' : {"Trigger": {}, "Substance_Experiencer":{}, "Substance_Status" : {} }}
  
  data = pd.read_csv(results_file_path)
  doc_ids = list(np.unique(data['doc_id']))

  def create_doc_id(docid):
    return f"test/{str(docid)}.txt"


  total_nt = 0
  total_np = 0
  total_tp = 0

  for id in tqdm.tqdm(np.unique(data['doc_id']).tolist()):
    #initialize json with schema
    format_id = create_doc_id(id)
    result_json[format_id] = {}#schema

    #fetch from csv
    doc_data = data[data['doc_id']==id]
    for event, event_info in schema.items():#result_json[format_id].items():
      result_json[format_id][event] = {}
      for arg, arg_info in event_info.items():
        if (event in doc_data['Event'].values.tolist()) and (arg in doc_data['Argument'].values.tolist()):
          NT = doc_data[(doc_data['Event'] == event) & (doc_data['Argument'] == arg)]['NT'].sum()
          total_nt += int(NT)
          NP = doc_data[(doc_data['Event'] == event) & (doc_data['Argument'] == arg)]['NP'].sum()
          total_np += int(NP)
          TP = doc_data[(doc_data['Event'] == event) & (doc_data['Argument'] == arg)]['TP'].sum()
          total_tp += int(TP)
        else:
          NT = 0
          NP = 0
          TP = 0

        result_json[format_id][event][arg] = {'NT':int(NT), 'NP':int(NP), 'TP':int(TP)}

  print(total_nt)
  print(total_np)
  print(total_tp)

  return result_json