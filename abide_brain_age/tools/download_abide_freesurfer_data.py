#!/usr/bin/env python
#
# This script downloads all ABIDE I structural neuroimaging data, preprocessed using the FreeSurfer pipeline.
#
# Written by Tim Schäfer, 2019-06-05


import os
import pandas as pd
import urllib.request
import shutil
import errno
# Download the file from `url` and save it locally under `file_name`:


def get_abide():
    local_base_dir = "./abide_data/"
    required_files_relative_to_subject_dir = ["surf/lh.white", "surf/rh.white"]

    print("Downloading ABIDE I structural data to local directory '%s'." % (local_base_dir))
    print("Will download %d files per subject." % (len(required_files_relative_to_subject_dir)))

    download_abide_structural_files_to(local_base_dir, required_files_relative_to_subject_dir)


def download_abide_structural_files_to(local_base_dir, required_files_relative_to_subject_dir):
    if not os.path.exists(local_base_dir):
        raise IOError("Local base directory '%s' does not exist, please create it first." % (local_base_dir))
    md = load_abide_metadata()
    file_ids = md['FILE_ID']

    num_ids = len(file_ids)
    print("Received meta data on %d subjects. Will download %d * %d = %d files in total." % (num_ids, num_ids, len(required_files_relative_to_subject_dir), (num_ids * len(required_files_relative_to_subject_dir))))

    base_url = "https://s3.amazonaws.com/fcp-indi/data/Projects/ABIDE_Initiative/Outputs/freesurfer/5.1/"

    for idx, fid in file_ids.items():
        if fid == "no_filename":
            continue
        for fpath in required_files_relative_to_subject_dir:
            fpath = fid + "/" + fpath
            fparts = fpath.split("/")
            extra_dirs = []
            file_name = fparts[-1]
            if len(fparts) > 1:
                extra_dirs = fparts[0:-1]
            download_file_to_local_dir(base_url, extra_dirs, file_name, local_base_dir)
            print(".", end="", flush=True)


def download_file_to_local_dir(base_url, extra_dirs, file_name, local_base_dir):
    """
    Download a remote file from a base url to a local folder, and create the equivalent directory structure in a local base dir.

    E.g., * If you download <base_url>/file.txt, it will go to <local_base_dir>/file.txt.
          * If you download <base_url>/blah/file2.txt, it will go to <local_base_dir>/blah/file2.txt.
    """
    if not os.path.exists(local_base_dir):
        raise IOError("Local base directory '%s' does not exist, cannot download file '%s' into it." % (local_base_dir, file_name))
    full_url = base_url + "/".join(extra_dirs) + "/" + file_name
    local_dir = os.path.join(local_base_dir, os.path.join(*extra_dirs))
    mkdir_p(local_dir)
    local_file = os.path.join(local_dir, file_name)
    with urllib.request.urlopen(full_url) as response, open(local_file, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)


def load_abide_metadata():
    metadata_csv_file = "Phenotypic_V1_0b_preprocessed1.csv"
    df = pd.read_csv(metadata_csv_file)
    return df


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


if __name__ == "__main__":
    get_abide()
