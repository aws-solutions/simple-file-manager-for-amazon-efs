## Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
## SPDX-License-Identifier: Apache-2.0
import pytest
import os
import logging

@pytest.fixture(scope='session')
def testing_env_variables():
    logging.info('INFO: Setting variables for tests')
    try:
        test_env_vars = {
            'MEDIA_PATH': os.environ['TEST_MEDIA_PATH'],
            'FILE': os.environ['TEST_FILE_NAME'],
            'SFM_ENDPOINT': os.environ['SFM_ENDPOINT'],
            'SFM_USERNAME': os.environ['SFM_USERNAME'],
            'SFM_PASSWORD': os.environ['SFM_PASSWORD'],
            'FILESYSTEM_ID': os.environ['FILESYSTEM_ID']
            }
    except KeyError as e:
        logging.error("ERROR: Missing a required environment variable for testing: {variable}".format(variable=e))
        raise Exception(e)
    else:
        return test_env_vars