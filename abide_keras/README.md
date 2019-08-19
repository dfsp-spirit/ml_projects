# ABIDE keras

Predict brain age from ABIDE data using keras deep neural networks on the GPU

# Installation (Python 3, CPU)

    python -m virtualenv keras_cpu
    source keras_cpu/bin/activate
    pip install tensorflow
    pip install keras
    pip install pandas scikit-learn seaborn matplotlib brainload

# Data

See ../abide_brain_age_sklearn/README.md, *Data* section

# Predictions

    python abide_keras.py
