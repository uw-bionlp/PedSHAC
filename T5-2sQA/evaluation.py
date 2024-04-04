from utils import *
import os
import json
import re

def itemize(ls):
    if isinstance(ls, str):
        ls=ls.split(",")
    #return [w.strip() for w in ls if w!='']
    return list(set([w.strip() for w in ls if w!='']))

def check_overlap(s1, s2):
    # Slide s1 over s2
    for i in range(1 - len(s1), len(s2)):
        overlap = ''.join([s1[j] for j in range(len(s1)) if 0 <= j + i < len(s2) and s1[j] == s2[j + i]])
        if overlap == s1 or overlap == s2:
            return True

def evaluate(scores,tl,pl,by_overlap=False):
    # tl=itemize(tl)
    # pl=itemize(pl)
    
    scores[0]+=len(tl)
    scores[1]+=len(pl)
    if by_overlap:
        mapped_p=[]
        for t2 in tl:
            for t1 in pl:
                if t1 in mapped_p:
                    continue
                if check_overlap(t1,t2): 
                    scores[2]+=1
                    mapped_p.append(t1)
                    break

    else:
        scores[2]+=len([t for t in tl if t in pl])
        # for t in tl:
        #     if t not in pl:
        #         print("flag")
        #         print([tl,pl])
    return scores

def sum_ls(dic,k="", negation=False):
    if negation:
        ls=[dic[key] for key in dic if k not in key and "Overall" not in key and ',None,' not in key ]
    else:
        ls=[dic[key] for key in dic if k in key  and "Overall" not in key and ',None,' not in key ]

    return [sum(sublist) for sublist in zip(*ls)]


def read_scores(filenames):
    scores={}
    for filename in filenames:
        lines=open(filename).readlines()
        
        for line in lines:
            if line:
                if 'Living_arrangement,Residence,None,0,' in line or \
                'Living_arrangement,Living_Type,None,0,' in line:
                    continue
                words=line.split(",")
                assert len(words)==9,filename
                if words[0].lower()=="event" or "overall" in line.lower():
                    continue
                key=",".join(words[:2])
                scores[key]=scores.get(key,[0]*3)
                for i in range(3,6):
                    scores[key][i-3]+=int(words[i])

    
    scores['Overall,'] = sum_ls(scores,"")
    scores['Overall,Trigger'] = sum_ls(scores,"Trigger")
    scores['Overall,Labeled-argument'] = sum_ls(scores,"Trigger",negation=True)
    return scores

def merge_scores(scores):
    new_scores = {}

    new_scores["Overall,"] = calc_scores(scores.get("Overall,", [0, 0, 0]))
    new_scores["Overall,Trigger"] = calc_scores(scores.get("Overall,Trigger", [0, 0, 0]))
    new_scores["Overall,Labeled-argument"] = calc_scores(scores.get("Overall,Labeled-argument", [0, 0, 0]))

    new_scores["Adoption,Trigger"] = calc_scores(scores.get("Adoption,Trigger", [0, 0, 0]))

    new_scores["Education_access,Trigger"] = calc_scores(scores.get("Education_access,Trigger", [0, 0, 0]))
    new_scores["Education_access,Education_Status"] = calc_scores(scores.get("Education_access,Education_Status", [0, 0, 0]))

    new_scores["Living_arrangement,Trigger"] = calc_scores(scores.get("Living_arrangement,Trigger", [0, 0, 0]))
    new_scores["Living_arrangement,Living_Status"] = calc_scores(scores.get("Living_arrangement,Living_Status", [0, 0, 0]))
    new_scores["Living_arrangement,Living_Type"] = calc_scores(scores.get("Living_arrangement,Living_Type", [0, 0, 0]))
    new_scores["Living_arrangement,Residence"] = calc_scores(scores.get("Living_arrangement,Residence", [0, 0, 0]))

    new_scores["Employment,Trigger"] = calc_scores(scores.get("Employment,Trigger", [0, 0, 0]))
    new_scores["Employment,Employment_Status"] = calc_scores(scores.get("Employment,Employment_Status", [0, 0, 0]))

    new_scores["Food_insecurity,Trigger"] = calc_scores(scores.get("Food_insecurity,Trigger", [0, 0, 0]))
    new_scores["Food_insecurity,Food_Status"] = calc_scores(scores.get("Food_insecurity,Food_Status", [0, 0, 0]))

    new_scores["Prior_trauma,Trigger"] = calc_scores(scores.get("Prior_trauma,Trigger", [0, 0, 0]))
    new_scores["Prior_trauma,Prior_Status"] = calc_scores(scores.get("Prior_trauma,Prior_Status", [0, 0, 0]))
    new_scores["Prior_trauma,Prior_Type"] = calc_scores(scores.get("Prior_trauma,Prior_Type", [0, 0, 0]))

    new_scores["Mental_health,Trigger"] = calc_scores(scores.get("Mental_health,Trigger", [0, 0, 0]))
    new_scores["Mental_health,Mental_Status"] = calc_scores(scores.get("Mental_health,Mental_Status", [0, 0, 0]))
    new_scores["Mental_health,Mental_Experiencer"] = calc_scores(scores.get("Mental_health,Mental_Experiencer", [0, 0, 0]))

    # For aggregated values from multiple keys
    substance_keys = ["Tobacco,Trigger", "Drug,Trigger", "Alcohol,Trigger"]
    aggregated_values = [sum(sublist) for sublist in zip(*[scores.get(key, [0, 0, 0]) for key in substance_keys])]

    new_scores["Substance,Trigger"] = calc_scores(aggregated_values)
    new_scores["Substance,Status"] = calc_scores(sum_ls(scores, "Substance_Experiencer"))
    new_scores["Substance,Experiencer"] = calc_scores(sum_ls(scores, "Substance_Status"))

    return new_scores

