#!/usr/bin/env python
# Retrieve the subjects which were part of the matched diMartino study from the list.
#
# This is for python3, btw.

import pandas as pd
import logging

def get_dm_subjects(metadata_file):
    full_df = pd.read_csv(metadata_file, header=0)
    logging.debug("Full metadata shape: %s" % (str(full_df.shape)))
    required_subjects_df = full_df.loc[full_df['SUB_IN_SMP'] == 1]
    required_subjects_with_files_df = required_subjects_df.loc[required_subjects_df['FILE_ID'] != "no_filename"]
    required_subject_dirnames = required_subjects_with_files_df['FILE_ID']
    rd = pd.DataFrame(required_subject_dirnames)
    rd.to_csv('subjects_diMarino.csv', index=False, header=False)
    print("Checking %d subjects total." % (full_df.shape[0]))
    print("Found %d subjects from diMartino study, %d of them had a structural data dir." % (required_subjects_df.shape[0], required_subjects_with_files_df.shape[0]))
    print("Subjects file 'subjects_diMartino.csv' written.")


if __name__ == "__main__":
    metadata_file = 'Phenotypic_V1_0b_preprocessed1.csv'
    get_dm_subjects(metadata_file)
