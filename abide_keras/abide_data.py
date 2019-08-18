import logging
import pandas as pd
import os
import sys
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.compose import ColumnTransformer

def preproc_data(descriptors, metadata, labels):
    logging.info("Scaling data, creating training and test sets.")

    if descriptors.shape[0] != metadata.shape[0]:
        logging.error("Mismatch in size of descriptors and metadata: %d versus %d, but both should be for the same number of observations/subjects." % (descriptors.shape[0], metadata.shape[0]))

    if descriptors.shape[0] != labels.shape[0]:
        logging.error("Mismatch in size of descriptors and labels: %d versus %d, but both should be for the same number of observations/subjects." % (descriptors.shape[0], labels.shape[0]))

    numeric_features = list(descriptors.columns) # set to list of all column names from current dataframe

    numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', MinMaxScaler())])

    categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder())])

    ## Add covariates to descriptors. Some are numerical (which is fine), but some are categorical and need special encoding.

    ## Add numerical covariates to descriptors:
    numerical_covariates = ["AGE_AT_SCAN"]
    for cov in numerical_covariates:
        descriptors[cov] = metadata[cov]

    ## Add categorial covariates
    categorical_covariates = ["SEX", "SITE_ID"]
    for cov in categorical_covariates:
        descriptors[cov] = metadata[cov]
    categorical_features = categorical_covariates   # The only categorial features in the dataframe are the covariates we just added.

    features_to_be_removed = [] # No need to drop stuff so far. (Most important: the label is not part of the descriptors, as it comes from the metadata. So no need to remove the label.)

    preprocessor = ColumnTransformer(
    remainder = 'passthrough',
    transformers=[
        ('numeric', numeric_transformer, numeric_features),
        ('categorical', categorical_transformer, categorical_features),
        ('remove', 'drop', features_to_be_removed)
    ])

    # prepare data for classification task:
    X_train, X_test, y_train, y_test = train_test_split(descriptors, labels, test_size=.4, random_state=42)

    logging.debug("Received training data: descriptor shape is %s, and %d labels for it." % (str(X_train.shape), y_train.shape[0]))
    logging.debug("Received test data: descriptor shape is %s, and %d labels for it." % (str(X_test.shape), y_test.shape[0]))

    X_train = preprocessor.fit_transform(X_train)
    X_test = preprocessor.fit_transform(X_test)

    logging.debug("After pre-proc: Training data shape is %s, with %d labels for it." % (str(X_train.shape), y_train.shape[0]))
    logging.debug("After pre-proc: Test data shape is %s, with %d labels for it." % (str(X_test.shape), y_test.shape[0]))

    logging.info("Running dimensionality reduction (PCA).")
    pca = PCA()
    X_train = pca.fit_transform(X_train)
    X_test = pca.transform(X_test)

    for pc in range(10):
        logging.info("  PCA principal component #%d explained variance: %f" % (pc, pca.explained_variance_ratio_[pc]))

    logging.debug("After PCA: Training data shape is %s, with %d labels for it." % (str(X_train.shape), y_train.shape[0]))
    logging.debug("After PCA: Test data shape is %s, with %d labels for it." % (str(X_test.shape), y_test.shape[0]))

    return X_train, X_test, y_train, y_test



def check_data(data):
    """
    Check whether the number of descriptors in the training and test data is equal. If not, the one-hot-encoding of categorial features may have caused issues (i.e., some values occur only in the training data or only in the test data).
    """
    X_train, X_test, y_train, y_test = data
    num_features_train = X_train.shape[1]
    num_features_test = X_test.shape[1]
    if num_features_train != num_features_test:
        logging.error("Mismatch between descriptor count in training and test data: %d versus %d. There may be categorical columns which lack column values in one of the two sets." % (num_features_train, num_features_test))




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

    Returns
    -------
    descriptors: dataframe
        Dataframe containing descriptor data, one subject per row.

    metadata: dataframe
        Dataframe containing metadata, one subject per row.
    """
    logging.info("Reading brain descriptor data from file '%s', subject order from file '%s'." % (descriptors_file, subjects_file))

    descriptors = pd.read_csv(descriptors_file, header=0)
    logging.debug("Descriptor data shape: %s" % (str(descriptors.shape)))
    subjects = pd.read_csv(subjects_file, header=None, names=["subject_id"])
    logging.debug("Subject data shape: %s" % (str(subjects.shape)))

    #logging.debug("Descriptors:")
    #logging.debug(descriptors.head())

    #descriptors["subject_id"] = subjects["subject_id"]    # add subject IDs to descriptors dataframe
    logging.debug("Merged descriptor data shape (with subject ID field): %s" % (str(descriptors.shape)))

    logging.debug("Reading ABIDE metadata on subjects from file '%s'." % (metadata_file))
    metadata = pd.read_csv(metadata_file, header=0)
    logging.debug("Full metadata shape: %s" % (str(metadata.shape)))


    logging.debug("Descriptors:")
    logging.debug(descriptors.head())

    # Drop all columns (descriptors) for which ALL subjects have NaN values. These are completely useless.
    descriptors.dropna(axis='columns', how='all', inplace=True)

    # Filter metadata: keep only the data on our subjects
    filtered_metadata = pd.merge(subjects, metadata, how='left', left_on="subject_id", right_on="FILE_ID")
    logging.debug("Filtered metadata shape after removing subjects which we have no descriptor data on: %s" % (str(filtered_metadata.shape)))
    return descriptors, filtered_metadata
