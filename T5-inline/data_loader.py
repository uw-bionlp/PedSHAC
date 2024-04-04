from utils import *
from glob import glob
from tqdm import tqdm
import copy
import json

def parse_pred(pred,text,top='[SEP]'):
    pred=pred.replace('[none]','').split(top)
    return [p for p in pred if p in text and p], [p for p in pred if p not in text]

def read_line(l):
    if l[0]=="T":
        span_idx=l.split()[0]
        span_type=l.split()[1]
        words=l.split("\t")
        start,end=int(words[1].split()[1]),int(words[1].split()[-1])
        return span_idx,span_type,start,end
    return None,None,None,None

def read_labels(target,anns):
    output=[line for line in anns if line[0]=="E" and line.split()[1]==target]
    assert len(output)==1
    result=[]
    for word in output[0].split()[2:]:
        result.append(word.split(":")[1])
    
    final_result={}
    for line in anns:
        if line[0]=="A":
            words=line.split()
            if words[2] in result:
                final_result[words[1].replace("Val","")]=words[-1]

    return final_result

def load_data_triggers(data_dir):
    files=glob(f"{data_dir}/*.txt")
    counts={}
    for trigger in Trigger_type:
        counts[trigger]=0
    with open(f"{data_dir}_trigger.jsonl","w") as f:
        for file in tqdm(files):
            text=open(file).read()

            anns=open(file.replace(".txt",".ann")).read().split("\n")
            labels=[]
            for line in anns:
                if line and line[0]=="T":
                    ann=line.split()
                    if ann[1] in Trigger_type:
                        ann=line.split("\t")[1].split()
                        span="\t".join(line.split("\t")[2:])
                        label_type,start,end=ann[0],int(ann[1]),int(ann[-1])
                        labels.append([label_type,start,span])

            labels.sort(key=lambda x: x[1])
            
            for trigger in Trigger_type:
                output="[SEP]".join([span for label_type,start,span in labels if label_type==trigger])
                if output=='':
                    output='[none]'
                counts[trigger]+=output.count('[SEP]')+1 if output!='[none]' else 0
                json.dump({"id":f"{file}-{trigger}",
                            'instruction':f'Extract all the {trigger} text spans as it is from {note_descrition}. If multiple spans present, separate them by [SEP]. If none of the events presents, output [none].',
                            "input":text,
                            'options':"",
                            "output":output},f)
                f.write("\n") 
    return

def load_data_arguments(data_dir):
    files=glob(f"{data_dir}/*.txt") 
    with open(f"{data_dir}_arguments.jsonl","w") as f:
        for file in tqdm(files):
            text=open(file).read()

            anns=[l for l in open(file.replace(".txt",".ann")).read().split("\n") if l]
            for l in anns:
                span_idx,trigger,start,end=read_line(l)
                if trigger and trigger in Trigger_type:
                    if trigger=="Adoption":
                        continue
                    true_arguments=read_labels(f"{trigger}:{span_idx}",anns)
                    for argument in ARGUMENTS_BY_EVENT_TYPE[trigger]:
                        span=text[start:end]
                        target_text=copy.deepcopy(text)
                        target_text=target_text[:start]+"<"+target_text[start:end]+">"+target_text[end:]

                        options=[]
                        for i in range(len(SUBTYPES_BY_ARGUMENT[argument])):
                            options.append(f'({choices[i]}) {SUBTYPES_BY_ARGUMENT[argument][i]}.')
                        if argument in [LIVING_TYPE, RESIDENCE]:
                            options.append(f'({choices[len(SUBTYPES_BY_ARGUMENT[argument])]}) Not Applicable - {argument} is not mentioned for the event {span}({trigger}).')

                        if argument in true_arguments:
                                i=SUBTYPES_BY_ARGUMENT[argument].index(true_arguments[argument])
                                answer=f'({choices[i]}) {SUBTYPES_BY_ARGUMENT[argument][i]}.'
                        else:
                            assert argument in [LIVING_TYPE, RESIDENCE]
                            answer=options[-1]
                        
                        json.dump({"id":f"{file}-{span}({trigger})-{argument}",
                                    'instruction':f'Choose the best {argument} value for the <{span}> ({trigger}) from {note_descrition}: ',
                                    "input":f"{target_text}\n",
                                    'options':f'Options: '+" ".join(options),
                                    "output":answer},f)
                        f.write("\n") 
    return

def load_data_arguments_pred_trigger(out_name,pred_file,data_dir):
    files=glob(f"{data_dir}/*.txt")
    pred_dic=json.loads(open(pred_file).read().replace("valid/","eval/"))
    with open(out_name,"w") as f:
        for file in tqdm(files):
            text=open(file).read()
            for trigger in ARGUMENTS_BY_EVENT_TYPE:
                id=f"{file}-{trigger}"
                if id in pred_dic:
                    spans,__=parse_pred(pred_dic[id],text)
                    for span in spans:
                            target_text=text.replace(span,f"<{span}>")
                            for argument in ARGUMENTS_BY_EVENT_TYPE[trigger]:
                                options=[]
                                for i in range(len(SUBTYPES_BY_ARGUMENT[argument])):
                                    options.append(f'({choices[i]}) {SUBTYPES_BY_ARGUMENT[argument][i]}.')
                                if argument in [LIVING_TYPE, RESIDENCE]:
                                    options.append(f'({choices[len(SUBTYPES_BY_ARGUMENT[argument])]}) Not Applicable - {argument} is not mentioned for the event {span}({trigger}).')
                                
                                json.dump({"id":f"{file}-{span}({trigger})-{argument}",
                                            'instruction':f'Choose the best {argument} value for the <{span}> ({trigger}) from {note_descrition}: ',
                                            "input":f"{target_text}\n",
                                            'options':f'Options: '+" ".join(options),
                                            "output":""},f)
                                f.write("\n") 
                else:
                    print(id)
    return


if __name__ == "__main__":
    # converting the source data to the T5 format
    for split in ['train','test','valid']:
        load_data_triggers(split)
        load_data_arguments(split)
    



