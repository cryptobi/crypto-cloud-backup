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

# list your files and directories here
filenames = [
    "/some/directory/",
    "/my/secrets/wallet.dat",
    "/etc/shadow",
]

# list your databases here
databases = [
    "local_db1",
    "local_db2",
]

dbuser = "dbuser"
dbpass = "dbpass"
dbhost = "localhost"
secsalt = "randomsecuresaltstringmakeitlong234923823804020393323"
odname = "/path/to/backups"  # directory where to store the encrypted backups for upload
mfname = odname + "/" + "mf"  # manifest filename
openssl = "/usr/bin/openssl"  # encryption command
tar = "/bin/tar"  # archive command path
mysqld = "/usr/bin/mysqldump"  # mysql dump program path
bkt = "mybucket"  # cloud bucket name
kpth = "my/backups"  # cloud backup path within bucket
backup_prefix = "skdkcms93"  # any short random alphanumeric string
max_upload_size = 50  # maximum upload file size in MB





