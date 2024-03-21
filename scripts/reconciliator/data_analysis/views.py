from django.shortcuts import render
from .scripts.settings import CONFIG
from .scripts.run_analysis import main as run_analysis
from .scripts.qualtrics_reader import makeQJSON
from datetime import datetime
import os, json

def string_to_bool(s):
    return s.lower() == "true"

def configure_analysis(request):

    surveys = os.listdir("surveys")
    surveys = [s.replace("_", " ").title() for s in surveys]

    return render(request, 'analysis_config.html', {"surveys": surveys})

def uploadQualtricsFile(request):

    surveys = os.listdir("surveys")
    surveys = [s.replace("_", " ").title() for s in surveys]

    return render(request, 'qualtrics_upload.html', {"surveys": surveys})

def uploadDataFile(request):

    surveys = os.listdir("surveys")
    surveys = [s.replace("_", " ").title() for s in surveys]

    return render(request, 'data_upload.html', {"surveys": surveys})

def reviewQuestions(request):

    surveys = os.listdir("surveys")
    surveys = [s.replace("_", " ").title() for s in surveys]
    surveys = os.listdir("surveys")
    surveys = [s.replace("_", " ").title() for s in surveys]

    return render(request, 'ask_for_survey.html', {"surveys": surveys})

def reviewSurveyQuestions(request):

     if request.method == 'POST':
        survey = request.POST['survey'].replace(" ", "_").lower()
        path = os.path.join("surveys", survey, "questions.json")
        with open(path, 'r', encoding="utf-8") as file:
            questions = json.load(file)
        for gname, gdata in questions.items():
            for qname, qdata in gdata.items():
                if qdata.get("options"):
                    qdata["options"] = [i.replace("'", "&#39;") for i in qdata["options"]]
        return render(request, 'review_questions.html', {"questions":questions,
                                                         "question_types":CONFIG.QUESTION_TYPES,
                                                         "survey":survey})

def run_data_analysis(request):

    if request.method == 'POST':
        survey = request.POST['survey']
        from_source = request.POST['from_source']
        pre_process = request.POST['pre_process']
        plot = request.POST.get('plot')
        coding_done = request.POST['coding_done']
        
        CONFIG.set_survey(survey.replace(" ", "_").lower())
        CONFIG.set_from_source(string_to_bool(from_source))
        CONFIG.set_pre_process(string_to_bool(pre_process))
        CONFIG.set_plot(plot)
        CONFIG.set_response_coding_done(string_to_bool(coding_done))

        run_analysis()

        return render(request, 'analysis_complete.html')
    
def createQuestionsFile(request):

    if request.method == 'POST':
        survey = request.POST['survey']
        file = request.FILES['fileUpload']
        new_file_name = survey.replace(" ", "_").lower()
        path = os.path.join("surveys", new_file_name, "files", f"{new_file_name}.qsf")
        with open(path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        makeQJSON(os.path.join("surveys", new_file_name))
        return render(request, 'upload_success.html')
    
def createDataFile(request):

    if request.method == 'POST':
        survey = request.POST['survey']
        file = request.FILES['fileUpload']
        survey_name = survey.replace(" ", "_").lower()
        now = datetime.now().strftime('%m-%d-%y')  # Get the current date and time
        path = os.path.join("surveys", survey_name, "files", f"data_{now}.csv")
        with open(path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return render(request, 'data_upload_success.html')
    
def updateSurveyQuestions(request):
    if request.method == 'POST':

        survey = request.POST['survey']

        path = os.path.join("surveys", survey, "questions.json")
        with open(path, 'r', encoding="utf-8") as file:
            questions = json.load(file)

        to_update = []
        for gname, gdata in questions.items():
            for qname, qdata in gdata.items():
                qdata['type'] = request.POST[f"{qname}_qtype"]
                if request.POST.get(f"{qname}_contains_pii"):
                    qdata['contains_pii'] = True
                if request.POST.get(f"{qname}_convert_to_range"):
                    qdata['convert_to_range'] = True
                if request.POST.get(f"{qname}_coded"):
                    qdata['coded'] = True
                if request.POST[f"{qname}_id"].strip() != qname:
                    to_update.append((gname, qname, request.POST[f"{qname}_id"].strip()))
                    
        for gname, qname, newname in to_update:
            questions[gname][newname] = qdata
            questions[gname].pop(qname)

        with open(path, 'w', encoding='utf-8') as file:
            json.dump(questions, file, ensure_ascii=False, indent=4)

        return render(request, 'data_upload_success.html')