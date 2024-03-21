from django.shortcuts import render, redirect
from .scripts.utils import CODES
from django.http import JsonResponse

# Create your views here.
def chooseCodes(request):
    qid = request.GET.get("qid") or "C5"
    codes = CODES.get(qid)
    questions = CODES.getQuetions()
    return render(request, 'choose_codes.html', {"codes":codes,
                                                 "questions":questions,
                                                 "qid":qid})

def reloadCodes(request):
    CODES.updateCodes()
    return redirect(request.META.get('HTTP_REFERER', '/'))

def searchCodes(request, question_id, term):
        hits = CODES.search(term, question_id)
        return render(request, "search_results.html", {"hits":hits})
    