import os
import numpy as np
import pandas as pd
import logging
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler

def predict_abide_brain_age():

    logging.basicConfig(level=logging.DEBUG)
    #logging.basicConfig(level=logging.INFO)

    ################ Specify data files and load data ####################

    descriptors_file = "braindescriptors.csv"
    subjects_file = "subjects.txt"
    metadata_file = os.path.join("tools", "Phenotypic_V1_0b_preprocessed1.csv")

    logging.info("Loading data.")
    descriptors, metadata = load_data(descriptors_file, subjects_file, metadata_file)


    ################# Prepare data ####################

    logging.info("Scaling data, creating training and test sets.")



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

    features_to_be_removed = [] # No need to drop stuff so far.

    preprocessor = ColumnTransformer(
    remainder = 'passthrough',
    transformers=[
        ('numeric', numeric_transformer, numeric_features),
        ('categorical', categorical_transformer, categorical_features),
        ('remove', 'drop', features_to_be_removed)
    ])

    # prepare data for classification task:
    labels = metadata["DX_GROUP"]
    X_train, X_test, y_train, y_test = train_test_split(descriptors, labels, test_size=.4, random_state=42)

    logging.info("Received training data: descriptor shape is %s, and %d labels for it." % (str(X_train.shape), y_train.shape[0]))
    logging.info("Received test data: descriptor shape is %s, and %d labels for it." % (str(X_test.shape), y_test.shape[0]))

    X_train = preprocessor.fit_transform(X_train)
    X_test = preprocessor.fit_transform(X_test)

    logging.info("After pre-proc: Received training data: descriptor shape is %s, and %d labels for it." % (str(X_train.shape), y_train.shape[0]))
    logging.info("After pre-proc: Received test data: descriptor shape is %s, and %d labels for it." % (str(X_test.shape), y_test.shape[0]))

    num_features_train = X_train.shape[1]
    num_features_test = X_test.shape[1]
    if num_features_train != num_features_test:
        logging.error("Mismatch between descriptor count in training and test data: %d versus %d. There may be categorical columns which lack column values in one of the two sets." % (num_features_train, num_features_test))

    ################ Start Classification ###################

    logging.info("Preparing classifiers.")
    # Test a number of classifiers
    names = ["Linear SVM", "RBF SVM", "Gaussian Process",
         "Decision Tree", "Random Forest", "Neural Net", "AdaBoost",
         "Naive Bayes", "QDA"]

    classifiers = [
    #KNeighborsClassifier(3),
    SVC(kernel="linear", C=0.025),
    SVC(gamma=2, C=1),
    GaussianProcessClassifier(1.0 * RBF(1.0)),
    DecisionTreeClassifier(max_depth=5),
    RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
    MLPClassifier(alpha=1, max_iter=1000),
    AdaBoostClassifier(),
    GaussianNB(),
    QuadraticDiscriminantAnalysis()]

    for name, clf in zip(names, classifiers):
        logging.info("Fitting classifier '%s' to training set." % (name))
        clf.fit(X_train, y_train)
        logging.info("Evaluating classifier '%s' on test set." % (name))
        score = clf.score(X_test, y_test)
        logging.info("Classifier %s achieved score: %f" % (name, score))



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






if __name__ == "__main__":
  predict_abide_brain_age()
