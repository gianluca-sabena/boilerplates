#!/bin/bash
#
#   Example bash script
#
#   REMEMBER TO check syntax with https://github.com/koalaman/shellcheck
#

# set -x          # debug enabled
set -e          # exit on first error
set -o pipefail # exit on any errors in piped commands

# ENVIRONMENT VARIABLES
declare SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
declare MODEL=''

function parseCli(){
	if [[ "$#" -eq 0 ]]; then
		usage
	fi
	while [[ "$#" -gt 0 ]]; do
		key="$1"
		val="$2"
		case $key in
			download) PARAM_A=$val; download; exit 0;;
			generate-petstore) MODEL=$val; generatePetstore; exit 0;;
			generate-proxy) MODEL=$val; generateProxy; exit 0;;
			generate-datajob) MODEL=$val; generateDatajob; exit 0;;
			-h | --help | *) usage; exit 0 ;;
		esac
		shift
	done

}

# @info:	Prints out usage
function usage {
    echo
    echo "  ${0}: "
    echo "-------------------------------"
    echo "  -h or --help         Opens this help menu"
    echo "  download             Download generator"
    echo "  generate-petstore    Run generator"
    echo "  generate-proxy       Run generator"
    echo "  generate-datajob     Run generator"
    echo
}


function download() {
  mkdir -p ${SCRIPT_DIR}/generator
	git clone https://github.com/networknt/light-codegen.git ${SCRIPT_DIR}/generator || echo "Repo already present!"
	cd ${SCRIPT_DIR}/generator
	mvn install -DskipTests
}

function generatePetstore() {
	mkdir -p ${SCRIPT_DIR}/openapi-petstore/model
	CODEGEN_JAR="${SCRIPT_DIR}/generator/codegen-cli/target/codegen-cli.jar"
	curl -o ${SCRIPT_DIR}/openapi-petstore/model/openapi-petstore-config.json https://raw.githubusercontent.com/networknt/model-config/master/rest/openapi/petstore/1.0.0/config.json
	curl -o ${SCRIPT_DIR}/openapi-petstore/model/openapi-petstore-openapi.json https://raw.githubusercontent.com/networknt/model-config/master/rest/openapi/petstore/1.0.0/openapi.json
	java -jar $CODEGEN_JAR  -f openapi -o ${SCRIPT_DIR}/openapi-petstore -m ${SCRIPT_DIR}/openapi-petstore/model/openapi-petstore-openapi.json -c ${SCRIPT_DIR}/openapi-petstore/model/openapi-petstore-config.json
}

function generateProxy() {
	mkdir -p ${SCRIPT_DIR}/openapi-proxy/model
	CODEGEN_JAR="${SCRIPT_DIR}/generator/codegen-cli/target/codegen-cli.jar"
	curl -o ${SCRIPT_DIR}/openapi-proxy/model/openapi-proxy-config.json https://raw.githubusercontent.com/networknt/model-config/master/rest/openapi/proxy-backend/config.json
	curl -o ${SCRIPT_DIR}/openapi-proxy/model/openapi-proxy-openapi.json https://raw.githubusercontent.com/networknt/model-config/master/rest/openapi/proxy-backend/openapi.json
	java -jar $CODEGEN_JAR  -f openapi -o ${SCRIPT_DIR}/openapi-proxy -m ${SCRIPT_DIR}/openapi-proxy/model/openapi-proxy-openapi.json -c ${SCRIPT_DIR}/openapi-proxy/model/openapi-proxy-config.json
}

function generateDatajob() {
	mkdir -p ${SCRIPT_DIR}/data-job/model
	CODEGEN_JAR="${SCRIPT_DIR}/generator/codegen-cli/target/codegen-cli.jar"
	java -jar $CODEGEN_JAR  -f openapi -o ${SCRIPT_DIR}/data-job -m ${SCRIPT_DIR}/data-job/model/data-job.yaml -c ${SCRIPT_DIR}/data-job/model/data-job-config.json
}

parseCli "$@"

main