def calc_scores(ls):
    if not ls:
        ls=[0]*3
    NT,NP,TP=ls
    Pre=round(TP*100.0/NP,3) if NP else 0
    Rec=round(TP*100.0/NT,3) if NT else 0
    F1=round(2*Pre*Rec/(Pre+Rec),3) if Pre+Rec>0 else 0
    return NT,Pre,Rec,F1

def print_scores(all_scores,out_csv,wtype="w",start_index=10):
    with open(out_csv,wtype) as f:
        triggers=list(all_scores.keys())
        triggers.sort()
        # if ',' not in triggers[0]:
        #     overall_key='Overall,Trigger,'
        # else:
        #     overall_key='Overall,labeled,'
        
        all_scores["Overall"]=[0]*3

        for i in range(3):
                all_scores["Overall"][i]=sum([all_scores[key][i] for key in all_scores if key!='Overall'])

        for trigger in triggers+['Overall']:
                NT,NP,TP=all_scores[trigger]
                _,Pre,Rec,F1=calc_scores([NT,NP,TP])
                if "," not in trigger:
                    trigger+=",Trigger,"
                f.write(trigger+","+",".join([str(s) for s in [NT,NP,TP,Pre,Rec,F1]])+"\n")

    return all_scores

def parse_pred(pred,text,top='[SEP]'):
    pred=pred.replace('[none]','').split(top)
    
    return [p for p in pred if p in text and p], [p for p in pred if p not in text]

def read_triggers(s,ttype):
    
    pattern = r'-(.*?)\({}\)'.format(re.escape(ttype))
    match = re.search(pattern, s.replace('\n',' '))
    assert match, [s,pattern]
    return match.group(1)

def read_trigger_type(s):
    return [f"{ttype}" for ttype in ARGUMENTS_BY_EVENT_TYPE if ttype in s][0]

# print results for the gold_triggers
def find_value(ls,target_str,prefix=" "):
    result=[t for t in ls if prefix+t in target_str]
    assert len(result)>=1,[target_str,result]
    if len(result)==1:
        return result[0]
    elif len(result)==2:
        return result[0] if len(result[0])>len(result[1]) else result[1]
    assert False,[target_str,result]
    return result[0]

def find_trigger_type(s):
     matches = re.findall(r'\((.*?)\)', s)
     assert len(matches)>=1,s
     return matches[-1]

