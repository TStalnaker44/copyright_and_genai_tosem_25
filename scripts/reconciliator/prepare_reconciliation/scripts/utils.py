
import os, csv, json
from .resp_config import REC_CONFIG
from itertools import combinations

input_file_template = "coder_%d.csv" # Format of the coded file names

def getQuestions():
    path = os.path.join(REC_CONFIG.PATH, "questions.json")
    with open(path, "r", encoding="utf-8") as file:
        d = json.load(file)
        questions = []
        for gdata in d.values():
            for qname, qdata in gdata.items():
                if qdata.get("coded"):
                    questions.append(qname)
        return questions
    
def getPidFilter():
    path = os.path.join(REC_CONFIG.PATH, "files", "invalid.txt")
    if os.path.isfile(path): 
        with open(path, "r") as file:
            return {int(pid.strip()) for pid in file.readlines()}
    else: 
        return set()


def all_combinations(input_list):
    all_combinations_list = []
    for r in range(1, len(input_list) + 1):
        all_combinations_list.extend(combinations(input_list, r))
    return ["".join(combo) for combo in all_combinations_list]

def readCodeFiles(questions):
    codes = []
    for x in range(REC_CONFIG.CODERS):
        path = input_file_template % (x+1,)
        path = os.path.join(REC_CONFIG.PATH, "response_coding", "code_files", path)
        codes.append(readCSVFile(path, questions))
    return codes
    
def readCSVFile(path, questions):
    d = {}
    with open(path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for i, row in enumerate(reader):
            if i > 0:
                pid = row[0]
                if pid.strip() != "" and not int(pid) in getPidFilter():
                    d[pid] = {}
                    for j, column in enumerate(questions):
                        codes = row[j+2].strip()
                        if codes == "":
                            codes = "[]"
                        codes = {c.strip() for c in eval(codes)}
                        d[pid][column] = codes
    return d