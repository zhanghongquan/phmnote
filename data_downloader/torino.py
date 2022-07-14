import ftplib
import argparse
import os
from datetime import datetime
from urllib.parse import urlparse


'''
意大利-都灵理工大学轴承数据DIRG_BearingData
'''

class FileInfo:
    def __init__(self, name, **kwargs):
        self.name = name
        typ = kwargs["type"]
        self.is_folder = typ in ["cdir", "pdir", "dir"]
        self.is_normalfolder = typ == "dir"
        self.is_file = not self.is_folder
        self.mode = kwargs["unix.mode"]
        self.modify_time = datetime.strptime(kwargs["modify"], "%Y%m%d%H%M%S")
        if self.is_file and "size" in kwargs:
            self.size = int(kwargs["size"])
        else:
            self.size = 0
    
    def __repr__(self):
        return f"{self.name} {'D' if self.is_folder else 'F'} {self.size} {self.modify_time}"
        

class FtpClient:
    def __init__(self, **kwargs):
        self.recursive = kwargs.get("recursive", True)
        self.username = kwargs.get("username", '')
        self.password = kwargs.get("password", '')
        self.ftp = None
        self.path = []
    
    def enter_folder(self, name, server_only = False):
        self.path.append(name)
        self.ftp.cwd("/".join(self.path))
        if not server_only:
            try:
                os.mkdir(name)
            except FileExistsError:
                pass
            os.chdir(name)
        print(f"changed directory into {'/'.join(self.path)}")

    def leave_folder(self, server_only = False):
        if len(self.path) <= 0:
            raise RuntimeError("path is empty, there is no way to leave current folder")
        self.path.pop()
        self.ftp.cwd("/".join(self.path))
        if not server_only:
            os.chdir("..")
        print(f"changed directory into {'/'.join(self.path)}")

    def download(self, url, target):
        '''
        download content from url to target via ftp protocol
        '''
        url_info = urlparse(url)
        url = url_info.netloc
        folders = url_info.path.split("/")
        self.ftp = ftplib.FTP(url)
        self.ftp.login(self.username, self.password)
        print("logged in successfully")
        if folders:
            for folder in folders:
                self.enter_folder(folder, server_only=True)
        working_directory = os.getcwd()
        try:
            if target:
                try:
                    os.makedirs(target)
                except FileExistsError:
                    pass
                os.chdir(target)
            self._download_folder(None)
        finally:
            os.chdir(working_directory)
    
    def _list_current_folder(self):
        for (name, props) in self.ftp.mlsd():
            yield FileInfo(name, **props)
    
    def _download_folder(self, folder):
        try:
            if folder:
                self.enter_folder(folder)
            for info in self._list_current_folder():
                if info.is_normalfolder:
                    self._download_folder(info.name)
                elif info.is_file:
                    self._download_file(info.name, info.size)
        finally:
            if folder:
                self.leave_folder()

    def _download_file(self, name, size=0):
        if os.path.exists(name):
            info = os.stat(name)
            if info.st_size == size:
                print(f"file {name} has already been downloaded, skip downloading")
                return
        with open(name, "wb") as file:
            print(f"{datetime.now()} downloading file:{name} size:{size}")
            self.ftp.retrbinary(f"RETR {name}", file.write)


def main():
    client = FtpClient()
    client.download("ftp://ftp.polito.it/people/DIRG_BearingData/", "../data/torino/")

if __name__ == "__main__":
    main()
