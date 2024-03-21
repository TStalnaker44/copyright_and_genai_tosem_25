# Licensing and Copyright Issues in Using Generative AI for Coding: A Practitioner Perspective

## What is Included
- `scripts/`: Python scripts used for data cleaning, open-coding, reconciliation, and data analysis
- `glossary.json`: Glossary of codes and definitions (per question) resulting from open-coding
- `survey_questions.pdf`: An anonymized PDF of the full survey text (including questions), as seen by participants, produced by Qualtrics
- `questions.json`: A JSON of questions, their associated IDs, and other relevant information
- `tags.json`: A JSON containing the tags / codes used to located repositories and the repositories that were mined for participants

## What is Not Included
In order to fully follow our approved protocol and for the sake of anonymity, individual responses are not included in this replication package.

NOTE: This means that some scripts may not run out of the box.  They require data files in order to function properly.

## Exploring Our Data
As mentioned in our paper, we were not able to cover all of the use cases, benefits, and challenges identified by developers in the survey.  If you wish to explore these and the rest of our data run the script `run_webui.py`.  This tool is capable of carrying out various survey related tasks, but you'll want to focus on the `Data Analysis and Visualization` section.  The first option, `Generate and Explore Plots`, will likely be of greatest interest.

Before running the script you will need to install `Django`.
