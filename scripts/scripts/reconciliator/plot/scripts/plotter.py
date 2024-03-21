
import os, json
from collections import Counter
from .generateReport import ReportGenerator
    
class Plotter(ReportGenerator):
    
    def __init__(self):
        ReportGenerator.__init__(self)
    
    # Plotter isn't currently able to support the added percentages from the ReportGenerator
    def processResults(self, results, count, total):
        results = [(result, count) for result, count in Counter(results).items()]
        results = sorted(results, key=lambda x: x[1], reverse=True)
        results = {resp:count for resp, count in results}
        results["Total Population"] = count
        return results
