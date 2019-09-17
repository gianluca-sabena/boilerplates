#!/bin/bash
declare DEST_PATH=""
read -r -p "Minio folder: " DEST_PATH

export MINIO_ACCESS_KEY=minio_access
export MINIO_SECRET_KEY=minio_secret

minio server "${DEST_PATH}"