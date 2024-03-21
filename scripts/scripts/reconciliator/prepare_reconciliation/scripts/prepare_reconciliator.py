
"""
- Complete steps 0-3 to set up The Grand Reconciliator (move database to reconciliator/reconciliator)
- Reconcile the codes
- Then run step 4
"""
from .comparer import main as comparer
from .to_json import main as to_json
from .pull_comments import main as pull_comments
from .createDB import main as createDB
from .populateDB import main as populateDB

def main():
    comparer()
    to_json()
    pull_comments()
    createDB()
    populateDB()