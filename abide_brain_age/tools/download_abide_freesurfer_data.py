#!/usr/bin/env python
#
# This script download the ABIDE structural neuroimaging data, preprocessed using the FreeSurfer pipeline

import pandas as pd


def download_abide_structural():
    md = load_abide_metadata()
    file_ids = md['FILE_ID']

    base_url = "https://s3.amazonaws.com/fcp-indi/data/Projects/ABIDE_Initiative/Outputs/freesurfer/5.1"
    for idx, fid in file_ids.items():
        #print("file at %d is '%s'" % (idx, fid))
        for fpath in ["surf/lh.white", "surf/rh.white"]:
            file_url = "%s/%s/%s" % (base_url, fid, fpath)
            print("Downloading file: %s" % (file_url))



def load_abide_metadata():
    metadata_csv_file = "Phenotypic_V1_0b_preprocessed1.csv"
    df = pd.read_csv(metadata_csv_file)
    return df





if __name__ == "__main__":
    download_abide_structural()
