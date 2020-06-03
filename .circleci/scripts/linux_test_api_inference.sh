#!/bin/bash

MODEL_STORE_DIR = 'test/model_store'
MMS_LOG_FILE = 'mms_inference.log'

POSTMAN_ENV_FILE = 'test/postman/environment.json'
POSTMAN_COLLECTION_JSON = 'test/postman/inference_api_test_collection.json'
POSTMAN_DATA_FILE = 'test/postman/inference_data.json'
REPORT_FILE = 'test/inference-api-report.html'

mkdir -p $MODEL_STORE_DIR

multi-model-server --start --model-store $MODEL_STORE_DIR >> $MMS_LOG_FILE 2>&1
sleep 10

newman run -e $POSTMAN_ENV_FILE $POSTMAN_COLLECTION_JSON -d $POSTMAN_DATA_FILE \
           -r cli,html --reporter-html-export $REPORT_FILE --verbose

multi-model-server --stop
