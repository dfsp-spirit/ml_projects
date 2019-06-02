#!/usr/bin/env python
#
# This script parses Wahlomat data provided by gockelhahn and performs some basic analyses
#
# This is a python3 script, run it with: `python3 wahlomat-analysis.py`
#
# written by Tim Schaefer

import os
import json
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

def wahlomat_analysis():
    merged_df, all_data, raw_data = load_data()
    #export_data(df, 'data_merged.csv')
    num_parties = all_data["party"].shape[0]
    num_statements = all_data["statement"].shape[0]
    print("Received data on %d parties, all of which answered %d different statements." % (num_parties, num_statements))
    answers = np.zeros((num_parties, num_statements), dtype=np.int)

    for o in raw_data["opinion"]:
        #print(o)
        party_idx = o["party"]
        statement_idx = o["statement"]
        answers[party_idx][statement_idx] = o["answer"]

    #print(answers)
    a_f = fix_answer_values(answers)
    #print(a_f)

    party_names = [p["name"] for p in raw_data["party"]]
    statement_long_texts = [s["text"] for s in raw_data["statement"]]
    statement_short_labels = [s["label"] for s in raw_data["statement"]]
    fixed_answers = ["Ja", "Egal", "Nein"]

    #plt.matshow(pd.DataFrame(a_f).corr())
    #plt.show()

    # Create a custom colormap to encode answers: yes=green, dunno=gray, no=red
    myColors = ((0.0, 1.0, 0.0, 1.0), (0.5, 0.5, 0.5, 1.0), (1.0, 0.0, 0.0, 1.0))
    cmap = LinearSegmentedColormap.from_list('Custom', myColors, len(myColors))

    g = sns.clustermap(a_f, xticklabels=statement_short_labels, yticklabels=party_names, cmap=cmap)
    g.fig.suptitle('Clustering von Parteien nach ihren Antworten auf Wahlomat-Fragen')
    #g.set_axis_labels(['x label', 'y label'])
    #g.set(xlabel='my x label', ylabel='my y label')
    #plt.tight_layout(False)
    plt.savefig("test.png", bbox_inches='tight')

    plt.show()

    #kmeans = KMeans(n_clusters=2, random_state=0).fit(answers)



def fix_answer_values(answers):
    """
    The answer values are encoded 0 for "yes", 1 for "no", and 2 for "no opinion. This makes no sense for clustering, as "no opinion" should be in the middle. So switch the values for "no" and no opinion."
    """
    answers_fixed = answers.copy()
    answers_fixed = np.where(answers_fixed==1, 3, answers_fixed)    # move "no" away temporarily
    answers_fixed = np.where(answers_fixed==2, 1, answers_fixed)    # set "no opinion" value to 1
    answers_fixed = np.where(answers_fixed==3, 2, answers_fixed)    # set temporary value 3 (meaning "no") to 2
    return answers_fixed



def export_data(df, file_name):
    df.to_csv(file_name, sep='\t', encoding='utf-8')
    print("Data exported to CSV file '%s'." % (file_name))


def load_data():
    """
    Load the data from the JSON files and return them in one merged data frame.
    """
    data_path = os.path.join('qual-o-mat-data', 'data', '2019', 'europa')
    data_keys = ["answer", "comment", "opinion", "party", "statement"]
    raw_data = dict()
    all_data = dict()

    # Create a dictionary of type <string, DataFrame> that contains the data from all JSON files
    for dk in data_keys:
        json_file = os.path.join(data_path, dk + ".json")
        with open(json_file, "r") as fh:
            raw_data[dk] = json.load(fh)
            all_data[dk] = pd.DataFrame(raw_data[dk])


    # Based on the opinion data, merge all other data frames on their ID fields to get usable names instead of just ID numbers
    merged_df = all_data["opinion"].copy()
    for to_merge in ["party", "statement", "comment", "answer"]:
        merged_df = merged_df.merge(all_data[to_merge], how='inner', left_on=[to_merge], right_on=['id'])

    #print(mdf.head())
    return merged_df, all_data, raw_data




if __name__ == "__main__":
    wahlomat_analysis()
