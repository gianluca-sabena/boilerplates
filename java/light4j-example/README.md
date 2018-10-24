# Light4j example

Based on <https://doc.networknt.com/tutorial/rest/openapi/petstore/environment/>

## Generate

Use `manage.sh` to download and compile code generator lib and example openapi files

## Run

Build `cd openapi-petstore` and `mvn package exec:exec`

Export token `export TOKEN=` see [openapi-petstore/README.md](openapi-petstore/README.md)

Test API `curl -k -H "Authorization: $token" -X GET https://0.0.0.0:8443/v1/pets`