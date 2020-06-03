#!/bin/bash

MODEL_STORE_DIR = 'test/model_store'
MMS_CONFIG_FILE = 'test/resources/config.properties'
MMS_LOG_FILE = 'mms_https.log'

POSTMAN_ENV_FILE = 'test/postman/environment.json'
POSTMAN_COLLECTION_JSON = 'test/postman/https_test_collection.json'
REPORT_FILE = 'test/https-api-report.html'

mkdir -p $MODEL_STORE_DIR

multi-model-server --start --mms-config $MMS_CONFIG_FILE --model-store MODEL_STORE_DIR >> $MMS_LOG_FILE 2>&1
sleep 10

newman run --insecure -e POSTMAN_ENV_FILE $POSTMAN_COLLECTION_JSON \
           -r cli,html --reporter-html-export $REPORT_FILE --verbose

multi-model-server --stop