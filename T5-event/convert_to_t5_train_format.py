"""

***code to encode and decode the data format for running T5 experiments.***

For example, the dictionary contains: 
{"id": "eval/10016.txt-Adoption", "instruction": 
"Extract all the Adoption events from this clinical note as it is, separated by comma.", Rewrite the following text by extracting the relevant social history events" 
"input": "SOCIAL HISTORY:\n\nDenies smoking, former heroin use", "output": ""}  
where I use "instruction" + "\n"+ "input" as the query. If you want, you could also use a key like "prompt" to put instruction and input together.
For the predictions, I will output a dictionary, where the key is the "id" and the value is the predicted output. 

"""
import json
import glob
import re

path = "/home/NETID/gramacha/projects/ped_sdoh/converted_data/"

def encode(data_types):
  for data_type in data_types:
    with open(path + f"{data_type}_t5_converted.json", "w") as fw:
      with open(path + f"{data_type}_t5.json", "r") as fr:
        for line in fr:
          input_line = json.loads(line)
          input = input_line['translation']
          output = {"id" : input['document_id'], 
                    "instruction" : "Rewrite the following text by extracting the relevant social history events", 
                    "input": input['en'],
                    "output": input['n2c2']
                    }
          fw.write(json.dumps(output))
          fw.write("\n")
