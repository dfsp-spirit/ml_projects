
import os
import numpy as np
import pandas as pd
import logging
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
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
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score


def predict_abide_brain_age():

    logging.basicConfig(level=logging.DEBUG)

    ################ Specify data files and load data ####################

    descriptors_file = "braindescriptors.csv"
    subjects_file = "subjects.txt"
    metadata_file = os.path.join("tools", "Phenotypic_V1_0b_preprocessed1.csv")

    logging.info("Loading data.")
    descriptors, metadata = load_data(descriptors_file, subjects_file, metadata_file)

    labels = metadata["DX_GROUP"]
    X_train, X_test, y_train, y_test = preproc_data(descriptors, metadata, labels)
    data = (X_train, X_test, y_train, y_test)
    check_data(data)
    compare_classifiers(data)


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


def compare_classifiers(data):
    """
    Quick comparison of different classifiers with hard-coded parameters (no parameter optimization). This is only useful to get a very rough first impression of the performance of the different classifiers.
    """
    X_train, X_test, y_train, y_test = data

    # Test a number of classifiers
    classifier_names = ["KNN", "Linear SVM", "RBF SVM", "Gaussian Process",
         "Decision Tree", "Random Forest", "Neural Net", "AdaBoost",
         "Naive Bayes", "QDA"]

    logging.info("Preparing %d different classifiers." % (len(classifier_names)))

    classifiers = [
    KNeighborsClassifier(3),
    SVC(kernel="linear", C=0.025),
    SVC(gamma=2, C=1),
    GaussianProcessClassifier(1.0 * RBF(1.0)),
    DecisionTreeClassifier(max_depth=5),
    RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
    MLPClassifier(alpha=1, max_iter=2000),
    AdaBoostClassifier(),
    GaussianNB(),
    QuadraticDiscriminantAnalysis()]

    for name, clf in zip(classifier_names, classifiers):
        logging.info("Fitting classifier '%s' to training set." % (name))
        clf.fit(X_train, y_train)

        kfold = 3
        logging.info("  Performing %d fold cross validation" % (kfold))
        cv_scores = cross_val_score(clf, X_train, y_train, cv=kfold, scoring="accuracy")
        logging.info("  Cross validation scores:")
        for k in range(kfold):
            logging.info("    %f" % (cv_scores[k]))

        logging.info("  Evaluating classifier '%s' on test set." % (name))
        score = clf.score(X_test, y_test)
        logging.info("  Classifier %s achieved score: %f" % (name, score))
        logging.info("  Predicting using %s for some observations from test set (true labels are: %d %d %d %d %d):" % (name, y_test.iloc[0], y_test.iloc[1], y_test.iloc[2], y_test.iloc[3], y_test.iloc[4]))
        pred = clf.predict([X_test[0,:], X_test[1,:], X_test[2,:], X_test[3,:], X_test[4,:]])
        logging.info("    %d %d %d %d %d" % (pred[0], pred[1], pred[2], pred[3], pred[4]))



    logging.info("Classifier comparison done.")



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




if __name__ == "__main__":
  predict_abide_brain_age()
