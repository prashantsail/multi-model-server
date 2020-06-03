#!/bin/bash

mkdir -p test/model_store

multi-model-server --start --mms-config test/resources/config.properties \
                   --model-store test/model_store >> mms_https.log 2>&1
sleep 10
newman run --insecure -e test/postman/environment.json \
           --verbose test/postman/https_test_collection.json \
           -r cli,html --reporter-html-export test/https-api-report.html
multi-model-server --stop