# -*- coding: utf-8 -*-

"""
This provides the logic for performing transfer tests independent of the
transfer tool. It provides logic for both uploads and downloads.

An upload test performs the following actions. During setup, it creates a file
of a specific size named "test" locally in the current working directory. Then,
during its run phase, it uses the Tool object under test to upload this file.
Finally, during teardown, it deletes both the data object created by the upload
and the local file.

A download test performs the following actions. During setup, it creates a local
file in the current working directory of the size of the data object to be
downloaded. This file is named "test". While still in the set up phase, it
uploads the file to the current working collection in iRODS. The new data object
is also named "test". After the file is uploaded it is deleted. During the run
phase, it uses the Tool object under test to download the data object. Finally,
during teardown, it deletes both the data object and the file created by the
download.

The Python iRODS Client is used to perform the file transfers and clean up tasks
that happen during setup and teardown. This module assumes that an iRODS session
has been initialized for the zone where performance testing will happen.
"""

import os
from os import path

from irods.exception import LOCKED_DATA_OBJECT_ACCESS
from irods.session import iRODSSession

from suite import Test, TestFactory, TestFailure, Tool


_DATA_NAME = 'test'

try:
    _IRODS_ENV_FILE = os.environ['IRODS_ENVIRONMENT_FILE']
except KeyError:
    _IRODS_ENV_FILE = path.expanduser('~/.irods/irods_environment.json')


def _create_file(size):
    try:
        with open(_DATA_NAME, mode='ab') as file:
            file.truncate(size)
    except OSError as oe:
        raise TestFailure(f"failed to create file {_DATA_NAME} of size {size} B") from oe

def _delete_file():
    if path.exists(_DATA_NAME):
        os.remove(_DATA_NAME)


def _irods_path(irods):
    return f"/{irods.zone}/home/{irods.username}/{_DATA_NAME}"


def _delete_data_obj(irods):
    try:
        abs_path = _irods_path(irods)
        if irods.data_objects.exists(abs_path):
            irods.data_objects.unlink(abs_path, force=True)
    except LOCKED_DATA_OBJECT_ACCESS as exn:
        raise TestFailure(f"failed to delete data object {_DATA_NAME}") from exn

def _create_data_obj(irods, size):
    _create_file(size)
    irods.data_objects.put(_DATA_NAME, _irods_path(irods), force=True)
    _delete_file()


class _DownloadTest(Test):

    def __init__(self, tool: Tool, data_size: int):
        super(Test, self).__init__()
        self.__tool = tool
        self.__data_size = data_size

    def _run(self):
        self.__tool.download(_DATA_NAME)

    def _set_up(self):
        with iRODSSession(irods_env_file=_IRODS_ENV_FILE) as session:
            _create_data_obj(session, self.__data_size)

    def _tear_down(self):
        _delete_file()
        with iRODSSession(irods_env_file=_IRODS_ENV_FILE) as session:
            _delete_data_obj(session)


class DownloadTestFactory(TestFactory):
    """This is a factory for generating Test objects for download testing.
    Parameters:
        data_size  This is the size in bytes of the data object to download.
    """

    def __init__(self, data_size: int):
        self.__data_size = data_size

    def test_name(self):
        return f'{self.__data_size} B download'

    def make_test(self, tool):
        return _DownloadTest(tool, self.__data_size)


class _UploadTest(Test):

    def __init__(self, tool: Tool, data_size: int):
        super(Test, self).__init__()
        self.__tool = tool
        self.__data_size = data_size
        self.__irods = iRODSSession(irods_env_file=_IRODS_ENV_FILE)

    def __del__(self):
        self.__irods.cleanup()

    def _run(self):
        self.__tool.upload(_DATA_NAME)

    def _set_up(self):
        _delete_data_obj(self.__irods)
        _create_file(self.__data_size)

    def _tear_down(self):
        _delete_data_obj(self.__irods)
        _delete_file()


class UploadTestFactory(TestFactory):
    """This is a factory for generating Test objects for upload testing.
    Parameters:
        data_size  This is the size in bytes of the file to upload.
    """

    def __init__(self, data_size: int):
        self.__data_size = data_size

    def test_name(self):
        return f'{self.__data_size} B upload'

    def make_test(self, tool):
        return _UploadTest(tool, self.__data_size)
