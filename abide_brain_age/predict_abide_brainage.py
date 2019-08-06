import os
import numpy as np
import pandas as pd
import logging


def predict_abide_brain_age():

    logging.basicConfig(level=logging.INFO)

    descriptors_file = "braindescriptors.csv"
    subjects_file = "subjects.txt"
    metadata_file = os.path.join("tools", "Phenotypic_V1_0b_preprocessed1.csv")

    descriptors, metadata = load_data(descriptors_file, subjects_file, metadata_file)

    logging.info("Done, exiting.")


def load_data(descriptors_file, subjects_file, metadata_file):

    logging.info("Reading brain descriptor data from file '%s', subject order from file '%s'." % (descriptors_file, subjects_file))

    descriptors = pd.read_csv(descriptors_file, header=0)
    logging.info("Descriptors have shape: %s" % (str(descriptors.shape)))
    subjects = pd.read_csv(subjects_file, header=None)
    logging.info("Subjects have shape: %s" % (str(subjects.shape)))

    # merge subject IDs and descriptor data here
    df_descriptors = ...


    logging.info("Reading ABIDE metadata on subjects from file '%s'." % (metadata_file))
    metadata = pd.read_csv(metadata_file, header=1)
    logging.info("Metadata has shape: %s" % (str(metadata.shape)))
    group = metadata.iloc[:, 7]

    # TODO: keep only the metadata lines which are of interest for the subjects we have in subjects list
    df_metadata = ...
    return df_descriptors, df_metadata






if __name__ == "__main__":
  predict_abide_brain_age()
