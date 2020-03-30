.DEFAULT_GOAL := help
.PHONY: install-dev

# https://stackoverflow.com/a/23324703
export ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
export NVM_DIR := $(ROOT_DIR)/.local/.nvm
export JUPYTER_CONFIG_DIR := $(ROOT_DIR)/.local/jupyterlab/config
export JUPYTER_PATH := $(ROOT_DIR)/.local/jupyterlab/path
export JUPYTER_DATA_DIR := $(ROOT_DIR)/.local/jupyterlab/data
export JUPYTER_RUNTIME_DIR := $(ROOT_DIR)/.local/jupyterlab/runtime

test:
	printenv;
	echo $(ROOT_DIR)

install-dev:
	@if [ ! -d ".venv" ]; then \
		pipenv install --dev; \
		[ -s "/usr/local/opt/nvm/nvm.sh" ] && . "/usr/local/opt/nvm/nvm.sh"; \
		nvm install v12.16.1; \
		nvm use --delete-prefix v12.16.1; \
		npm install -g tslab; \
		pipenv run tslab install; \
	fi

activate: install-dev
	pipenv shell

clean:
	rm -rf $(ROOT_DIR)/.venv
	rm -rf $(ROOT_DIR)/.local
	rm -rf $(ROOT_DIR)/node_modules

.PHONY:jupyterlab
jupyterlab: install-dev
	[ -s "/usr/local/opt/nvm/nvm.sh" ] && . "/usr/local/opt/nvm/nvm.sh"; \
	pipenv run tslab install; \
	pipenv run jupyter lab --notebook-dir=notebooks;

# credits https://stackoverflow.com/a/26339924/7568979
help:
	@echo "--- automatic extracted targets: ---"
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print "" $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'