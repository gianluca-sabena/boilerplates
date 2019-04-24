#!/bin/bash
#
#   Example bash script
#
#   REMEMBER TO check syntax with https://github.com/koalaman/shellcheck
#

#set -x          # debug enabled
set -e          # exit on first error
set -o pipefail # exit on any errors in piped commands

#ENVIRONMENT VARIABLES

declare SCRIPT_DIR=""
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# @info:	current version
declare VERSION="1.0.0"

# @info:  Parses and validates the CLI arguments
# @args:	Global Arguments $@

function parseCli() {
  if [[ "$#" -eq 0 ]]; then
    usage
  fi
  while [[ "$#" -gt 0 ]]; do
    declare KEY="$1"
    declare VALUE="$2"
    case "${KEY}" in
    # exec command here
    -action)
      main "${KEY}" "${VALUE}"
      exit 0
      ;;
    -v | --version)
      version
      exit 0
      ;;
    # or delegate to main function
    -h | --help)
      usage
      exit 0
      ;;
    *)
      usage
      exit 0
      ;;
    esac
    shift
  done

}

# @info:	Prints out usage
function usage() {
  echo
  echo "  ${0}: "
  echo "-------------------------------"
  echo
  echo "  -h or --help          Opens this help menu"
  echo "  -v or --version       Prints the current docker-clean version"
  echo
  echo
  echo "  -action value               first param "
  echo
}

function version() {
  echo "Version: ${VERSION}"
  exit 0
}

function main() {
  declare KEY="$1"
  declare VALUE="$2"
  echo "Key: ${KEY}"
  echo "Value: ${VALUE}"
  case "${VALUE}" in
  info)
    echo "Script dir is: ${SCRIPT_DIR}"
    ;;
  test)
    echo "Test!"
    ;;
  *)
    usage
    exit 0
    ;;
  esac

}

parseCli "$@"
