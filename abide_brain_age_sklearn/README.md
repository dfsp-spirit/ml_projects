# ABIDE brain age

Predict brain age from ABIDE data using scikit-learn models

# Installation (Python 3)

    python -m virtualenv env
    source env/bin/activate
    pip install numpy scikit-learn brainload pandas

# Data

Run the scripts in tools/ to get ABIDE I structural MRI data. Then:

    python gen_braindescriptors.py

# Predictions

    python predict_abide_brainage.py

    
