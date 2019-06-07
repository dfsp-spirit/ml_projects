#!/usr/bin/env python
#
# This script downloads all ABIDE I structural neuroimaging data, preprocessed using the FreeSurfer pipeline.
#
# Written by Tim Schäfer, 2019-06-05


import os, sys
import pandas as pd
import urllib.request
import urllib.error
import shutil
import errno
# Download the file from `url` and save it locally under `file_name`:
from os.path import expanduser

def get_abide():
    #local_base_dir = "./abide_data/"
    local_base_dir = os.path.join(expanduser("~"), "data", "abide", "structural")
    #required_files_relative_to_subject_dir = ["surf/lh.white", "surf/rh.white", "surf/notthere"]
    required_files_relative_to_subject_dir = get_fs_subject_filenames()

    for file_idx, file in enumerate(required_files_relative_to_subject_dir):
        print("%d: %s" % (file_idx+1, file))

    diagnose_output("............................................ssssss......ssssss......ssssss......ssssss......ssssss......ssssss", required_files_relative_to_subject_dir)

    print("Downloading ABIDE I structural data to local directory '%s'." % (local_base_dir))
    print("Will download %d files per subject." % (len(required_files_relative_to_subject_dir)))

    download_abide_structural_files_to(local_base_dir, required_files_relative_to_subject_dir, skip_existing=True)


def get_fs_subject_filenames():
    """Generates the file paths of all important FreeSurfer files for a subject, relative to its subject dir."""
    files = []
    files = files + _get_both_hemi_files_in_dir("surf", ["white", "pial", "inflated", "orig", "smoothwm", "sphere", "sphere.reg", "jacobian_white", "thickness", "area", "curv", "volume", "sulc"])
    files = files + _get_both_hemi_files_in_dir("stats", ["aparc.stats", "aparc.a2009s.stats"])
    files = files + _get_files_in_subdir("stats", ["aseg.stats"])
    files = files + _get_files_in_subdir("mri", ["brain.mgz", "brainmask.mgz", "orig.mgz", "T1.mgz", "aseg.mgz"])
    files = files + _get_files_in_subdir("mri/transforms", ["talairach.m3z", "talairach.xfm"])
    files = files + _get_surf_both_hemi_fsaverge_mappings(["area", "area.pial", "sulc", "thickness", "curv", "volume"])
    return files

def diagnose_output(out_str, files):
    for idx, c in enumerate(out_str):
        if c != ".":
            print("%s: %s" % (c, files[idx]))

def _get_both_hemi_files_in_dir(subdir, file_list):
    files_lh = [("%s/lh.%s" % (subdir, f)) for f in file_list]
    files_rh = [("%s/rh.%s" % (subdir, f)) for f in file_list]
    return files_lh + files_rh

def _get_files_in_subdir(subdir, file_list):
    return [("%s/%s" % (subdir, f)) for f in file_list]


def _get_surf_both_hemi_fsaverge_mappings(file_name_parts_list, subdir="surf"):
    """
    Supply something like ["area", "volume"] to get a list of file names including ["lh.area.fwhm0.fsaverage.mgh", "lh.area.fwhm0.fsaverage.mgh", lh.area.fwhm5.fsaverage.mgh, ...]
    """
    fsaverage_parts = []
    files = []
    for smoothing in ["0", "5", "10", "15", "20", "25"]:
        files_lh = [("%s/lh.%s.fwhm%s.fsaverage.mgh" % (subdir, f, smoothing)) for f in file_name_parts_list]
        files_rh = [("%s/lh.%s.fwhm%s.fsaverage.mgh" % (subdir, f, smoothing)) for f in file_name_parts_list]
        files = files + files_lh + files_rh
    return files


def download_abide_structural_files_to(local_base_dir, required_files_relative_to_subject_dir, verbose=True, skip_existing=False):
    if not os.path.exists(local_base_dir):
        raise IOError("Local base directory '%s' does not exist, please create it first." % (local_base_dir))
    md = load_abide_metadata()
    file_ids = md['FILE_ID']

    #file_ids = pd.Series(["Pitt_0050003", "Pitt_0050004", "Pitt_0050005"])

    num_ids = len(file_ids)
    num_files_total = (num_ids * len(required_files_relative_to_subject_dir))
    if verbose:
        print("Received meta data on %d subjects. Will download %d * %d = %d files in total." % (num_ids, num_ids, len(required_files_relative_to_subject_dir), num_files_total))

    base_url = "https://s3.amazonaws.com/fcp-indi/data/Projects/ABIDE_Initiative/Outputs/freesurfer/5.1/"
    ok_files = []
    error_files = []
    error_full_urls = []
    error_messages = []
    skipped_files = []

    for idx, fid in file_ids.items():
        if fid == "no_filename":
            continue
        if idx % 10 == 0:
            print("At subject number %d of %d: encountered problems with %d of %d files so far, skipped %d." % (idx, num_ids, len(error_files), len(error_files) + len(ok_files), len(skipped_files)))
        if verbose:
            print("[%s]" % (fid), end="", flush=True)
        for fpath in required_files_relative_to_subject_dir:
            fpath = fid + "/" + fpath
            fparts = fpath.split("/")
            extra_dirs = []
            file_name = fparts[-1]
            if len(fparts) > 1:
                extra_dirs = fparts[0:-1]
            code, full_url, msg = download_file_to_local_dir(base_url, extra_dirs, file_name, local_base_dir, skip_existing=skip_existing)
            if code == 1:
                error_files.append(fpath)
                error_full_urls.append(full_url)
                error_messages.append(msg)
                if verbose:
                    print("E", end="", flush=True)
            elif code == -1:
                skipped_files.append(fpath)
                if verbose:
                    print("s", end="", flush=True)
            elif code == 0:
                ok_files.append(fpath)
                if verbose:
                    print(".", end="", flush=True)
            else:
                print("Unhandled return code received from download function, exiting.")
                sys.exit(1)

        if verbose:
            print("")
    if error_files:
        print("Encountered problems with %d of the %d files:" % (len(error_files), num_files_total))
        for idx, fname in enumerate(error_files):
            print("-error file %s : url '%s' : error '%s'" % (error_files[idx], error_full_urls[idx], error_messages[idx]))
    if skipped_files:
        print("Skipped %d of the %d files:" % (len(skipped_files), num_files_total))
        for idx, fname in enumerate(skipped_files):
            print("-skipped file %s" % (skipped_files[idx]))


def download_file_to_local_dir(base_url, extra_dirs, file_name, local_base_dir, skip_existing=False):
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

    if skip_existing and os.path.isfile(local_file):
        return -1, full_url, "skipped on user request: local file exists"

    try:
        with urllib.request.urlopen(full_url) as response, open(local_file, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
    except urllib.error.HTTPError as h_err:
        return 1, full_url, str(h_err.code)
    except urllib.error.URLError as u_err:
        return 1, full_url, str(u_err.reason)
    except Exception as e:
        if hasattr(e, 'message'):
            return 1, full_url, e.message
        return 1, full_url, str(e)

    return 0, full_url, ""


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
