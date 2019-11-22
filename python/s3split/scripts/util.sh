#!/bin/bash
#
#   REMEMBER TO check syntax with https://github.com/koalaman/shellcheck
#

#set -x          # debug enabled
set -e          # exit on first error
set -o pipefail # exit on any errors in piped commands

#ENVIRONMENT VARIABLES

declare SCRIPT_DIR=""
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MINIO_SERVER_DATA="/tmp/minio-server/data"
MINIO_ACCESS_KEY="test_access"
MINIO_SECRET_KEY="test_secret"
BENCHMARK_FILES_1GB_PATH="/tmp/big-files/1gb"
# @info:  Parses and validates the CLI arguments
# @args:	Global Arguments $@

function parseCli() {
  if [[ "$#" -eq 0 ]]; then
      echo "  ${0}: "
      echo ""
      echo "               minio-server               start minio server "
      exit 0
  fi
  while [[ "$#" -gt 0 ]]; do
    declare KEY="$1"
    declare VALUE="$2"
    case "${KEY}" in
    # exec command here
    minio-server)
      # echo "Key: ${KEY} - Value: ${VALUE}"
      # echo "Script dir is: ${SCRIPT_DIR}"
      echo "Start minio server... data path: ${MINIO_SERVER_DATA} - access_key: ${MINIO_ACCESS_KEY} - secret key: ${MINIO_SECRET_KEY} "
      export MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
      export MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
      minio server ${MINIO_SERVER_DATA}
      ;;
    test-s3split-local-minio-1gb-files)
      echo "Run s3split with local minio"
      python "${SCRIPT_DIR}/../src/s3split.py" --s3-secret-key ${MINIO_SECRET_KEY} --s3-access-key ${MINIO_ACCESS_KEY} --s3-endpoint http://127.0.0.1:9000 --s3-bucket s3split-benchmarks --source-path "${BENCHMARK_FILES_1GB_PATH}"
    ;;
    test-s3split-remote-minio-1gb-files)
      echo "Run s3split with remote minio"
      # shellcheck source=${HOME}/.s3split
      source "${HOME}/.s3split"
      python "${SCRIPT_DIR}/../src/s3split.py" --s3-secret-key "${S3_SECRET_KEY}" --s3-access-key "${S3_ACCESS_KEY}" --s3-endpoint "${S3_ENDPOINT}" --s3-use-ssl True --s3-bucket "${S3_BUCKET}" --source-path "${BENCHMARK_FILES_1GB_PATH}"
    ;;
    -h | *)
      ${0}
      ;;
    esac
    shift
  done
}

parseCli "$@"
