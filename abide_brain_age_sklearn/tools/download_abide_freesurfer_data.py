#!/usr/bin/env python
#
# This script downloads all ABIDE I structural neuroimaging data, preprocessed using the FreeSurfer pipeline.
#
# This is a parallel implementation. Sequential takes ages.
#
# Written by Tim Schäfer, 2019-06-05


import os, sys
import pandas as pd
import urllib.request
import urllib.error
import shutil
import errno
import argparse
from multiprocessing.dummy import Pool
from urllib.request import urlretrieve
from os.path import expanduser

def get_abide():
    parser = argparse.ArgumentParser(description="Download ABIDE structural data, preprocessed with FreeSurfer pipeline.")
    parser.add_argument("target_dir", help="The target download directory. This dir will contain all the subject directories. You may want to create a new, empty dir for this.")
    parser.add_argument("-n", "--num-files-parallel", help="How many files to download in parallel. Defaults to 10.", default="10")
    parser.add_argument("-r", "--re-download", help="Whether to re-download existing files. Defaults to FALSE if omitted, which means that existing files will be kept.", action="store_true")
    parser.add_argument("-v", "--verbose", help="Whether to print more detailed information while downloading. Defaults to false if omitted.", action="store_true")
    args = parser.parse_args()

    num_in_parallel = int(args.num_files_parallel)
    skip_existing = not args.re_download

    local_base_dir = args.target_dir
    required_files_relative_to_subject_dir = get_fs_subject_filenames()

    print("Downloading ABIDE I structural data to local directory '%s'." % (local_base_dir), flush=True)
    print("Will download %d files in parallel. skip_existing is set to %s." % (num_in_parallel, str(skip_existing)), flush=True)
    print("Will download %d files per subject:" % (len(required_files_relative_to_subject_dir)), flush=True)

    if args.verbose:
        for file_idx, file in enumerate(required_files_relative_to_subject_dir):
            print("    %d: %s" % (file_idx+1, file))



    download_abide_structural_files_to(local_base_dir, required_files_relative_to_subject_dir, skip_existing=skip_existing, verbose=args.verbose, num_in_parallel=num_in_parallel)


def get_fs_subject_filenames():
    """Generates the file paths of all important FreeSurfer files for a subject, relative to its subject dir."""
    files = []
    files = files + _get_both_hemi_files_in_dir("surf", ["white", "pial", "inflated", "orig", "smoothwm", "sphere", "sphere.reg"])      # surfaces
    files = files + _get_both_hemi_files_in_dir("surf", ["jacobian_white", "thickness", "area", "area.pial", "curv", "curv.pial", "volume", "sulc"])        # surface morphometry data (native space)
    files = files + _get_surf_both_hemi_fsaverge_mappings(["area", "area.pial", "sulc", "thickness", "curv", "volume"])     # surface morphometry data mapped to standard space (fsaverage surface)
    files = files + _get_both_hemi_files_in_dir("stats", ["aparc.stats", "aparc.a2009s.stats"])     # atlas stats. Note: "aparc.DKTatlas.stats" is not available for ABIDE
    files = files + _get_files_in_subdir("stats", ["aseg.stats"])   # segmenatation stats, not hemi dependent
    files = files + _get_both_hemi_files_in_dir("label", ["aparc.annot", "aparc.a2009s.annot", "cortex.label"])     # brain surface parcellations for standard atlases and other labels
    files = files + _get_files_in_subdir("mri", ["brain.mgz", "brainmask.mgz", "orig.mgz", "T1.mgz", "aseg.mgz", "wm.mgz"])   # volumes
    files = files + _get_files_in_subdir("mri/transforms", ["talairach.m3z", "talairach.xfm"])  # transformation matrices to convert between different spaces
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


