#!/bin/bash
declare SOURCE_PATH=""
read -r -p "Mirror folder: " SOURCE_PATH

declare BUKET=""
read -r -p "BUKET: " BUKET

export MINIO_ACCESS_KEY=minio_access
export MINIO_SECRET_KEY=minio_secret

mc config host add localhost http://localhost:9000 "${MINIO_ACCESS_KEY}" "${MINIO_SECRET_KEY}"
mc mb "localhost/${BUKET}"
mc ls localhost/

time mc mirror "${SOURCE_PATH}" "localhost/${BUKET}"