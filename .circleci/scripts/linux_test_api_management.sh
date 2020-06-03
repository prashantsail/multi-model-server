#!/bin/bash

mkdir test/model_store
mkdir test/management-api/

multi-model-server --start --model-store test/model_store >> mms_management.log 2>&1
sleep 10
newman run -e test/postman/environment.json \
           --verbose test/postman/management_api_test_collection.json \
           -r cli,html --reporter-html-export test/management-api/management-api-report.html
multi-model-server --stop