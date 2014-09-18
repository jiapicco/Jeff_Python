# -*- coding: utf-8 -*-

"""
This program will create a object for each person entered into the command line interface
and then save the objects to a file using the pickle module.  Thr information captured for each
person is:

    Name
    Address
    Home Phone Number
    Cell Phone Number
    Birthday

"""

import sys, pickle, person, re

"""
Just a short test of list comprehension
"""


a= [0, 2, 4, 6, 8, 9]
b = [0, 2, 3]
c = [[x, y, (x+2)**y] for x in a for y in b]
for d in (c):
    print (d)

#Create empty dictionary that will hold references to the person objects
people={}
#Count of people in the database
old_cnt = 0
#Check to see a db file already exist, is so input the objects from that file
file = ''
ans = input("Does a db file alread exist (y/n)?")
if ans == 'y' or ans == 'Y':
    while(True):
        file = input("Enter the file that holds the db:")
        try:
            INFILE = open(file, 'rb')
        #If file does not exist go to beginning of loop
        except (FileNotFoundError, IOError):
            print('Invalid file name.')
            continue
        #Catch any other exceptions
        except Exception as e:
            person.err(e)
        #First object in the file is the number of person objects in the file
        old_cnt = pickle.load(INFILE)
        for i in range(old_cnt):
            people[i] = pickle.load(INFILE) 
        INFILE.close()
        break

while(True):
    print("_______________________________________________________________________")
    print("Enter command:")
    print("\tEnter new person (enter)")
    print("\tSearch for a person (search)")
    print("\tSearch based on partial string (partial)")
    print("\tList all people (list)")
    print("\tPrint filtered list (filter)")
    print("\tPrint list filtered on partial string(pfilter)")
    print("\tSave the db file (save)")
    print("\tDelete recoord (delete)")
    print ("\tDefrag the list (defrag)")
    print("\tExit (exit)")
    print("_______________________________________________________________________")
    ans = input("Command: ")
    if ans == 'enter':
        old_cnt = person.enter(people)
        print ("Now", old_cnt, "records in the db.")
    elif ans == 'search':
        person.search(people)
    elif ans == 'partial':
        person.partial_search(people) 
    elif ans == 'list':
        for i in sorted(people.keys()):
            print("Record:", i)
            people[i].prt()
    elif ans == 'filter':
        person.filter_obj(people)
    elif ans == 'pfilter':
        person.partial_filter_obj(people)
    elif ans == 'save':
        if file == '':
            file=input("Enter name of file for saving DB: ")
        try:
            OUTFILE = open(file, 'wb')
        except Exception as e:
            person.err(e)
        cnt = len(people)
        #First object in the file is the number of person objects
        pickle.dump(cnt, OUTFILE)
        for i in (sorted(people.keys())):
            pickle.dump(people[i], OUTFILE)
        OUTFILE.close()
    elif ans == 'delete':
          person.delete(people)
    elif ans == 'defrag':
          person.defrag(people)
    elif ans == 'exit':
        ans1 = input("Do you want to save the db file before exiting (y/n)? ")
        if ans1 == 'y' or ans1 == 'Y':
            if file == '':
                file=input("Enter name of file for saving DB: ")
            try:
                OUTFILE = open(file, 'wb')
            except Exception as e:
                person.err(e)
            #First object in the file is the number of person objects
            cnt = len(people)
            pickle.dump(cnt, OUTFILE)
            for i in (sorted(people.keys())):
                pickle.dump(people[i], OUTFILE)
            OUTFILE.close()
        sys.exit()
    else:
        print("Invalid input!")

      









    







