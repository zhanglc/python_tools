# -*- coding: utf-8 -*-

from __future__ import print_function
from ftplib import FTP
import os, os.path, time, sys
from datetime import datetime
from multiprocessing import Pool
import csv


server_files = []
local_files = []
download_files = []
download_path = None


def remove_all(remove, list):
    return filter(lambda a: a != remove, list)


def get_server_file(line):
    temp = {}
    info = remove_all('', line.split(' '))
    global server_files
    server_files.append(buildObj(info[3], datetime.strptime(" ".join(info[0:2]), '%m-%d-%y %I:%M%p'), int(info[2])))
    print(".", end="")


def init_local_file():
    global local_files
    for name in os.listdir(download_path):
        date = datetime.fromtimestamp(os.path.getmtime(os.path.join(download_path, name)))
        size = os.path.getsize(os.path.join(download_path, name))
        local_files.append(buildObj(name, date, size))


def buildObj(name, date, size):
    temp = {}
    temp["date"] = date
    temp["size"] = size
    temp["name"] = name
    return temp;


def init_server_file():
    print("get file file name for server", end="")
    ftp = FTP('ftp.ingrammicro.com.au')
    ftp.login('IMGuest_ftpscript', 'FtPIM4fiLE')
    ftp.retrlines('LIST', get_server_file)
    ftp.quit()


def findDownloadFile():
    global local_files, server_files, download_files

    for srv in server_files:
        find = False
        for loc in local_files:
            if (loc["name"] == srv["name"]):
                find = True
                if (loc["size"] == srv["size"] ):
                    if (loc["date"].now() < srv["date"].now()):
                        download_files.apped(srv["name"])
                        break
                else:
                    download_files.append(srv["name"])
                    break
        if (not find):
            download_files.append(srv["name"])

    local_files = None
    server_files = None

def needDownload(file_obj,download_path):
    name = file_obj["name"]
    if not os.path.exists("%s%s"%(download_path, name)):
        return True
    else:
        date = datetime.fromtimestamp(os.path.getmtime(os.path.join(download_path, name)))
        size = os.path.getsize(os.path.join(download_path, name))
        if (file_obj["size"] != size):
            return True
        else:
            if (date > file_obj["date"]):
                return False
            else:
                return True


def downloadSingle(file_object, download_path):
    # name,download_path = name_download_path
    name = file_object["name"]
    try:
        ftp = FTP('ftp.ingrammicro.com.au')
        ftp.login('IMGuest_ftpscript', 'FtPIM4fiLE')
        with open("%s%s" % (download_path, name), 'wb') as f:
            ftp.retrbinary('RETR %s' % name,
                           f.write)
            f.close()
        ftp.quit()
        print("%s is downloaded." % name)
        return name, "success"
    except Exception:
        return name, "fail"



def wrapf(t):
    if (needDownload(*t)):
        return downloadSingle(*t)


def downloadAll():
    print("Downloading....")
    global server_files, download_path
    pool = Pool(2)
    res = pool.map(wrapf, [(x, download_path) for x in server_files])
    with open(download_path+"result.log.csv","wb") as f:
        resWR = csv.writer(f,delimiter=',')
        for row in res:
            resWR.writerow(row)
        f.close()
    print("Done!")


def main():
    global download_path

    script, download_path = sys.argv
    if (not download_path.endswith("/")):
        download_path = download_path + "/"
    print("download path:" + download_path)
    init_server_file()
    downloadAll()


if __name__ == '__main__':
    main()


