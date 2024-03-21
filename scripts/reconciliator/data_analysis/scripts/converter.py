
import os, json, itertools, copy, csv, re
from .config import Config

class Converter():

    def __init__(self, survey_folder, file_name):
        self._file_name = file_name
        self._survey_folder = survey_folder
        self.config = Config(survey_folder)
        self.setConfigs()

    def setConfigs(self):
        self._partitions = self.config.partitions
        self._ranked = self.config.ranked
        self._multi = self.config.multi
        self._single = self.config.single
    
    def filterByRole(self, data, targets, pdata, strict=False):
        ids = pdata["partitions"]
        targets = [ids[t] for t in targets] #normalize targets to short form
        pids = list(data.keys())
        for pid in pids:
            group, question = pdata["path"]
            if pdata["type"] == "single":
                roles = data[pid][group][question]
            else:
                roles = data[pid][group][question]["answers"]
            if strict:
                matches = set(targets) == set(roles)
            else:
                matches = all([role in roles for role in targets])
            if not matches:
                data.pop(pid)

    def getValidIDs(self, data):
        """Get the list of valid response IDs"""        
        pids = set(data.keys())
        path = os.path.join(self._survey_folder, "files", "invalid.txt")
        if os.path.isfile(path): 
            with open(path, "r") as file:
                invalids = set([pid.strip() for pid in file.readlines()])
        else: invalids = set()
        return list(pids - invalids)
        
    def getData(self):
        """Read in and save the JSON data"""
        path = os.path.join(self._survey_folder, "files", self._file_name)
        with open(path, "r") as file:
            return json.load(file)

    def removeInvalid(self, data):
        """Remove invalid responses"""
        valid = self.getValidIDs(data)
        pids = list(data.keys())
        for pid in pids:
            if not pid in valid:
                data.pop(pid)

    def getCombos(self, ids):
        combos = []
        for r in range(len(list(ids.keys())) + 1):
            combos.extend(list(itertools.combinations(ids.keys(), r)))
        return combos

    def generateStrictFolder(self, data, pname, pdata):
        parts = pdata["partitions"]
        combos = self.getCombos(parts)
        for r in combos:
            self.run(copy.deepcopy(data), pname, pdata, list(r), True)

    def generateLooseFolder(self, data, pname, pdata):
        parts = pdata["partitions"]
        for r in parts.keys():
            self.run(copy.deepcopy(data), pname, pdata, [r], False)

    def writeToFile(self, participants, path, fieldnames):
        with open(path, "w", newline="", encoding="UTF-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for p in participants:
                writer.writerow(p)

    def generateFiles(self, data, path):
        for question in self._ranked:
            self.rankedAnswer(question, data, path)
        for question in self._multi:
            self.getMultiAnswer(question, data, path)
        self.getAllSingleAnswers(data, path)

    def run(self, data, pname, pdata, roles=[""], strict=False):

        if roles != [""] and roles != []:
            self.filterByRole(data, roles, pdata, strict)

        if len(data) > 0:

            folder = "-".join(roles)
            if folder == "": 
                folder = "all"
                parent = ""
                path = os.path.join(self._survey_folder, "data")
            else:

                if strict: parent = "strict"
                else: parent = "loose"

                path = os.path.join(self._survey_folder, "data", "partitions", pname, parent)
                if not os.path.isdir(path): 
                    os.mkdir(path)

            role_folder_path = os.path.join(path, folder)
            if not os.path.isdir(role_folder_path):
                os.mkdir(role_folder_path)
                os.mkdir(os.path.join(role_folder_path, "rank"))
                os.mkdir(os.path.join(role_folder_path, "multi_select"))
            self.generateFiles(data, role_folder_path)

    def rankedAnswer(self, question, data, path):
        participants = []
        formats = set()
        for p in data.values():
            d = {}
            d["ResponseID"] = p["meta"]["ResponseID"]   
            match = re.match(r"([A-Za-z]+)\d+", question)
            qtype = match.group(1)
            answer = p[self.config.types[qtype]][question] 
            for i, a in answer.items():
                if i != "other" and a != "":
                    full_answer = self.config.ranked_answers[question][int(i)-1]
                    d[full_answer] = a
                    formats.add(full_answer)
            participants.append(d)
        path = os.path.join(path, "rank", question + ".csv")
        self.writeToFile(participants, path, self.config.shared+list(formats))

    def getMultiAnswer(self, question, data, path):

        participants = []
        formats = set()
        
        for p in data.values():

            d = {}
            d["ResponseID"] = p["meta"]["ResponseID"]

            match = re.match(r"([A-Za-z]+)\d+", question)
            qtype = match.group(1)
            answer = p[self.config.types[qtype]][question]
            keyword = "answers"

            if answer[keyword] == [""]:
                d["No Answer"] = 1
                formats.add("No Answer")
            else:
                for a in answer[keyword]:
                    d[a] = 1
                    formats.add(a)
                if answer["other"] != "":
                    d[answer["other"]] = 1
                    formats.add(answer["other"])

            participants.append(d)

        path = os.path.join(path, "multi_select", f"{question}.csv")
        self.writeToFile(participants, path, self.config.shared+list(formats))


    def getAllSingleAnswers(self, data, path):

        participants = []

        for p in data.values():

            d = {}
            d["ResponseID"] = p["meta"]["ResponseID"]

            for group, question in self._single:
                answer = p[group][question]
                if type(answer) == dict:
                    if answer["other"]:
                        d[question] = answer["other"]
                    else:
                        d[question] = answer["answers"]
                else:
                    d[question] = answer

            participants.append(d)

        path = os.path.join(path, "single.csv")
        field_names = self.config.shared + [x[1] for x in self._single]
        self.writeToFile(participants, path, field_names)

    def makePartitionFolder(self, pname):
        path = os.path.join(self._survey_folder, "data", "partitions", pname)
        if not os.path.isdir(path):
            os.mkdir(path)

    def makeTopLevelPartitionFolder(self):
        path = os.path.join(self._survey_folder, "data", "partitions")
        if not os.path.isdir(path):
            os.mkdir(path)

    def main(self):
        data = self.getData()
        # print("Total responses:", len(data))
        self.removeInvalid(data)
        print("Valid responses:", len(data))
        print("Generated CSVs...")
        if len(self._partitions) > 0:
            self.makeTopLevelPartitionFolder()
            for pname, pdata in self._partitions.items():
                self.makePartitionFolder(pname)
                self.generateStrictFolder(data, pname, pdata)
                self.generateLooseFolder(data, pname, pdata)
        else:
            self.run(data, "", {})
        print("Done!")