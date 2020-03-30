.DEFAULT_GOAL := help
.PHONY: install-dev

export ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
export JUPYTER_CONFIG_DIR := $(ROOT_DIR)/.local/jupyterlab/config
export JUPYTER_PATH := $(ROOT_DIR)/.local/jupyterlab/path
export JUPYTER_DATA_DIR := $(ROOT_DIR)/.local/jupyterlab/data
export JUPYTER_RUNTIME_DIR := $(ROOT_DIR)/.local/jupyterlab/runtime

install-dev:
	@if [ ! -d ".venv" ]; then \
	  pipenv install --dev; \
	fi

activate: install-dev
	pipenv shell

clean:
	rm -rf .venv

jupyter-notebook: install-dev
	pipenv run jupyter notebook --notebook-dir=notebooks

# credits https://stackoverflow.com/a/26339924/7568979
help:
	@echo "--- automatic extracted targets: ---"
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print "" $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'