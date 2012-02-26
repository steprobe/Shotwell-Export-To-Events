#!/usr/bin/python

import shutil
import sqlite3
import os
import sys
import getopt
from subprocess import Popen, PIPE
from hashlib import sha1

input_db=None
dest=None
rotate=False

def show_usage():
    print '''
Usage:''', sys.argv[0], '''
    -i      Input Shotwell Database (required)
    -d      Destination to copy events (required)
    -r      Rotate source photo's in place. Off by default. Requires 
            exiftran to be installed. Will slow down process.
    -h      Show this help
'''

def parse_args():
    global input_db
    global dest
    global rotate

    input_db_set=False
    dest_set=False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:d:rh")
    except getopt.GetoptError, err:
        show_usage()
        sys.exit(10)

    for o,a in opts:
        if o == "-i":
            input_db_set = True
            input_db = a
        elif o == "-d":
            dest_set = True
            dest = a
        elif o == "-h":
            show_usage()
            exit(0)
        elif o == "-r":
            rotate = True

    if not input_db_set or not dest_set:
        show_usage()
        exit(10)

def shafile(filename):
    try:
        with open(filename, "rb") as f:
            return sha1(f.read()).hexdigest()
    except IOError:
        return 0

def main():

    parse_args()

    print "Going to output to", dest
    print "Going to Read database from", input_db
    print "Rotation of source photos? ", rotate

    conn = sqlite3.connect(input_db)
    crs = conn.cursor()
    crs.execute('select id, name from EventTable')
    for row in crs:
        if row[1] != None:

            print "======================"
            print "Dealing with Event", row[1]

            event_dir = dest + os.sep + row[1].replace(os.sep, "_") #in case of seps in the string
            if not os.path.exists(event_dir):
                print "Creating", event_dir
                os.makedirs(event_dir)

            photo_crs = conn.cursor()
            photo_crs.execute('select filename from PhotoTable where event_id=?', (row[0],))
            copy_cnt = 0
            exist_cnt = 0
            for photo in photo_crs:

                if rotate:
                    Popen(("exiftran", "-a", "-i", "-p", photo[0]), stdout=PIPE, stderr=PIPE).communicate()

                filename = event_dir + os.sep + os.path.basename(photo[0])

                destsha = shafile(filename)
                sourcesha = shafile(photo[0])
                if destsha != sourcesha:
                    sys.stdout.write('.')
                    sys.stdout.flush()

                    shutil.copyfile(photo[0], filename)
                    copy_cnt = copy_cnt + 1
                else:
                    sys.stdout.write('e')
                    sys.stdout.flush()
                    exist_cnt = exist_cnt + 1

            print '\nCopied', copy_cnt, 'files. (Ignored', exist_cnt,'files as they already existed)'

    #Finally, delete empty dirs to tidy up (caused by old events in DB)
    for name in os.listdir(sys.argv[1]):
        if os.path.isdir(name) and len(os.listdir(name)) == 0:
            os.remove(name)

if __name__ == "__main__":
    main()
