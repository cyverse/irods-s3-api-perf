# -*- coding: utf-8 -*-

"""TODO document"""

import subprocess

from suite import Tool


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
        subprocess.run(['aws', 's3', 'cp', '--only-show-errors', src, dest], check=False)

    def __mk_path_uri(self, path):
        return self.__bucket_uri + '/' + path
