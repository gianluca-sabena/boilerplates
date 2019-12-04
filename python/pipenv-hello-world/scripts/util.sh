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
declare CURRENT_PATH
CURRENT_PATH=$(pwd)
declare APP_NAME="helloworld"
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
    # declare VALUE="$2"
    case "${KEY}" in
    # exec command here
    test-pip-install)
      export PIPENV_IGNORE_VIRTUALENVS=1
      export PIPENV_VENV_IN_PROJECT="enabled"
      # export DISTUTILS_DEBUG="enabled"
      rm -rf /tmp/${APP_NAME}
      mkdir -p /tmp/${APP_NAME}
      cd /tmp/${APP_NAME}
      pipenv --python 3.7
      ls "${SCRIPT_DIR}/../"
      pipenv run pip install "${SCRIPT_DIR}/../"
      pipenv run ${APP_NAME}
      cd "${CURRENT_PATH}"
    ;;
    run)
      python "${SCRIPT_DIR}/../src/${APP_NAME}/app.py"
    ;;
    test)
      python run pytest
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
