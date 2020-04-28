# Remenber: makfile requires to indent with tabs!
# Credits: https://danishpraka.sh/2019/12/07/using-makefiles-for-go.html

.DEFAULT_GOAL := help

.PHONY: build run clean help setup

## build: build the application
build: clean
	@echo "Building..."
	@go build

## test: run tests recursively
test:
	go test ./...

## run: runs go run main.go
run:
	go run -race hello.go

## clean: cleans the binary
clean:
	@echo "Cleaning"
	@go clean

## setup: setup go modules
setup:
	@go mod init \
		&& go mod tidy \
		&& go mod vendor

help:
	@echo "Usage: \n"
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' |  sed -e 's/^/ /'