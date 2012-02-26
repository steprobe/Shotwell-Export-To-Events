#!/usr/bin/python

import shutil
import sqlite3
import os
import sys
from subprocess import Popen, PIPE

def show_usage():
    print sys.argv[0], "[destination] [location_ofshotwell_db.db]"

def main():

    if len(sys.argv) != 3:
        show_usage()
        exit(10)

    print "Going to output to", sys.argv[1]
    print "Going to Read database from", sys.argv[2]

    dest = sys.argv[1]

    conn = sqlite3.connect(sys.argv[2])
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
                filename = event_dir + os.sep + os.path.basename(photo[0])
                if not os.path.exists(filename):
                    sys.stdout.write('.')
                    sys.stdout.flush()
    
                    Popen(("exiftran", "-a", "-i", "-p", photo[0]), stdout=PIPE, stderr=PIPE).communicate()

                    shutil.copyfile(photo[0], filename)
                    copy_cnt = copy_cnt + 1
                else:
                    sys.stdout.write('e')
                    sys.stdout.flush()
                    exist_cnt = exist_cnt + 1
                    

            print '\nCopied', copy_cnt, 'files. (Ignored', exist_cnt,'files as they already existed)'

if __name__ == "__main__":
    main()
