#!/usr/bin/python
import sys, string, random, re

"""
This script will generate files composed of random words. The number of characters in the files is set by the
first argumentm to the script. The number of files is set by the second argument to the script. The third argument
provides the directory in which the files will be created.
"""

#Function to provide the usage information for the script
def usage():
    print('Usage: make_messages.py number-files file-size attachment-directory')
    exit()

"""
Main routine
"""
def main():
    #get the words from /usr/share/dict/words and put tem into a list WORDS
    word_file = "/usr/share/dict/words"
    WORDS = open(word_file).read().splitlines()
    #check for correct number of arguments
    if len(sys.argv) < 4:
        usage()
    #check that number of files is an integer
    try:
        numfiles = int(sys.argv[1])
    except Exception as e:
        usage()
    #check that size of files is an integrer
    try:
        filesize = int(sys.argv[2])
    except Exception as e:
        usage()
    i = 0
    dir = sys.argv[3]
    while(i < numfiles):
        #the name of the file is attachment followed by four random characters .txt
        name = dir+'/attachment'+random.choice(string.letters)+random.choice(string.letters)+random.choice(string.letters)+random.choice(string.letters)+random.choice(string.letters)+'.txt'
        try:
            file = open(name, 'w')
        except Exception as e:
            print('Could not open file %s: %s' % (file, e))
            exit()
        j = 0
        k = 0
        line = ''
        while(j < filesize):
            word = random.choice(WORDS)
            line = line+word+' '
            j += len(word)+1
            #Every 10 words add a new line
            k += 1
            if k == 10:
                line = line + '\n'
                file.write(line)
                line = ''
                k = 0
                j += 1
        line += '\n'
        file.write(line)
        file.close()
        i += 1
    
if __name__ == '__main__':
    main()


