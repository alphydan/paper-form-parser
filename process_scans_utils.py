#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
functions used in the process_scans.py 
"""

__author__      = "Alvaro Feito + Eduardo Alonso Peleato"
__copyright__   = "Copyright 2019, Laniakea Supercluster"
__license__     = "GPLv3, www.gnu.org/licenses/gpl-3.0"
__email__       = "alvaro@baut.bm"
__status__      = "Production"
__date__        = "2019-11-19"


import csv
import cv2  # Import statement to import opencv-python
import numpy as np # for arrays used with opencv
from pyzbar import pyzbar
import ntpath
from shutil import copyfile


data_path = '/keybase/team/XXX.XXX/XXXXXXXX/'


def get_answers(path):
    """
    Parses answers (3) and returns them. If not found, the image is sent to review
    :param path: Path to the image of a form
    :return: list with the three options chosen by the student
    """
    im = cv2.imread(path)
    circles = get_circles(im)
    sorted_c = sort_circles(circles)

    if sorted_c[3]:  # the number of circles varies between the 3 columns
        print(ntpath.basename(path), ' invalid # of bubbles, sending to review')
        copyfile(path, './review/circles/' + ntpath.basename(path))
        return None
    else:
        a1 = get_answer(sorted_c[0], im)
        a2 = get_answer(sorted_c[1], im)
        a3 = get_answer(sorted_c[2], im)
        answers = [a1, a2, a3]
        if 0 in answers:
            print(ntpath.basename(path),
                  ' More than 1 answer selected, sending to review')
            copyfile(path, 'review/answers/' + \
                     ntpath.basename(path))
            return None


        draw_answers(data_path + 'output/' + ntpath.basename(path),
                     im, answers, sorted_c)
        print('output saved to' + data_path + 'output/' + ntpath.basename(path), '\n\n')
        return answers


def activities_for_class(student_class, activity_list):
    """
    :param student_class: class of the student
    :param activity_list: list of activities
    :return: list of activities available for the specified class
    """
    custom_list = []
    for activity in activity_list:
        if activity[1] and student_class not in activity[1]:
            continue

        custom_list.append(activity[0])
    return custom_list


def get_qr_pos(im, avg_x):
    """
    Gets the QR-code Y position based on an average X position
    :param im: Image
    :param avg_x: Average X position of the center of the QR-code
    :return: The upper Y position of the QR code
    """
    # At this point we don't really know where the QR-code is located at.
    # The average X coordinate of the center is ~500 so we'll use that to get the Y
    # Now let's go down until we find the square of the QR
    y_position = 0
    for i in range(100, 600):  # I don't think it can be found outside of this bounds
        if im[i, avg_x][0] < 128 and im[i, avg_x][1] < 128 and im[i, avg_x][2] < 128:
            y_position = i
            break

    return y_position - 20


def get_qr(img):
    """
    This function rotates and transforms the image using the QR-code as reference
    :param img: Path of the image to be corrected
    :return: The image in a corrected format
    """

    im = cv2.imread(img)

    y_positions = []  # We'll probe for some X values and get the one with the smallest Y
    avg_x = 450
    for i in range(400, 700, 50):
        y_positions.append(get_qr_pos(im, i))

    y_pos = min(y_positions)
    qr_img = im[y_pos:y_pos + 500, avg_x - int(avg_x / 2): avg_x * 2]

    # Prepare image for the reader
    qr_img = 255 - cv2.cvtColor(cv2.inRange(qr_img, (0, 0, 0), (200, 200, 200)), cv2.COLOR_GRAY2BGR)
    barcodes = pyzbar.decode(qr_img)

    if len(barcodes) != 1:
        return

    return barcodes[0]


def get_name(img):
    '''
    input: string with path and image holding QR-code
    output: string with decoded QR-code: name of student
    '''
    #im = cv2.imread(img)
    # Coordinates calculated from the example paper
    #qrImg = im[170:170 + 400, 360:360 + 360]
    #qrImg = im[150:150 + 500, 350:350 + 380]

    # Black & white image + invert so that the library gets the qr right
    #qrImg = 255 - cv2.cvtColor(cv2.inRange(qrImg,(0,0,0),(200,200,200)),cv2.COLOR_GRAY2BGR)
    #barcodes = pyzbar.decode(qrImg)

    barcode = get_qr(img)

    if barcode is None:
        return '0'
    else:
        ## check for encoding problems, which are found with ä, ë
        try:
            stu_name = barcode.data.decode("ascii")
            return stu_name
        except UnicodeDecodeError: # if 'ascii' encoding fails, try this instead:
            try:
                stu_name = barcode.data.decode("iso-8859-1")#.encode("sjis") # a bit hackish
                #stu_name = stu_name.decode("iso-8859-1")
                return stu_name
            except UnicodeDecodeError: # it can actually fail
                return '0'
            

def get_student_list(data_path):
    '''
    opens list of students and stores a list
    with names, year and form class
    '''
    list_file = data_path + 'students2.csv'
    list_of_students = []
    with open(list_file, 'r', encoding='utf-8') as studentfile:
        reader = csv.reader(studentfile)
        # next(reader) no header in this file
        for stu in reader:
            name = stu[0]
            year_of_student = stu[1][:-4] # remove the teacher 4 letters from the end
            form_class = stu[1]
            list_of_students.append([name,
                                     year_of_student,
                                     form_class])

    return list_of_students


def get_circles(image):
    '''
    https://www.pyimagesearch.com/2014/07/21/detecting-circles-images-using-opencv-hough-circles/
    https://www.learnopencv.com/hough-transform-with-opencv-c-python/
    for more on the Hough transform
    ``in``: is an image object already opened by cv2 previously (full size)
    ``out``: numpy array of circles (x, y, r)

    '''
    crop = _crop_answers(image)
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    ### THIS IS JUST DIAGNOSTIC TO SEE DOUBLE CROPPING
    cv2.imwrite('_image_for_circles.jpg', gray)
    ### END OF DIAGNOSTIC IMAGE PRINTING
    
    circles = cv2.HoughCircles(gray, # input grayscale image
              cv2.HOUGH_GRADIENT, # algo - only 1 option
              0.5, # inverse ratio of resolution
              minDist=79, # centers of circles at least 79px appart
              param1=100, param2=30,
              minRadius=20, # Minimum radius to be detected. If unknown, put zero as default.
              maxRadius=30) # Maximum radius to be detected. If unknown, put zero as default.

    return circles


def sort_circles(circles):
    '''
    ``input``: circles is a numpy array with all the circles in the image
    ``output``: a list with the [Left, Middle, Right] arrays of circles
    '''
    # convert pixel coordinates to integers
    circles = np.round(circles[0, :]).astype("int")

    # let's organize the circles in columns
    # axis = 0 means by rows
    # index of the min values of all circles independently:
    min_circle_values = np.argmin(circles, axis = 0) 
    # index the max coordinate of all circles independently
    max_circle_values = np.argmax(circles, axis = 0) 

    # find coordinates of extremes
    top_circle_y = circles[min_circle_values[1]][1]  # first index: y-coord max value, 2nd index, y-coord chosen circle
    bottom_circle_y = circles[max_circle_values[1]][1]
    left_most_circle_x = circles[min_circle_values[0]][0]
    right_most_circle_x = circles[max_circle_values[0]][0]

    top_3_circles = list(filter(lambda x: x[1] <= (top_circle_y + 40), circles))
    bottom_3_circles = list(filter(lambda x: x[1] >= (bottom_circle_y - 40), circles))


    top_L_circle = [x  for x in top_3_circles if
                    x[0] <= left_most_circle_x + 65][0]
    bottom_L_circle = [x  for x in bottom_3_circles if
                       x[0] <= left_most_circle_x + 50][0]

    L_column = circles[ ((left_most_circle_x - 50) < circles[:,0]) &
                        (circles[:,0] < (left_most_circle_x + 50)) ]
    sorted_L_column = L_column[L_column[:,1].argsort()]

    R_column = circles[ ((right_most_circle_x - 50) < circles[:,0]) &
                        (circles[:,0] < (right_most_circle_x + 50)) ]
    sorted_R_column = R_column[R_column[:,1].argsort()]

    # middle column has x-values larger than largest x-value in sorted_L_column
    # middle column has x-values smaller than the smallest x-value in sorted_R_column
    max_L_column_x = np.max(sorted_L_column, axis = 0)[0] # sorted_L_column[0][0]
    min_R_column_x = np.min(sorted_R_column, axis = 0)[0] # sorted_R_column[len(sorted_R_column)-1][0]

    Mid_column = circles[((max_L_column_x + 5) < circles[:,0]) &
                         (circles[:,0] < (min_R_column_x -5))]
    sorted_M_column = Mid_column[Mid_column[:,1].argsort()]

    # Check if all columns have the same number of circles
    nr_circles = set([len(sorted_L_column), len(sorted_M_column), len(sorted_R_column)])
    # print(nr_circles, len(nr_circles))
    if len(nr_circles) > 1:
        error_code = 1 # there is an error
    else:
        error_code = 0 # no problem

        
    return [sorted_L_column, sorted_M_column, sorted_R_column, error_code]
    
    
def _crop_answers(im):
    '''
    crops the opencv image object to keep just the bubble
    sheet answers
    `in`: opencv image object
    '''
    to_crop = im.copy()
    height, width, channels = to_crop.shape 
    over_half_width = int(width/2+width/10)
    quarter_height = int(height/4)
    right_margin = int(width/7)

    cropped_answers = to_crop[quarter_height: height, over_half_width:(width-right_margin)]
    return cropped_answers

def _high_contrast_answers(im):
    '''
    `in` opencv image object of answers already cropped
    to only the bubble sheet answers
    `out` high contrast opencv image object
    with background black, and writing / lines in white
    '''
    gray_crop = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray_crop, 220, 255, cv2.THRESH_BINARY)
    black_thresh = cv2.bitwise_not(thresh)
    return black_thresh



def get_answer(sorted_column, img):
    '''
    `in`: - sorted circles column
          - opencv image object which is cropped and
    transformed into Black & White, high contrast, inverted
    (background black, writing and circles in white)
    `out`: index of answer selected (starting at 1)
          - if two or more answers were selected in a column
            then number "0" is returned as a sign of failure
    '''
    output = img.copy()
    out_crop = _crop_answers(output)
    black_thresh = _high_contrast_answers(out_crop)
    
    filling = []
    for i, circ in enumerate(sorted_column):
        r = circ[2]*1.2 # look slightly outside the circle
        circle_crop = black_thresh[int(circ[1]-r):int(circ[1]+r), 
                          int(circ[0]-r):int(circ[0]+r)]

        count = cv2.countNonZero(circle_crop) # count non-black pixels
        filling.append(count)

    # What is the maximum value of filled circle?
    max_fill = max(filling)
    # Are there others with similar coloring? (withing 80%)
    all_max = list(filter(lambda y : y > max_fill*0.85, filling))
    # this would find their index:
    all_max_index = [filling.index(i) for i in all_max]
    if len(all_max) > 1:
        print('more than one selected')
        return 0
    elif len(all_max) == 1:
        return all_max_index[0]+1 #+1 corrects for start counting at 1.


#########################################
# Helper Functions to Visualize results #
#########################################


def draw_answers(img_file_name, img, answers, s_circles):
    '''
    for quality control, save a copy
    of the cropped answers with a bright
    circle indicating the answers found
    `in`: - opencv image object (then cropped)
          - answers: list with:
            * index of answer 1
            * index of answer 2
            * index of answer 3
          - sorted circles (to find coordinates)
    '''
    
    output = img.copy()
    output = _crop_answers(output)
    for i, a in enumerate(answers):
        x = s_circles[i][a-1][0]
        y = s_circles[i][a-1][1]
        r = s_circles[i][a-1][2]
        if a == 0: # draw a cross if it's an invalid answer
            x = s_circles[i][a][0]
            y = s_circles[i][a][1]
            r = s_circles[i][a][2]
            cv2.line(output, (x-r, y-r-80), (x+r, y+r-80), (0,180, 255), 10 )
            cv2.line(output, (x+r, y-r-80), (x-r, y+r-80), (0,180, 255), 10 )
        else: # draw a rectangle on the chosen answer
            cv2.rectangle(output, (x-r, y-r), (x+r, y+r), (0,180, 255), 6 )
    
    cv2.imwrite(img_file_name, output)




def draw_sorted_circles(img, s_circles):
    # ensure at least some circles were found
    if s_circles is not None:
        output = img.copy()
        output = _crop_answers(output)
        # convert the (x, y) coordinates and radius of the circles to integers
        r_circles = s_circles[2] # np.round(s_circles[2][0, :]).astype("int")
        l_circles = s_circles[0]
        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in r_circles:
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            cv2.circle(output, (x, y), r, (0, 255, 0), 2)
            cv2.rectangle(output, (x - 2, y - 2), (x + 2, y + 2), (0, 128, 255), -1)
        for (x,y,r) in l_circles:
            cv2.circle(output, (x, y), r, (0, 255, 0), 2)
            cv2.rectangle(output, (x - 2, y - 2), (x + 2, y + 2), (0, 128, 255), -1)
            
        cv2.imwrite('sorted_circles.jpg', output)


def draw_circles(img, circles):
    # ensure at least some circles were found
    if circles is not None:
        output = img.copy()
        output = _crop_answers(output)
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in circles:
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            cv2.circle(output, (x, y), r, (0, 255, 0), 2)
            cv2.rectangle(output, (x - 2, y - 2), (x + 2, y + 2), (0, 128, 255), -1)
        cv2.imwrite('_circles.jpg', output)



##########################
# TESTING SCRIPT         #
##########################



# img = 'scans/0176.jpg'
# img = 'scans/0006.jpg'

# img = 'scans/0219.jpg'
# im = cv2.imread(img)
# crop = _crop_answers(im)
# circles = get_circles(im)
# draw_circles(im, circles)
# hc = _high_contrast_answers(crop)
# cv2.imwrite('_high_contrast.jpg', hc)
# sorted_circles = sort_circles(circles)
# a1 = get_answer(sorted_circles[0], im)
# print (a1)

# crop2 = _crop_answers(crop)
# cv2.imwrite('_cropped.jpg', crop)


# print(circles, len(circles))
# print(sorted_circles)

# draw_sorted_circles(im, sorted_circles)

# a2 = get_answer(sorted_circles[1], im)
# a3 = get_answer(sorted_circles[2], im)

# answers=[a1, a2, a3]
# print(answers)
# draw_answers('answers.jpg', crop, answers, sorted_circles)

        
