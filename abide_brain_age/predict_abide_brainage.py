import os
import numpy as np
import pandas as pd
import logging


def predict_abide_brain_age():

    logging.basicConfig(level=logging.DEBUG)
    #logging.basicConfig(level=logging.INFO)

    descriptors_file = "braindescriptors.csv"
    subjects_file = "subjects.txt"
    metadata_file = os.path.join("tools", "Phenotypic_V1_0b_preprocessed1.csv")

    descriptors, metadata = load_data(descriptors_file, subjects_file, metadata_file)
    logging.info("Data loaded.")

    logging.info("Done, exiting.")


def load_data(descriptors_file, subjects_file, metadata_file):
    """
    Load data and merge it.

    Parameters
    ----------
    descriptors_file: str
        Path to a file containing brain descriptor values in CSV format. Each line should contain data on a single subject, and can have an arbitrary number of columns (descriptor values). All lines must have identical length, though. Must have a header line.

    subject_file: str
        Path to subjects text file, each line contains a single subject ID, no header.

    metadata_file: str
        Path to metadata CSV file from ABIDE data. The required file is named 'Phenotypic_V1_0b_preprocessed1.csv' when downloaded from ABIDE.
    """
    logging.info("Reading brain descriptor data from file '%s', subject order from file '%s'." % (descriptors_file, subjects_file))

    descriptors = pd.read_csv(descriptors_file, header=0)
    logging.info("Descriptor data shape: %s" % (str(descriptors.shape)))
    subjects = pd.read_csv(subjects_file, header=None, names=["subject_id"])
    logging.info("Subject data shape: %s" % (str(subjects.shape)))

    #logging.debug("Descriptors:")
    #logging.debug(descriptors.head())

    descriptors["subject_id"] = subjects["subject_id"]    # add subject IDs to descriptors dataframe
    logging.info("Merged descriptor data shape: %s" % (str(descriptors.shape)))


    logging.info("Reading ABIDE metadata on subjects from file '%s'." % (metadata_file))
    metadata = pd.read_csv(metadata_file, header=0)
    logging.info("Full metadata shape: %s" % (str(metadata.shape)))

    # Filter metadata: keep only the data on our subjects
    filtered_metadata = pd.merge(subjects, metadata, how='left', left_on="subject_id", right_on="FILE_ID")
    logging.info("Filtered metadata shape after removing subjects which we have no descriptor data on: %s" % (str(filtered_metadata.shape)))
    return descriptors, filtered_metadata






if __name__ == "__main__":
  predict_abide_brain_age()
