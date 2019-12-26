#!/usr/bin/python3

"""

/*
 *
 * Crypto.BI Toolbox
 * https://Crypto.BI/
 *
 * Author: José Fonseca (https://zefonseca.com/)
 *
 * Distributed under the MIT software license, see the accompanying
 * file COPYING or http://www.opensource.org/licenses/mit-license.php.
 *
 */

"""

import os
import sys
from getpass import getpass
import zkln
import dt
import datetime

# --------------- CONFIG -------------------------

dbuser = dt.dbuser
dbpass = dt.dbpass
dbhost = dt.dbhost
secsalt = dt.secsalt
odname = dt.odname
mfname = dt.mfname
openssl = dt.openssl
tar = dt.tar
mysqld = dt.mysqld
filenames = dt.filenames
databases = dt.databases


# --------------- MAIN PROGRAM -------------------------

# check if all files/dirs exist
for filename in filenames:
    if not os.path.exists(filename):
        print("{} DOES NOT EXIST OR IS NOT REGULAR FILE/DIR. FIX FILE/DIR LIST AND TRY AGAIN.".format(filename))
        sys.exit(1)

print("All paths checked OK. Proceeding.")

start_time = datetime.datetime.now()

pwd = getpass("Archive password:")
pwd2 = getpass("Repeat password:")

if pwd != pwd2:
    print("Passwords do not match. Will not proceed.")
    sys.exit(1)

# will not upload files larger than max_size MB
max_size = dt.max_upload_size

if len(sys.argv) >= 2:
    max_size = int(sys.argv[1])

zkln.cleartree(odname)
zkln.write_manifest(filenames, databases, mfname, secsalt)
xfname = odname + "/" + zkln.make_remote_filename("mf", secsalt)
zkln.encr_fil(mfname, pwd, openssl, xfname)
os.unlink(mfname)

for filename in filenames:
    if os.path.isfile(filename):
        zkln.process_file(filename, pwd, odname, secsalt, openssl)
    elif os.path.isdir(filename):
        zkln.process_dir(filename, pwd, odname, tar, secsalt, openssl)
    else:
        print("IGNORED unknown file type for %s" % filename)

for db in databases:
    zkln.process_db(dbuser, dbpass, dbhost, db, secsalt, mysqld, odname, openssl)

size = zkln.du(odname)
print("TOTAL {} SIZE {}".format(odname, size))

zkln.sendall(dt.odname, dt.bkt, dt.kpth, max_size)

end_time = datetime.datetime.now()

print("STARTED {} ENDED {}".format(start_time, end_time))