def evaluate_trigger(source,pred_file,out_csv):
    by_overlap=True
    Npre,Nhull=0,0
    pred=json.loads(open(pred_file).read().replace("\"valid/","\"eval/"))
    all_labels={}
    
    outlier_dic={}
    for line in open(source).readlines():
                if line:
                    dic=json.loads(line)
                    if dic['id'] not in pred:
                            continue
                    trigger=dic['id'].split('-')[1]
                    id=dic['id']
                    all_labels[id]=all_labels.get(id,[[],[]])
                    all_labels[id][0],__=parse_pred(dic['output'],dic['input'],top='[SEP]')
                    pred_s,outlier=parse_pred(pred[dic['id']],dic['input'],top='[SEP]')
                    all_labels[id][1].extend(pred_s)
                    if outlier:
                                outlier_dic[dic['id']]={
                                    "note":dic['input'],
                                    "pred":outlier,
                                }
                    Npre+=len(pred_s)
                    Nhull+=len(outlier)

    #print(f"------------evaluating by overlap: {by_overlap}")
    all_scores={}                
    for id in all_labels:
            trigger=id.split('-')[1]
            all_scores[trigger]=evaluate(all_scores.get(trigger,[0]*3),
                                    all_labels[id][0],
                                    all_labels[id][1],
                                    by_overlap)
        
    print_scores(all_scores,out_csv,"w")

    with open(pred_file.replace('.json',"_outlier.json"),"w") as f:
        json.dump(outlier_dic,f,indent=4)
    
    print('{}{} - hallucination rate {:.1f}'.format(pred_file,100.0*Nhull/(Nhull+Npre)))
    return

def evaluate_arguments(source,pred_file,out_csv):
    pred=json.loads(open(pred_file).read().replace("\"valid/","\"eval/"))
    all_scores={}
    for ttype in ARGUMENTS_BY_EVENT_TYPE:
        for argument in ARGUMENTS_BY_EVENT_TYPE[ttype]:
            for subtype in SUBTYPES_BY_ARGUMENT[argument]:
                key=",".join([ttype,argument,subtype])
                all_scores[key]=[0]*3

    # finding the true labels
    source_dic={}    
        
    for line in open(source).readlines():
            if line:
                dic=json.loads(line)
                id=dic['id']
                ttype=read_trigger_type(id)
                trigger=read_triggers(id,ttype)
                argument=find_value(ARGUMENTS_BY_EVENT_TYPE[ttype],id,prefix='-')
                #NT
                if 'Not Applicable' not in dic['output']:
                    subtype=find_value(SUBTYPES_BY_ARGUMENT[argument],dic['output'])
                    dic_key=(id.split("-")[0],ttype,trigger)
                    source_dic[dic_key]=source_dic.get(dic_key,{})
                    source_dic[dic_key][argument]=subtype
                    pred_key=",".join([ttype,argument,subtype])
                    all_scores[pred_key][0]+=1
    event_dic={}
    for id in pred:
                if 'Not Applicable' not in  pred[id]:
                    ttype=read_trigger_type(id)
                    trigger=read_triggers(id,ttype)
                    argument=find_value(ARGUMENTS_BY_EVENT_TYPE[ttype],id,prefix='-')
                    pred_subtype=[t for t in SUBTYPES_BY_ARGUMENT[argument] if f") {t}" in pred[id]]
                    
                    if len(pred_subtype)>1:
                        if pred_subtype==['home','homeless']:
                            pred_subtype=['homeless']
                        else:
                            print([pred_subtype,pred[id],id])
                            continue
                    elif len(pred_subtype)==1:
                        # pred_subtype=['invalid']
                        pred_subtype=pred_subtype[0]
                        pred_key=",".join([ttype,argument,pred_subtype])
                        all_scores[pred_key][1]+=1
                        # find corresponding trigger:
                        candididate_triggers=[key for key in source_dic if key[0]==id.split("-")[0] and key[1]==ttype]
                        ekey=(id.split("-")[0],ttype,trigger)
                        event_dic[ekey]=event_dic.get(ekey,{})
                        event_dic[ekey][argument]=pred_subtype
                        #print(trigger,ct)
                        for ct in candididate_triggers:
                            if check_overlap(trigger,ct[-1]):
                                if pred_subtype==source_dic[ct].get(argument,"INVALID"):
                                    all_scores[pred_key][2]+=1
                                    source_dic[ct][argument]="INVALID"
                                    
                                    break
                        
    print_scores(all_scores,out_csv)
    with open(pred_file.replace('GPT_predictions/','analysis_event_level/GPT_').replace('predictions/','analysis_event_level/'),"w") as f:
            json.dump([[key,item] for key, item in event_dic.items() ],f,indent=2)
    return
if __name__ == "__main__":

    source='' # input file to T5
    pred_file='' # predicted file from T5
    out_csv='' # the desired evaluation output

    #choose one below
    evaluate_trigger(source,pred_file,out_csv)
    #evaluate_arguments(source,pred_file,out_csv)

