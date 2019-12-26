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

import hashlib
import os, shutil
from subprocess import call
import boto3
import subprocess
import datetime
import dt


def du(path):
    """disk usage in human readable format (e.g. '2,1GB')"""
    return subprocess.check_output(['du', '-sh', path]).split()[0].decode('utf-8')


def encr_fil(filname, pwd, openssl, ofpath):
    """Encrypt a file using openssl."""
    call([openssl, "aes-256-cbc", "-a", "-salt", "-in", filname, "-out", ofpath, "-pass", "pass:"+pwd])


def hashname(name, secsalt):
    """Obtain a sha256 hash from a name."""
    m = hashlib.sha256()
    m.update((name + secsalt).encode("utf-8"))
    return m.hexdigest()


def make_remote_filename(filename, secsalt):
    "Build the remote filename for upload."
    return "{}-{}".format(dt.backup_prefix, hashname(filename, secsalt))


def process_dir(filename, pwd, odname, tar, secsalt, openssl):
    """Process all files in a directory."""
    hash = make_remote_filename(filename,secsalt)
    print("{} PROCESSING DIR {} -> {}".format(datetime.datetime.now(), filename, hash))
    xfname  = odname + "/" + hash
    xfname2 = xfname + ".t"
    fe = open("/dev/null", "wb")

    call([tar, "cjf", xfname2, filename], stderr=fe)

    fe.close()
    encr_fil(xfname2, pwd, openssl, xfname)
    siz = du(xfname)
    print("{} DIR {} {} SIZE {}".format(datetime.datetime.now(), filename, xfname, siz))
    os.unlink(xfname2)


def process_file(filename, pwd, odname, secsalt, openssl):
    hash = make_remote_filename(filename, secsalt)
    print("{} PROCESSING FILE {} -> {}".format(datetime.datetime.now(), filename, hash))
    xfname = odname + "/" + hash
    encr_fil(filename, pwd, openssl, xfname)
    siz = du(xfname)
    print("{} FILE {} {} SIZE {}".format(datetime.datetime.now(), filename, xfname, siz))


def process_db(user,pwd,host,filename, secsalt,mysqld,odname,openssl):
    hash = make_remote_filename(filename, secsalt)
    print("{} PROCESSING DB {} -> {}".format(datetime.datetime.now(), filename, hash))
    print("db {0}".format(filename))
    xfname  = odname + "/" + hash
    xfname2 = xfname + ".t"
    fx = open(xfname2, "wb")
    fe = open("/dev/null", "wb")
    call([mysqld, "-u", user, "-p"+pwd, filename], stdout=fx, stderr=fe)
    fe.close()
    fx.close()
    encr_fil(xfname2, pwd, openssl, xfname)
    siz = du(xfname)
    print("{} DB {} {} SIZE {}".format(datetime.datetime.now(), filename, xfname, siz))
    os.unlink(xfname2)


def cleartree(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)


def write_manifest(fils, databases, mfname, secsalt):
    str = ""

    for fn in fils:
        hash = make_remote_filename(fn, secsalt)
        str += "file:" + fn + ":" + hash + "\n"

    for db in databases:
        hash = make_remote_filename(db, secsalt)
        str += "db:" + db + ":" + hash + "\n"

    with open(mfname, "w") as f:
        f.write(str)


def sort_smaller_files(lst):
    pairs = []
    for file in lst:
        # Get size and add to list of tuples.
        size = os.path.getsize(file)
        pairs.append((size, file))

    pairs.sort(key=lambda s: s[0])
    return map(lambda x: x[1], pairs)


def __upload_file_callback(bts):
    siz = bts / 1024
    print(" {} KB ".format(siz), end='')


def sendall(dirname, bkt, pth, max_size):
    s3 = boto3.resource('s3')
    lst = map(lambda f: os.path.join(dirname, f), os.listdir(dirname))
    slst = sort_smaller_files(lst)
    tot_sz = du(dirname)
    sent_sz = 0

    for the_file in slst:
        knam = "{}/{}".format(pth, os.path.basename(the_file))
        sz = du(the_file)
        bsz = os.path.getsize(the_file)
        bszmb = bsz / (1024 * 1024)    # size in MB

        if (bszmb > max_size):
            print("{} IGNORING FILE TOO BIG {} SIZE {}".format(datetime.datetime.now(), knam, sz))
            continue

        print("{} SENDING {}  SIZE {}".format(datetime.datetime.now(), knam, sz))
        s3.Object(bkt, knam).upload_file(the_file, None,  __upload_file_callback, None)
        sent_sz += bsz
        sent_kb = sent_sz / 1024
        print("{} DONE {} SIZE {}".format(datetime.datetime.now(), knam, sz))
        print("{} {} OF {} DONE".format(datetime.datetime.now(), sent_kb, tot_sz))



