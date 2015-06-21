import re, sys, os, operator, stat

def CheckFile(file, name):
    result = 0
    try:
        mode = os.stat(file).st_mode
    except Exception as e:
        err(e, "Failure during stat(1): ")
        return(result)
    if stat.S_ISREG(mode):
        print(file, name)
        if re.search(name, file):
            OUT.write(file+"\n")
            print(file)
            result = 1
        return(result)
    if stat.S_ISDIR(mode):
        try:
            file_list = os.listdir(file)
        #If an exception occurs log it and return
        except Exception as e:
            err(e, "Failure opeing dir: ")
            return(result)
        for f in file_list:
            #Create full path to the file
            if(not re.search("\\\\$", file)):
                file2=file+'\\'+f
            else:
                file2 = file+f
            try:
                mode = os.stat(file2).st_mode
                #If this is a regular file, see if it matches the search
                #criteria
                if stat.S_ISREG(mode):
                    if re.search(name, file2):
                        OUT.write(file2+"\n")
                        print(file2)
                #If this is a directory, recursively call CheckFile on it
                if stat.S_ISDIR(mode):
                    CheckFile(file2, name)
            #If an exception occure, log it and then continue the FOR loop
            except Exception as e:
                err(e, "Failure during stat(2): ")
        return(result)


def err(e, *txt):
    for s in txt:
        LOG.write(s)
    LOG.write("Error {0}".format(str(e)))
    LOG.write("\n")
    return()
    

#Open files to record any eceptions and the files that match the search criteria
LOG = open('c:\\Python Source\\fail.log', 'w')
OUT = open('c:\\Python Source\\found.log', 'w')

#First argument holds the starting directory and second arguments holds regular
#exporession to be searched for
if(sys.argv[1] == '.'):
    dir = os.getcwd()
else:
    dir = sys.argv[1]
CheckFile(dir, sys.argv[2])
sys.exit()
