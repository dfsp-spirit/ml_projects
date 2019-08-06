import os
import numpy as np
import brainload as bl
import brainload.freesurferdata as fsd
import brainload.braindescriptors as bd
import brainload.nitools
import logging

def run_desc():
    #subjects_list = ['subject1', 'subject2']
    #subjects_dir = os.path.join("tests", "test_data")

    subjects_dir = os.path.join(os.getenv("HOME"), "data", "abide", "structural")
    #subjects_dir = os.path.join("/Volumes", "shared-1", "projects", "abide", "structural")
    subjects_file = os.path.join(subjects_dir, 'subjects.txt')
    subjects_list = brainload.nitools.read_subjects_file(subjects_file)

    logging.basicConfig(level=logging.INFO)

    bdi = bd.BrainDescriptors(subjects_dir, subjects_list)
    bdi.add_parcellation_stats(['aparc', 'aparc.a2009s'])
    bdi.add_segmentation_stats(['aseg'])
    bdi.add_custom_measure_stats(['aparc', 'aparc.a2009s'], ['area', 'area.pial', 'curv', 'curv.pial', 'jacobian_white', 'sulc', 'thickness', 'truncation', 'volume'])

    #bdi.report_descriptors()

    bdi._check_for_duplicate_descriptor_names()
    data_output_file = "braindescriptors.csv"
    subjects_output_file="subjects.txt"
    bdi.save(data_output_file, subjects_file=subjects_output_file)
    logging.info("Saved values of %d descriptors for each of the %d subjects to file '%s'. Subject order for data written to file '%s'." % (len(bdi.descriptor_names), len(bdi.subjects_list), data_output_file, subjects_output_file))


if __name__ == "__main__":
  run_desc()