def _get_surf_both_hemi_fsaverge_mappings(file_name_parts_list, subdir="surf", smoothings=["0", "5", "10", "15", "20", "25"]):
    """
    Supply something like ["area", "volume"] to get a list of file names including ["lh.area.fwhm0.fsaverage.mgh", "lh.area.fwhm0.fsaverage.mgh", lh.area.fwhm5.fsaverage.mgh, ...]
    """
    fsaverage_parts = []
    files = []
    for smoothing in smoothings:
        files_lh = [("%s/lh.%s.fwhm%s.fsaverage.mgh" % (subdir, f, smoothing)) for f in file_name_parts_list]
        files_rh = [("%s/lh.%s.fwhm%s.fsaverage.mgh" % (subdir, f, smoothing)) for f in file_name_parts_list]
        files = files + files_lh + files_rh
    return files


def download_abide_structural_files_to(local_base_dir, required_files_relative_to_subject_dir, verbose=True, skip_existing=False, num_in_parallel = 8):
    if not os.path.exists(local_base_dir):
        raise IOError("Local base directory '%s' does not exist, please create it first." % (local_base_dir))
    md = load_abide_metadata()
    file_ids = md['FILE_ID']

    #file_ids = pd.Series(["Pitt_0050003", "Pitt_0050004", "Pitt_0050005"])

    num_ids = len(file_ids)
    num_files_total_max = (num_ids * len(required_files_relative_to_subject_dir))
    if verbose:
        print("Received meta data on %d subjects. May download up to %d * %d = %d files in total (if all requested files are available for all subjects)." % (num_ids, num_ids, len(required_files_relative_to_subject_dir), num_files_total_max))

    base_url = "https://s3.amazonaws.com/fcp-indi/data/Projects/ABIDE_Initiative/Outputs/freesurfer/5.1/"
    ok_files = dict()
    error_files = dict()
    skipped_files = dict()

    url_tuples = list()

    num_no_filename_files = 0

    for idx, fid in file_ids.items():
        if fid == "no_filename":
            num_no_filename_files = num_no_filename_files + len(required_files_relative_to_subject_dir)
            continue
        else:
            for fpath in required_files_relative_to_subject_dir:
                fpath = fid + "/" + fpath
                fparts = fpath.split("/")
                extra_dirs = []
                file_name = fparts[-1]
                if len(fparts) > 1:
                    extra_dirs = fparts[0:-1]
                url_tuple = (base_url, extra_dirs, file_name, local_base_dir, skip_existing, ok_files, error_files, skipped_files, verbose)
                url_tuples.append(url_tuple)

        if verbose:
            print("")

    num_files_total = len(url_tuples)
    print("Downloading %d files in parallel using %d threads." % (num_files_total, num_in_parallel))
    print("----- Download Start -----")

    Pool(num_in_parallel).map(retrieve_url, url_tuples)

    print("----- Download End -----")

    print("Legend for download status codes (first letter of the lines above, if any): K=download okay, S=skipped, E=download error")
    print("Download finished: handled %s URLs in total (%d in parallel). Result: %d downloaded, %d existed, %d failed, %d no_filename." % (num_files_total, num_in_parallel, len(ok_files.keys()), len(skipped_files.keys()), len(error_files.keys()), num_no_filename_files))
    print("Check local directory '%s' for downloaded files. Exiting." % (local_base_dir))


def retrieve_url(arg_tuple):
    """
    The actual downloader.
    """
    base_url, extra_dirs, file_name, local_base_dir, skip_existing, ok_files, error_files, skipped_files, verbose = arg_tuple
    code, full_url, msg = download_file_to_local_dir(base_url, extra_dirs, file_name, local_base_dir, skip_existing=skip_existing)

    if code == 1:
        error_files[full_url] = msg
        print("E: %s" % (full_url), flush=True)
    elif code == -1:
        skipped_files[full_url] = msg
        if verbose:
            print("S: %s" % (full_url), flush=True)
    elif code == 0:
        ok_files[full_url] = msg
        if verbose:
            print("K: %s" % (full_url), flush=True)
    else:
        error_files[full_url] = "Unhandled exception: '%s'" % (msg)
        print("EE: %s" % (full_url), flush=True)

    if verbose:
        num_so_far = len(ok_files) + len(error_files) + len(skipped_files)
        if num_so_far % 1000 == 0:
            print("# %d" % (num_so_far))


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
