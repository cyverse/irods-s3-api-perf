# -*- coding: utf-8 -*-

"""This is the implementation of a Tool class for GoCommands.

This tool requires that GoCommands version 0.7+ is installed. It also requires
that a GoCommands session be initialized for the iRODS zone where performance
testing will happen.
"""

import subprocess
from subprocess import CalledProcessError

from suite import TestFailure, Tool


class GoCommands(Tool):
    """This provides the transfer logic for testing GoCommands."""

    def __str__(self):
        return "GoCommands"

    def download(self, path: str):
        try:
            subprocess.run(['gocmd', 'get', path], capture_output=True, check=True)
        except CalledProcessError as cpe:
            raise TestFailure(cpe.stderr.decode()) from cpe

    def upload(self, path: str):
        try:
            subprocess.run(['gocmd', 'put', path], capture_output=True, check=True)
        except CalledProcessError as cpe:
            raise TestFailure(cpe.stderr.decode()) from cpe
