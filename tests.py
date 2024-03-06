# -*- coding: utf-8 -*-

"""TODO document"""

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
    """TODO document"""

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
    """TODO document"""

    def __init__(self, data_size: int):
        self.__data_size = data_size

    def test_name(self):
        return f'{self.__data_size} B upload'

    def make_test(self, tool):
        return _UploadTest(tool, self.__data_size)
