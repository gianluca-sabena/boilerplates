#!/bin/bash
#
#   REMEMBER TO check syntax with https://github.com/koalaman/shellcheck
#

#set -x          # debug enabled
set -e          # exit on first error
set -o pipefail # exit on any errors in piped commands

#ENVIRONMENT VARIABLES
declare SCRIPT_PATH=""
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
declare CURRENT_PATH
CURRENT_PATH=$(pwd)
declare APP_NAME="s3split"
MINIO_SERVER_DATA="/tmp/minio-server/data"
MINIO_ACCESS_KEY="test_access"
MINIO_SECRET_KEY="test_secret"
PATH_TEST_FILES="/tmp/s3cmd-test-files"
# @info:  Parses and validates the CLI arguments
# @args:	Global Arguments $@

function parseCli() {
  if [[ "$#" -eq 0 ]]; then
      echo "  ${0}: {command}"
      echo ""
      echo "  command:"
      echo "    - prepare-dev-venv"
      echo "    - run-python"
      echo "    - run-cli"
      echo "    - run-test"
      echo "    - test-pip-install"
      echo ""
      echo "    - minio-server               start minio server "
      echo ""
      exit 0
  fi
  while [[ "$#" -gt 0 ]]; do
    declare KEY="$1"
    # declare VALUE="$2"
    case "${KEY}" in
    # exec command here
    create-pipenv-dev)
      cd  "${SCRIPT_PATH}/../"
      # install current package in editable mode (use simlink to source code)
      # https://setuptools.readthedocs.io/en/latest/setuptools.html#development-mode
      # https://pipenv-fork.readthedocs.io/en/latest/basics.html#editable-dependencies-e-g-e
      pipenv install --dev
      echo ""
      echo "========== Test run cli: pipenv run ${APP_NAME} ========== "
      pipenv run ${APP_NAME}
      echo ""
      echo "========== Test run module: pipenv run python -m helloworld.main ========== "
      pipenv run python -m helloworld.main
      echo ""
    ;;
    test-pip-install)
      export TMP_VENV_PATH="/tmp/pipenv/${APP_NAME}"
      echo ""
      echo "========== Create venv in temp folder: ${TMP_VENV_PATH} ========== "
      export PIPENV_IGNORE_VIRTUALENVS=1
      export PIPENV_VENV_IN_PROJECT="enabled"
      # export DISTUTILS_DEBUG="enabled"
      [ -d "${TMP_VENV_PATH}" ] && rm -rf "${TMP_VENV_PATH}"
      mkdir -p "${TMP_VENV_PATH}"
      cd "${TMP_VENV_PATH}"
      pipenv --python 3.7
      echo "========== Install ${APP_NAME} package name from source ${SCRIPT_PATH}/../setup.py ========== "
      pipenv run pip install "${SCRIPT_PATH}/../"
      echo ""
      echo "========== Test run cli: pipenv run ${APP_NAME} ========== "
      pipenv run ${APP_NAME}
      echo ""
      echo "========== Test run module: pipenv run python -m helloworld.main ========== "
      pipenv run python -m helloworld.main
      echo ""
    ;;
    run-python)
      cd "${SCRIPT_PATH}/../"
      pipenv run pip install -e .
      pipenv run python "${SCRIPT_PATH}/../src/${APP_NAME}/main.py"
    ;;
    run-cli)
      cd "${SCRIPT_PATH}/../"
      pipenv run pip install -e .
      pipenv run ${APP_NAME}
    ;;
    run-test)
      cd "${SCRIPT_PATH}/../"
      pipenv run pytest -v
    ;;
    minio-server)
      # echo "Key: ${KEY} - Value: ${VALUE}"
      # echo "Script dir is: ${SCRIPT_PATH}"
      echo "Start minio server... data path: ${MINIO_SERVER_DATA} - access_key: ${MINIO_ACCESS_KEY} - secret key: ${MINIO_SECRET_KEY} "
      export MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
      export MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
      minio server ${MINIO_SERVER_DATA}
      ;;
    generate-data)
      # Generate 5 GB + 1 GB
      local SIZE=1024
      local NUM_FILES=128
      local NUM_FOLDERS=40
      local TOTAL=$(( SIZE * NUM_FILES * NUM_FOLDERS))
      #local PATH_BASE="${PATH_TEST_FILES}/${NUM_FOLDERS}d-${NUM_FILES}f-${SIZE}kb"
      local PATH_BASE="${PATH_TEST_FILES}/random"
      mkdir -p "${PATH_BASE}"
      local counter=1
      while [[ $counter -le $NUM_FOLDERS ]]; do
        genfilesrandom ${PATH_BASE}/dir_${counter} ${SIZE} ${NUM_FILES}
        ((counter += 1))
      done
      # To do generate 8 files * 128 Mb = 1 GB
      local SIZE=$(( 1024 * 128 ))
      genfilesrandom ${PATH_BASE} ${SIZE} 8
      local TOTAL; TOTAL=$(du -sh ${PATH_BASE})
      echo "Generated total KB: ${TOTAL}"

    ;;
    test-s3split-local-minio)
      local PATH_PREFIX="random"
      #echo "Run s3split with local minio"
      python "${SCRIPT_PATH}/../src/s3split/main.py" --s3-secret-key ${MINIO_SECRET_KEY} --s3-access-key ${MINIO_ACCESS_KEY} --s3-endpoint http://127.0.0.1:9000 --s3-bucket s3split-benchmarks --s3-path "${PATH_PREFIX}" --fs-path "${PATH_TEST_FILES}/${PATH_PREFIX}"
    ;;
    test-s3split-fail)
      local PATH_PREFIX="random"
      #echo "Run s3split with local minio"
      python "${SCRIPT_PATH}/../src/s3split/main.py" --s3-secret-key A --s3-access-key B --s3-endpoint C --s3-bucket D --s3-path E --fs-path /tmp upload
    ;;
    test-s3split-local-minio-1gb-files)
      echo "Run s3split with local minio"
      python "${SCRIPT_PATH}/../src/s3split/main.py" --s3-secret-key ${MINIO_SECRET_KEY} --s3-access-key ${MINIO_ACCESS_KEY} --s3-endpoint http://127.0.0.1:9000 --s3-bucket s3split-benchmarks --fs-path "${BENCHMARK_FILES_1GB_PATH}" 
    ;;
    test-s3split-remote-minio-1gb-files)
      echo "Run s3split with remote minio"
      # shellcheck disable=SC1091,SC1090
      source "${HOME}/.s3split"
      python "${SCRIPT_PATH}/../src/s3split/main.py" --s3-secret-key "${S3_SECRET_KEY}" --s3-access-key "${S3_ACCESS_KEY}" --s3-endpoint "${S3_ENDPOINT}" --s3-use-ssl True --s3-bucket "${S3_BUCKET}" --fs-path "${BENCHMARK_FILES_1GB_PATH}"
    ;;
    -h | *)
      ${0}
      ;;
    esac
    shift
  done
}


#
# genfilesrandom FOLDER SIZE_KB NUM_FILES
#
function genfilesrandom() {
  local DEST_PATH=${1}
  local SIZE=$((1024 * $2))
  local NUM_FILES=$3
  mkdir -p "${DEST_PATH}"
  echo "Dest folder: ${DEST_PATH}"
  echo "Size kb: ${SIZE}"
  echo "Number of files: ${NUM_FILES}"
  echo "Creating master file..."
  head -c "$SIZE" /dev/urandom >"${DEST_PATH}/file_1.txt"
  local counter=2
  while [[ $counter -le $NUM_FILES ]]; do
    echo "Duplicating file: $counter "
    cp "${DEST_PATH}/file_1.txt" "${DEST_PATH}/file_${counter}.txt"
    ((counter += 1))
  done
}
parseCli "$@"
