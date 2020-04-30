import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch,cm
from reportlab.platypus import Image, Paragraph
from reportlab.lib.utils import ImageReader

import qrcode


with open('students2.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    student_list = []
    for row in readCSV:
        student_list.append([row[0], row[1]])

        
with open('activities2.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    next(readCSV)
    activity_list = []
    for row in readCSV:
        activity_list.append(row)


#############################        
# Generate Personalized Form 
############################# 
        
from reportlab.pdfgen import canvas

# parameters
width, height = letter
top_margin = 1*inch
left_margin = 0.8*inch # 1.2*inch
right_margin = 0.68*inch
bottom_margin = 0.45*inch

# Instantiate the Document
c = canvas.Canvas("Enrichment_forms.pdf", pagesize=letter)
c.setAuthor("Alvaro Feito Boirac")


def add_header(student, c):
    c.drawImage('bhs_CMYK.tif', width-2.5*inch, height - 0.99 * inch, 178/1.8,60/1.8)
    c.setFont("Helvetica", 28)
    c.drawString(width/2-4*cm, height-2*inch, "Enrichment Activity - "  + student[1])
    c.setFont("Helvetica", 26)
    c.drawString(width/2-3*cm, height-2.4*inch, "Sign-up Sheet")


def add_identity(student, c):
    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(student[0] + "--" + student[1] )
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("qr.png")

    logo = ImageReader('qr.png')

    c.drawImage(logo, 1*inch, height-1.7*inch, 100, 100, mask='auto')
    c.setFont("Helvetica", 18)
    c.drawString(2.5*inch, height-1.15*inch, student[0])


def add_activities(student, activity_list, c):
    c.setFont("Helvetica", 12)
    delta = 0.5 * inch
    spacing = 0.3*inch
    starting_pos = height-3.5*inch
    counter = 0
    c.drawString(left_margin + 4.95 * inch, starting_pos + 0.2*inch - counter*spacing, '1')
    c.drawString(left_margin + 4.95 * inch + delta, starting_pos + 0.2*inch - counter*spacing, '2')
    c.drawString(left_margin + 4.95 * inch + 2 * delta, starting_pos + 0.2*inch - counter*spacing, '3')
             
    c.setFont("Helvetica", 14)
    c.drawString(left_margin, starting_pos + 1.5*spacing, 'Select your 1st, 2nd and 3rd choices from the list')           
    c.setFont("Helvetica", 12)
    
    year_of_student = student[1][:-4] # remove the teacher 4 letters from the end
    for acti in activity_list:
        if not acti[1]:
            c.drawString(left_margin, starting_pos - counter*spacing, acti[0])
            c.circle(left_margin + 5 * inch, starting_pos - counter*spacing, 6, stroke=1, fill=0)
            c.circle(left_margin + 5 * inch + delta, starting_pos - counter*spacing, 6, stroke=1, fill=0)
            c.circle(left_margin + 5 * inch + 2 * delta, starting_pos - counter*spacing, 6, stroke=1, fill=0)
            counter +=1
        elif year_of_student in acti[1]:
            c.drawString(left_margin, starting_pos - counter*spacing, acti[0])
            c.circle(left_margin + 5 * inch, starting_pos - counter*spacing, 6, stroke=1, fill=0)
            c.circle(left_margin + 5 * inch + delta, starting_pos - counter*spacing, 6, stroke=1, fill=0)
            c.circle(left_margin + 5 * inch + 2 * delta, starting_pos - counter*spacing, 6, stroke=1, fill=0)
            counter +=1
        else:
            pass

for i, student in enumerate(student_list):
    if i < 350:
        add_header(student, c)
        add_identity(student,c)    
        add_activities(student, activity_list, c)
        c.showPage()

c.save()



#############################        
#    Generate Generic Form 
#############################


from reportlab.pdfgen import canvas

# parameters
width, height = letter
top_margin = 1*inch
left_margin = 0.8*inch # 1.2*inch
right_margin = 0.68*inch
bottom_margin = 0.45*inch

# Instantiate the Document
c = canvas.Canvas("Blank_enrichment_forms.pdf", pagesize=letter)
c.setAuthor("Alvaro Feito Boirac")



def add_header(student, c):
    c.drawImage('bhs_CMYK.tif', width-2.5*inch, height - 0.99 * inch, 178/1.8,60/1.8)
    c.setFont("Helvetica", 28)
    c.drawString(width/2-4*cm, height-2*inch, "Enrichment Activity")
    c.setFont("Helvetica", 26)
    c.drawString(width/2-3*cm, height-2.4*inch, "Sign-up Sheet")


def add_blank_identity(student, c):
    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data('0')
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("qrb.png")

    logo = ImageReader('qrb.png')

    c.drawImage(logo, 1*inch, height-1.7*inch, 100, 100, mask='auto')
    c.setFont("Helvetica", 18)
    c.drawString(2.5*inch, height-0.8*inch, student[0])
    c.drawString(2.5*inch, height-1.2*inch, "Form: ______________")


def add_activities(student, activity_list, c):
    c.setFont("Helvetica", 12)
    delta = 0.5 * inch
    spacing = 0.28*inch
    starting_pos = height-3.5*inch
    counter = 0
    c.drawString(left_margin + 4.95 * inch, starting_pos + 0.2*inch - counter*spacing, '1')
    c.drawString(left_margin + 4.95 * inch + delta, starting_pos + 0.2*inch - counter*spacing, '2')
    c.drawString(left_margin + 4.95 * inch + 2 * delta, starting_pos + 0.2*inch - counter*spacing, '3')
             
    c.setFont("Helvetica", 14)
    c.drawString(left_margin, starting_pos + 1.6*spacing, 'Select your 1st, 2nd and 3rd choices from the list')           
    c.setFont("Helvetica", 11)
    counter = 0
    for acti in activity_list:
        if acti[1]:
            open_to = ' ---- only for years ' + acti[1]
        else:
            open_to = ''
        c.drawString(left_margin, starting_pos - counter*spacing, acti[0] + open_to)
        c.circle(left_margin + 5 * inch, starting_pos - counter*spacing, 6, stroke=1, fill=0)
        c.circle(left_margin + 5 * inch + delta, starting_pos - counter*spacing, 6, stroke=1, fill=0)
        c.circle(left_margin + 5 * inch + 2 * delta, starting_pos - counter*spacing, 6, stroke=1, fill=0)
        counter +=1
        

student=['Name:_____________']
add_header(student, c)
add_blank_identity(student,c)    
add_activities(student, activity_list, c)
c.showPage()

c.save()
