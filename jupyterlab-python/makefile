.DEFAULT_GOAL := help
.PHONY: install-dev

export JUPYTER_CONFIG_DIR := .local/.jupyterlab

install-dev:
	@if [ ! -d ".venv" ]; then \
	  pipenv install --dev; \
	fi

activate: install-dev
	pipenv shell

clean:
	rm -rf .venv

jupyterlab: install-dev
	pipenv run jupyter lab --notebook-dir=notebooks

# credits https://stackoverflow.com/a/26339924/7568979
help:
	@echo "--- automatic extracted targets: ---"
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print "" $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'