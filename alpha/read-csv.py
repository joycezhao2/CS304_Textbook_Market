#!/usr/local/bin/python3.6

import sys, csv

if __name__ == '__main__':
    fname = sys.argv[1]
    deptAndNumber = []

    with open(fname, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            course_info = row[1]
            info = course_info.split(' ')
            department = info[0]
            number = info[1]
            deptAndNumber.append([department, number])

    with open('courses.csv', 'w') as courses:
        writer = csv.writer(courses, delimiter=',')
        for course in deptAndNumber: 
            writer.writerow(course)

    
    


            
        
