import os, sys
import numpy as np
import logging
from keras.models import Sequential
from keras.layers import Dense
from abide_data import preproc_data, load_data

def run_nn():

    logging.basicConfig(level=logging.DEBUG)

    ################ Specify data files and load data ####################

    data_path = os.path.join("..", "abide_brain_age_sklearn")
    descriptors_file = os.path.join(data_path, "braindescriptors.csv")
    subjects_file = os.path.join(data_path, "subjects.txt")
    metadata_file = os.path.join(data_path, "tools", "Phenotypic_V1_0b_preprocessed1.csv")

    logging.info("Loading data.")
    descriptors, metadata = load_data(descriptors_file, subjects_file, metadata_file)

    labels = metadata["DX_GROUP"]
    X_train, X_test, y_train, y_test = preproc_data(descriptors, metadata, labels)
    data = (X_train, X_test, y_train, y_test)
    input_dim = X_train.shape[1]

    model = Sequential()
    model.add(Dense(units=64, activation='relu', input_dim=input_dim))
    model.add(Dense(units=10, activation='softmax'))
    model.compile(loss='sparse_categorical_crossentropy',
                  optimizer='sgd',
                  metrics=['accuracy'])

    model.fit(X_train, y_train, epochs=5, batch_size=32)
    loss_and_metrics = model.evaluate(X_test, y_test, batch_size=128)
    print(model.metrics_names)

    print("Predicting classes.")
    classes = model.predict(X_test, batch_size=128)


if __name__ == "__main__":
    run_nn()
