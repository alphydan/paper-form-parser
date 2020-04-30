#!/usr/bin/env python

"""img_processing_utils.py contains useful functions used by process_scans.py
See ipython notebook 'Activities-Survey.ipynb' and 'form_parsin.ipynb' for more 
documentation and visual explanations
"""

__author__      = "Alvaro Feito + Eduardo Alonso Peleato"
__copyright__   = "Copyright 2019, Laniakea Supercluster"
__license__     = "GPLv3, www.gnu.org/licenses/gpl-3.0"
__email__       = "alvaro@baut.bm"
__status__      = "Production"
__date__        = "2019-11-19"


import csv
import glob
from shutil import copyfile
import ntpath
import os
import pandas as pd
from fuzzywuzzy import fuzz

from process_scans_utils import data_path, get_name, \
    get_student_list, get_answers, activities_for_class

# For the ones that could not be detected
if not os.path.exists('review'):
    os.mkdir('review')


student_list = get_student_list(data_path)

activity_list = []
with open(data_path + 'activities2.csv') as file:
    readCSV = csv.reader(file, delimiter=',')
    next(readCSV)
    for row in readCSV:
        activity_list.append(row)


image_dir = data_path + 'scans/*.jpg'
csv_content = []
for path_n_image in glob.iglob(image_dir):
    scan_number = ntpath.basename(path_n_image)
    # extract the student name from the 
    # QR Code in the picture
    student_name = get_name(path_n_image)
    # if student_name = '0' send to review folder
    if student_name == '0':
        print(scan_number, ' invalid student name, sending to review')
        copyfile(path_n_image, './review/qr/' + scan_number)
        continue

    student_answers = get_answers(path_n_image)

    if student_answers is None:
        continue

    # let's check if the name is in the list and has a year and class:
    stu_name = student_name.split('--')[0]  # Jane Something 9A--9Smit -> Jane Something 9A
    student_details = list(filter(lambda x: fuzz.ratio(stu_name, x[0]) >= 80, student_list))
    if student_details:
        text = activities_for_class(student_details[0][1], activity_list)
        csv_content.append([    scan_number, # picture scan number | for diagnostics
                                student_details[0][0], # name
                                student_details[0][1], # year (just a number: 7, 8, 9, 10, 11)
                                student_details[0][2], # form (number+4letters teacher)
                                text[student_answers[0] - 1].strip(),
                                text[student_answers[1] - 1].strip(),
                                text[student_answers[2] - 1].strip()])
    else:
        stu_name = student_name.split('--')[0] # Jane Something 9A--9Smit -> Jane Something 9A
        csv_content.append([scan_number, student_name, None, None, None, None, None])

    print()

# Sort the records
df = pd.DataFrame(csv_content, columns=['Scan#', 'Name', 'Year', 'Class', 'First option', 'Second option', 'Third option'])
df = df.sort_values('Class')

with open(data_path + 'student_choices.csv', 'a') as csvfile:
    output_writer = csv.writer(csvfile)

    for choices in df.values.tolist():
        output_writer.writerow(choices)
