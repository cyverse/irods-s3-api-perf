# irods-s3-api-perf

This tests the transfer performance of the iRODS S3 API and compares it against iCommands and GoCommands. It uses the AWS CLI to transfer files through the S3 API. Transfers of 1 kiB files are used to compare the overhead of the client, i.e., the amount of time the client takes outside of transferring data. Transfers of 1 GiB files are used to compare client throughput. Both uploads and downloads are compared. Each transfer is performed five times. The geometric mean is reported in seconds along with the its one geometric standard deviation bounds.

## Configuration

Before using this suite, the Python dependencies need to be installed. It depends on numpy and python-irodsclient. The full set of requirements are captured `requirements.txt` and can be installed using pip.

```console
pip install --requirement=requirements.txt
```

This requires the following external programs be installed.

- AWS CLI 2.15+
- GoCommands 0.7+
- iCommands 4.3+

All three applications need to be configured to talk to the iRODS zone that will be used for testing and have their sessions initialized.

## Execution

This program will generate a 1 kiB and a 1 GiB temporary file locally in the current working directory and in the current working collection in iRODS, so the program should be run from a location in the file system where it can create these files.

The performance testing program is named `s3api_perf`. When executing it, the name of the iRODS bucket that will be used during testing is required. The performance results are written to stdout, while all notification messages, like progress updates, are written to stderr. This allows performance results to be redirected to a file. If stdout is redirected, the performance results will be written to both stdout and stderr.

```console
./s3api_perf irods-bucket > results
starting performance test suite
performing 1024 B upload tests
   ⋮
```
