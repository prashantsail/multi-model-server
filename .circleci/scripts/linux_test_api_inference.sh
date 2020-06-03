#!/bin/bash

mkdir test/model_store
mkdir test/inference-api/

multi-model-server --start --model-store test/model_store >> mms_inference.log 2>&1
sleep 10
newman run -e test/postman/environment.json \
           --verbose test/postman/inference_api_test_collection.json \
           -d test/postman/inference_data.json \
           -r cli,html --reporter-html-export test/inference-api/inference-api-report.html
multi-model-server --stop
