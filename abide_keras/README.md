# ABIDE keras

Predict brain age from ABIDE data using keras deep neural networks on the GPU

# Installation (Python 3, GPU)

    python -m virtualenv env
    source env/bin/activate
    pip install tensorflow-gpu
    pip install keras
    pip install pandas
    pip install scikit-learn

# Data

See ../abide_brain_age_sklearn/README.md, *Data* section

# Predictions

    python abide_keras.py
