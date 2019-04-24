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

declare SCRIPT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
declare FILE="env.sh"
# @info:    Parses and validates the CLI arguments
# @args:	Global Arguments $@

declare PARAM_A=''

function parseCli(){
	if [[ "$#" -eq 0 ]]; then
		usage
	fi
	while [[ "$#" -gt 0 ]]; do
		key="$1"
		val="$2"
		case $key in
      -h | --help ) usage; exit 0 ;;
      add) PARAM=$val; main; exit 0 ;;
      *) usage; exit 0;;
		esac
		shift
	done

}

# @info:	Prints out usage
function usage {
    echo
    echo "  ${0}: "
    echo "-------------------------------"
    echo
    echo "  -h or --help          Opens this help menu"
    echo "  add KEY=value             Replace or add KEY=value in env.sh   "
    echo
}

function main() {
  if [[ ! -f "${SCRIPT_PATH}/${FILE}" ]]; then
    echo "File ${FILE} not found... creating..."
    echo "#!/bin/bash" > "${SCRIPT_PATH}/${FILE}"
  fi
  KEY=${PARAM%=*}  # retain the part before the colon
  VALUE=${PARAM#*=}  # retain the part after the last slash
  if grep "${KEY}" "${SCRIPT_PATH}/${FILE}" > /dev/null ; then
    echo "Key ${KEY} found in file ${FILE}"
    sed -i -e "s|${KEY}=.*|${KEY}=\"${VALUE}\"|g" "${SCRIPT_PATH}/${FILE}"
  else 
    echo "Key ${KEY} NOT found in file ${FILE}"
    echo "export ${KEY}=\"${VALUE}\"" >> "${SCRIPT_PATH}/${FILE}"
  fi
  echo
  echo "Final env file: ${SCRIPT_PATH}/${FILE} "
  cat "${SCRIPT_PATH}/${FILE}"
  exit 0
}

parseCli "$@"











