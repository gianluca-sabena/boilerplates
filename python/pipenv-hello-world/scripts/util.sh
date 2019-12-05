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
      echo "  ${0}: {command}"
      echo ""
      echo "  command:"
      echo "    - prepare-dev-venv"
      echo "    - run-python"
      echo "    - run-cli"
      echo "    - run-test"
      echo "    - test-pip-install"
      exit 0
  fi
  while [[ "$#" -gt 0 ]]; do
    declare KEY="$1"
    # declare VALUE="$2"
    case "${KEY}" in
    # exec command here
    create-pipenv-dev)
      cd  "${SCRIPT_DIR}/../"
      pipenv install --dev
      # install current package in editable mode (use simlink to source code)
      # https://setuptools.readthedocs.io/en/latest/setuptools.html#development-mode
      pipenv run pip install -e .
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
      pipenv run pip install "${SCRIPT_DIR}/../"
      echo ""
      echo "========== Test run cli: pipenv run ${APP_NAME} ========== "
      pipenv run ${APP_NAME}
      echo ""
      echo "========== Test run module: pipenv run python -m helloworld.main ========== "
      pipenv run python -m helloworld.main
      echo ""
    ;;
    run-python)
      cd "${SCRIPT_DIR}/../"
      pipenv run pip install -e .
      pipenv run python "${SCRIPT_DIR}/../src/${APP_NAME}/main.py"
    ;;
    run-cli)
      cd "${SCRIPT_DIR}/../"
      pipenv run pip install -e .
      pipenv run ${APP_NAME}
    ;;

    run-test)
      cd "${SCRIPT_DIR}/../"
      pipenv run pytest -v
    ;;
    -h | *)
      ${0}
      ;;
    esac
    shift
  done
  cd "${CURRENT_PATH}"
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
