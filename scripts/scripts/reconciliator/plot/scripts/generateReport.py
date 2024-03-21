
import json, os
from collections import Counter

SINGLE_ANSWER = ("single-select", "single-select-with-other", "likert", "single-text")
LIST_ANSWER   = ("multi-select", "multi-select-with-other", "short-answer", "cleaned")

def readJson(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

class ReportGenerator():

    def __init__(self):
        self.questions = self.getQuestions()
        self.data = self.getData()
        self.qids = self.getQuestionIDs()
        self.getQuestionInfo()
        self.results = {qid:{} for qid in self.qids}

    def getQuestions(self):
        return readJson(os.path.join("surveys", "ai_legal", "questions.json"))
    
    def getData(self):
        return readJson(os.path.join("surveys","ai_legal", "files", "results.json"))
    
    def getQuestionIDs(self):
        return list(self.data.keys())
    
    def getQuestionText(self, qid):
        return self.qtexts[qid]
        
    def getQuestionInfo(self):
        self.qtypes = {}
        self.qtexts = {}
        for gname, gdata in self.questions.items():
            for qname, qdata in gdata.items():
                self.qtypes[qname] = qdata.get("type")
                self.qtexts[qname] = qdata["question"]
        for qid in self.qids:
            if qid not in self.qtypes:
                self.qtypes[qid] = "cleaned"
                self.qtexts[qid] = self.qtexts[qid.split("_")[0]]
    
    """
    conditions = [{'question':"<question id>",
                   'answers':['a1',a2,a3]}] # This is an OR relationship

    conditions = [{"question":"C3_tools", "answers":["codellama"]},
                  {"question":"C3_tools", "answers":["phind"]}] # This is an AND
    """

    def answerMatch(self, qid, answer, response):
        qtype = self.qtypes[qid]
        if qtype in SINGLE_ANSWER:
            return response.lower() == answer.lower()
        if qtype in LIST_ANSWER:
            return answer.lower() in map(lambda x: x.lower(), response)
        return False

    def getFilteredResponses(self, conditions):
        hits = []
        for condition in conditions:
            qid = condition["question"]
            answers = condition["answers"]
            valid = set()
            for pid, response in self.data[qid].items():
                for a in answers:
                    if self.answerMatch(qid, a, response):
                        valid.add(pid)
            hits.append(valid)
        return set.intersection(*hits)
    
    def getResults(self, qid, valid=None):
        data = self.data[qid]
        if valid == None: valid = list(data.keys())
        results = []
        resp_count = 0
        for pid, response in data.items():
            if pid in valid:
                qtype = self.qtypes[qid]
                if qtype in SINGLE_ANSWER and response != "":   
                    results.append(response)
                    resp_count += 1
                elif qtype in LIST_ANSWER and not response in ([], [""]):
                    results.extend(response)
                    resp_count += 1
        return self.processResults(results, resp_count, qid)
    
    def formatReturn(self, count, total):
        if total:
            percent = round((count/total)*100, 2)
            if percent.is_integer(): percent = int(percent)
        else: percent = 0
        return {"count":count, 
                "percent":percent}
    
    def sortResults(self, result, qid):
        response = result[0]
        count = result[1]
        if self.qtypes[qid] == "likert":
            for gname, gdata in self.questions.items():
                for qname, qdata in gdata.items():
                    if qid == qname:
                        answers = list(qdata["partitions"].values())
                        answers.reverse()
                        return answers.index(response)
        else:
            return count
                        
            
    def processResults(self, results, total, qid):
        results = [(result, count) for result, count in Counter(results).items()]
        answers = self.getPossibleAnswers(qid)
        for a in answers:
            if not any([a == r[0] for r in results]):
                results.append((a, 0)) 
        results = sorted(results, key=lambda x: self.sortResults(x, qid), reverse=True)
        results = {resp:self.formatReturn(count, total) for resp, count in results}
        results["Total Population"] = self.formatReturn(total, total)
        return results
    
    def getPossibleAnswers(self, qid):
        data = self.data[qid]
        responses = set()
        qtype = self.qtypes[qid]
        for response in data.values():
            if qtype in SINGLE_ANSWER and response != "":
                responses.add(response)
            elif qtype in LIST_ANSWER and not response in ([], [""]):
                responses.update(list(response))
        return sorted(list(responses))