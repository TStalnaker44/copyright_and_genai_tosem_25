from django.shortcuts import render
import os

def index(request):
    return render(request, 'home.html')

def addSurveyForm(request):
    return render(request, "add_survey.html")

def add_survey(request):

    if request.method == 'POST':

        survey = request.POST.get("new_survey")

        # Code for adding new survey and directory structure
        path = os.path.join("surveys", survey)
        if not os.path.exists(path):
            os.makedirs(path)
            os.makedirs(os.path.join(path, "files"))
            os.makedirs(os.path.join(path, "data"))
            os.makedirs(os.path.join(path, "figs"))
            return render(request, "success.html", {"survey": survey})
        else:
            return render(request, "failure.html", {"survey": survey})

        