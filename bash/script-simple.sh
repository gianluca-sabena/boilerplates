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

# @info:  Parses and validates the CLI arguments
# @args:	Global Arguments $@

function parseCli() {
  while [[ "$#" -gt 0 ]]; do
    declare KEY="$1"
    declare VALUE="$2"
    case "${KEY}" in
    # exec command here
    -action)
      echo "Key: ${KEY} - Value: ${VALUE}"
      echo "Script dir is: ${SCRIPT_DIR}"
      exit 0
      ;;
    -h | *)
      echo "  ${0}: "
      echo ""
      echo "               -action value               first param "
      exit 0
      ;;
    esac
    shift
  done
  ${0} -h
}

parseCli "$@"
