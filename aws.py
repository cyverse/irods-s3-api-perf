# -*- coding: utf-8 -*-

""" This is the implementation of a Tool class for the AWS CLI.

This tool requires that AWS CLI version 2.15+ is installed. It also requires
that the CLI be configured to connect to the performance testing iRODS zone by
default.
"""

import subprocess
from subprocess import CalledProcessError

from suite import TestFailure, Tool

_READ_TIMEOUT = 300


class AWS(Tool):
    """This provides the transfer logic for testing AWS CLI.
    Parameters:
        bucket  This is the name of the bucket where data will be transferred
            to and from.
    """

    def __init__(self, bucket: str):
        self.__bucket_uri = f's3://{bucket}'

    def __str__(self):
        return "iRODS S3 API over AWS CLI"

    def download(self, path: str):
        self.__cp(self.__mk_path_uri(path), path)

    def upload(self, path: str):
        self.__cp(path, self.__mk_path_uri(path))

    def __cp(self, src: str, dest: str):
        """
        This method builds the AWS CLI command to copy an object from a
        source to a destination within S3 storage.
        """
        try:
            exe = [
                'aws',
                f'--cli-read-timeout={_READ_TIMEOUT}',
                's3',
                'cp',
                '--only-show-errors',
                src,
                dest]
            subprocess.run(exe, capture_output=True, check=True)
        except CalledProcessError as cpe:
            raise TestFailure(cpe.stderr.decode()) from cpe

    def __mk_path_uri(self, path: str):
        return f"{self.__bucket_uri}/{path}"
