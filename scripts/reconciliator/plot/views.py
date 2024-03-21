from django.shortcuts import render
from .scripts.plotter import Plotter
from .scripts.generateReport import ReportGenerator

def showPlot(request):

    p = Plotter()

    qid = request.GET.get("qid", "C1")
    qpart = request.GET.get("qpart")
    apart = request.GET.get("apart")
    if apart == "SHOW ALL": apart = None
    part = True if request.GET.get("part", "false") == "true" else False

    questions = p.getQuestionIDs()
    if qid not in questions:
        qid = questions[0]

    question_labels = [f"{q}: {p.getQuestionText(q)}" for q in questions]

    questions = list(zip(questions, question_labels))

    answers = [] if not qpart else p.getPossibleAnswers(qpart) + ["SHOW ALL"]
    qtext = p.getQuestionText(qid)   

    data = {}
    labels = [label.replace("'", "`") for label in p.getResults(qid)]
    if (part and qpart) and not apart:
        datasets = []
        for answer in answers[:-1]:
            temp = {}
            temp["label"] = answer.replace("'", "`")
            conditions = [{"question":qpart, "answers":[answer]}]
            valid = p.getFilteredResponses(conditions)
            hits = p.getResults(qid, valid) 
            temp["data"] = [hits.get(label.replace("`", "'"), 0) for label in labels]
            datasets.append(temp)
        data = {"labels":labels, "datasets":datasets}
    elif part and qpart and apart:
        conditions = [{"question":qpart, "answers":[apart]}]
        valid = p.getFilteredResponses(conditions)
        codes = p.getResults(qid, valid)
        labels = [label.replace("'", "`") for label in codes]
        values = list(codes.values())
        data = {"labels":labels, "datasets":[{"label":apart, "data":values}]}
    else:
        values = list(p.getResults(qid).values())
        data = {"labels":labels, "datasets":[{"label":"ALL", "data":values}]} 
        
    height = max(len(labels) * len(data["datasets"]) * 5, 150)

    totals = []
    for value in data["datasets"]:
        totals.append(value["data"][-1])
    totals = str(totals)

    data = str(data)
    
    return render(request, 'plot.html', {"data":data, "questions":questions,
                                         "qid":qid, "qtext":qtext , "qpart":qpart,
                                         "answers":answers, "apart":apart, "part":part,
                                         "height":height, "totals":totals})

def showReport(request):
    
    formats = ["table", "list"]
    report_format = request.GET.get("format", "table")

    # conditions = [{"question":"C3_tools", "answers":["codellama"]},
    #             {"question":"C3_tools", "answers":["phind"]}]
    conditions = []
    rg = ReportGenerator()
    qids = rg.getQuestionIDs()
    report = {}
    for qid in qids:
        qtext = rg.getQuestionText(qid)
        if conditions:
            hits = rg.getFilteredResponses(conditions)
            results = rg.getResults(qid, hits)
        else: 
            results = rg.getResults(qid)
        report[qid] = {"results":results, "qtext":qtext}
    return render(request, 'report.html', {"report":report,
                                           "report_format":report_format})

def showComparisonTable(request):

    qid = request.GET.get("qid", "C1")
    qpart = request.GET.get("qpart", "D5")

    rg = ReportGenerator()
     
    report = {"question":{
                "qid":qid,
                "qtext":rg.getQuestionText(qid),
                "answers":[]},
              "partition":{
                "question":{
                    "qid":qpart, 
                    "qtext":rg.getQuestionText(qpart)},
                "results":{}
                }
            }
    
    questions = rg.getQuestionIDs()
    question_labels = [f"{q}: {rg.getQuestionText(q)}" for q in questions]
    questions = list(zip(questions, question_labels))
    
    results = {}
    answers = rg.getPossibleAnswers(qpart) 
    for answer in answers:
        conditions = [{"question":qpart, "answers":[answer]}]
        hits = rg.getFilteredResponses(conditions)
        results[answer] = rg.getResults(qid, hits)
    report["partition"]["results"] = results

    report["question"]["answers"] = results[list(results.keys())[0]].keys()

    return render(request, 'comparison.html', {"report":report, "questions":questions})