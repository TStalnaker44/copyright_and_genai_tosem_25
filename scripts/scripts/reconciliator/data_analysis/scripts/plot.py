import json, os, textwrap, glob, importlib
import pandas as pd

from .pathmanager import PathManager
from .config import Config

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

labels = ["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"]

def main():
    directory = "survey"
    plot(directory)

def plot(directory, file_type="png"):
    Plotter(directory, file_type).run()

class Plotter():

    def __init__(self, directory, file_type="png"):

        self._show_total = True
        self._dir = directory
        self._file_type = file_type
        self._path = PathManager(directory)
        self._q_map = self.getQuestionsFromFile()
        config = Config(directory)
        self._likert = config.likert
        self._partitions = config.partitions
        self._convertToRange = config.convertToRange

    def getQuestionsFromFile(self):
        with open(os.path.join(self._dir, "questions.json"), "r") as file:
            d = {}
            for questions in json.load(file).values():
                for qid, qdata in questions.items():
                    d[qid] = qdata["question"]
            return d
        
    def run(self):

        self._path.role = ""
        print(f"Now plotting all data...")
        self.generatePlots()

        if len(self._partitions) > 0:
            self._path.makeTopLevelPartDirectory()

        for pname in self._partitions.keys():

            self._path.setPartition(pname)

            self._path.strict = True
            for r in self.getStrictRoles(pname):
                self._path.role = r
                print(f"Now plotting {r}s at strict level...")  
                self.generatePlots()

            self._path.strict = False
            for r in self.getLooseRoles(pname):
                self._path.role = r
                print(f"Now plotting {r}s at loose level...")  
                self.generatePlots()
  
    def getStrictRoles(self, pname):
        path = os.path.join(self._dir, "data", "partitions", pname, "strict")
        if os.path.isdir(path):
            return os.listdir(path)
        else: return []

    def getLooseRoles(self, pname):
        path = os.path.join(self._dir, "data", "partitions", pname, "loose")
        if os.path.isdir(path):
            return os.listdir(path)
        else: return []

    def generatePlots(self):
        self.plotSingleAnswerQuestions()
        multi = self.getQuestions("multi_select")
        self.plotMultiAnswerQuestions(multi)
        ranked = self.getQuestions("rank")
        self.plotRankedQuestions(ranked)
        self.plotSpreadForRankedQuestions(ranked)
        path = os.path.join(self._path.getDataPath(), "response_coding.csv")
        if os.path.isfile(path):
            self.plotCodingQuestions()

    def getQuestions(self, folder):
        files = glob.glob(os.path.join(self._path.getDataPath(), folder) + os.sep + "*")
        return list(map(lambda x: x.split(os.sep)[-1][:-4], files))

    def readCSVFile(self, file, folder=""):
        path = self._path.getDataPath()
        if folder != "":
            return pd.read_csv(os.path.join(path, folder, file))
        else:
            return pd.read_csv(os.path.join(path, file))
        
    def plotFigure(self, q, data, log=False, name=""):
        plt.close() # in case any plots are open
        if len(data) > 0:
            plt.figure(figsize=(18, 14))
            ax = data.plot(kind="bar", logy=log)
            for bars in ax.containers:
                ax.bar_label(bars)
            plt.xlabel("Response")
            plt.ylabel("Count")
            plt.title(textwrap.fill("%s (%s) - %s" % (q, self._path.role, self._q_map[q.upper()]),70))
            plt.gcf().subplots_adjust(bottom=0.2)
            self.cleanAxisLabels(ax)    

            if name == "":
                name = q
            name += "." + self._file_type

            path = os.path.join(self._path.getFigPath(), name)
            plt.savefig(path)
            plt.close()

    def cleanAxisLabels(self, ax):
        labels = []
        for label in ax.get_xticklabels():
            text = str(label.get_text())
            text = text.replace("_", " ")
            text = textwrap.shorten(text, 160, placeholder="...")
            text = textwrap.fill(text, 35)
            labels.append(text)
        plt.xticks(rotation=90, ha='center')
        ax.set_xticklabels(labels)

    def convertToYearRange(self, clean):
        resps = []
        for v in clean:
            for l, h in [(0,10), (11,20), (21,30), (31,40),(41,50)]:
                if v >= l and v <= h: resps.append("%2d-%2d" % (l,h))
        return pd.Series(resps).value_counts()


    def plotSingleAnswerQuestions(self):

        df_single = self.readCSVFile("single.csv")

        for q in df_single.columns[1:]:

            clean = df_single[q].dropna()

            if len(clean) > 0:
            
                if q in self._likert:
                    clean = clean.value_counts().reindex(labels, fill_value=0)
                elif q in self._convertToRange:
                    clean = self.convertToYearRange(clean)
                else:
                    clean = clean.value_counts()

                if self._show_total:
                    total_count = clean.sum()
                    clean = pd.concat([clean, pd.Series(total_count, index=["Total"])]) 

                self.plotFigure(q, clean)

    def plotMultiAnswerQuestions(self, questions):
        for q in questions:
            
            df = self.readCSVFile(f"{q}.csv", "multi_select")

            df.drop(df.columns[0], axis=1, inplace=True)
            if "No Answer" in df.columns:
                df.drop(columns=["No Answer"], inplace=True)
            
            clean = df.sum().sort_values(ascending=False)

            if self._show_total:
                total_count = df.notnull().any(axis=1).sum()
                clean = pd.concat([clean, pd.Series(total_count, index=["Total"])])

            self.plotFigure(q, clean)

    def plotRankedQuestions(self, questions):
        for q in questions:
            df = self.readCSVFile(f"{q}.csv", "rank")
            df.drop(df.columns[0], axis=1, inplace=True)
            clean = df.mean().round(2).sort_values(ascending=True)
            self.plotFigure(q, clean)

    def plotSpreadForRankedQuestions(self, questions):
        for q in questions:
            df = self.readCSVFile(f"{q}.csv", "rank")
            df.drop(df.columns[0], axis=1, inplace=True)
            clean = df.apply(pd.Series.value_counts)
            if len(clean.columns) > 0:
                self.plotFigure(q, clean, True, q + "_spread")

    def plotCodingQuestions(self):

        df = self.readCSVFile("response_coding.csv")
        df.drop(df.columns[[0,1]], axis=1, inplace=True)

        for q in df.columns:

            if not q.lower().startswith("unnamed:"): #needed for backwards compatibility
            
                tags = [tag for lyst in df[q].dropna() for tag in eval(lyst)]
                if len(tags) > 0:

                    tags = pd.Series(tags)
                    
                    clean = tags.value_counts().sort_values(ascending=False)

                    if self._show_total:
                        total_count = df[q].count()
                        clean = pd.concat([clean, pd.Series(total_count, index=["Total"])])

                    if self._dir == "key_projects":
                        q = q.split(" ")[0]

                    self.plotFigure(q, clean)

if __name__ == "__main__":
    main()
