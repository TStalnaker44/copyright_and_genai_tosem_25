import requests, csv, openpyxl, shutil

class CodeBook():

    _INSTANCE = None

    @classmethod
    def instance(cls):
        if cls._INSTANCE is None:
            cls._INSTANCE = cls._CodeBook()
        return cls._INSTANCE
    
    class _CodeBook():
        def __init__(self):
            # self.updateCodes()
            pass

        def updateCodes(self):
            self.loadCodeBook()
            self.codes = self.getCodes()
            self.addDefinitions()

        def filterCodes(self, codes):
            new_codes = []
            for code, definition in codes.items():
                if code != "" and not code.startswith("--"):
                    if definition == "": 
                        definition = "No definition available. Try downloading latest code book."
                    new_codes.append((code, definition))
            new_codes.sort(key=lambda x: x[0])
            return new_codes

        def get(self, qid):
            return self.filterCodes(self.codes[qid])
        
        def getQuetions(self):
            return list(self.codes.keys())
        
        def search(self, term, qid):
            term = term.lower()
            hits = {}
            codes = self.codes[qid]
            for code, definition in codes.items():
                if term in code.lower() or term in definition.lower():
                    definition = definition.replace("&#39;","'")
                    hits[code] = definition
            return hits

        def loadCodeBook(self):
            spreadsheet_id = "" # Made blank for anonymity
            sheet_name = "" # Made blank for anonymity
            url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
            response = requests.get(url)
            if response.status_code == 200:
                with open("downloaded_sheet.csv", "wb") as file:
                    file.write(response.content)
            else:
                print(f"Failed to download CSV. Status code: {response.status_code}")

        def getCodes(self):
            with open("downloaded_sheet.csv", "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                codes = {}
                for i, row in enumerate(reader):
                    if i == 0:
                        questions = row
                        for column in row:
                            if column != "": codes[column] = {}
                    else:
                        for j, column in enumerate(row):
                            if column != "":
                                codes[questions[j]][column] = ""
                return codes
            
        def addDefinitions(self):
            path = "downloaded_sheet.xlsx"
            workbook = openpyxl.load_workbook(path)
            sheet = workbook['Selection Options']

            def getDefinition(comment):
                if comment is None:
                    return ("", "")
                else:
                    comment = comment.text.split('\n\t-')
                    return (comment[0], comment[-1])
                
            questions = self.getQuetions()
            # Iterate over columns
            for i, column in enumerate(sheet.iter_cols(min_col=1, max_col=len(questions), min_row=3)):
                for cell in column:
                    term = cell.value
                    definition, author = getDefinition(cell.comment)
                    if term != None:
                        definition = definition.replace("'", "&#39;")
                        self.codes[questions[i]][term] = definition
            return self.codes

CODES = CodeBook.instance()

