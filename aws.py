# -*- coding: utf-8 -*-

"""TODO document"""

import subprocess

from suite import Tool

_READ_TIMEOUT = 300

class AWS(Tool):
    """TODO document"""

    def __init__(self, bucket: str):
        self.__bucket_uri = 's3://' + bucket

    def name(self):
        return "iRODS S3 API over AWS CLI"

    def download(self, path):
        self.__cp(self.__mk_path_uri(path), path)

    def upload(self, path):
        self.__cp(path, self.__mk_path_uri(path))

    def __cp(self, src, dest):
        exe = [
            'aws',
            '--cli-read-timeout=' + str(_READ_TIMEOUT),
            's3',
            'cp',
            '--only-show-errors',
            src,
            dest ]
        subprocess.run(exe, check=False)

    def __mk_path_uri(self, path):
        return self.__bucket_uri + '/' + path
