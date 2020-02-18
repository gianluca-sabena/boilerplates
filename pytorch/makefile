.DEFAULT_GOAL := help

# .PHONY: install-dev

install-dev:
	@if [ ! -d ".venv" ]; then \
		pipenv install --dev; \
	fi

activate: install-dev
	pipenv shell

clean:
	rm -rf .venv
	rm -rf runs

run-mnist-simple: install-dev
	pipenv run python mnist-tensorboard/src/mnist-tensorboard-simple.py

open-tensorboard-simple: install-dev
	pipenv run tensorboard --logdir=runs/mnist-simple

run-mnist-full: install-dev
	pipenv run python mnist-tensorboard/src/mnist-tensorboard-full.py

open-tensorboard-full: install-dev
	pipenv run tensorboard --logdir=runs/mnist-full

run-torchscript-simple:
	pipenv run python torch-script/simple.py

# credits https://stackoverflow.com/a/26339924/7568979
help:
	@echo "--- automatic extracted targets: ---"
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print "" $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'
