# irods-s3-api-perf

This tests the transfer performance of the iRODS S3 API and compares it against iCommands and GoCommands. It uses the AWS CLI to transfer files through the S3 API. Transfers of 1 kiB files are used to compare the overhead of the client, i.e., the amount of time the client takes outside of transferring data. Transfers of 1 GiB files are used to compare client throughput. Both uploads and downloads are compared. Each transfer is performed five times. The geometric mean is reported in seconds along with the its one geometric standard deviation bounds.

## Configuration

Before using this suite, the Python dependencies need to be installed. It depends on numpy and python-irodsclient. The full set of requirements are captured `requirements.txt` and can be installed using pip.

```console
pip install --requirement=requirements.txt
```

<!-- TODO discuss AWS CLI configuration -->

<!-- TODO discuss iCommands configuration -->

<!-- TODO discuss GoCommands configuration -->

<!-- TODO discuss execution -->
