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
    -h | *)
      ${0}
      ;;
    esac
    shift
  done
  cd "${CURRENT_PATH}"
}


parseCli "$@"