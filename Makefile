# load and export .env
ifneq (,$(wildcard ./.env))
  include .env
  export
endif


## init project
init: check-submodule
	sudo apt-get install imagemagick
	python3 -m pip install -r requirements.txt
	python3 -m pip install -r module_gmail_sender/requirements.txt
	python3 -m pip install -r module_python_l10n_logger/requirements.txt
.PHONY: init

# check out git submodules
check-submodule:
	@if [ ! -f "./module_gmail_sender/.git" ]; then \
		echo "Submodule Gmail Sender not found. Adding submodule..."; \
		git submodule add https://github.com/jeffreycai/module_gmail_sender.git module_gmail_sender; \
	fi
	@echo "Checking out tag v1.0.0 in submodule..."; \
	git submodule update --init --recursive module_gmail_sender; \
	cd module_gmail_sender && git checkout v1.0.0

	@if [ ! -f "./module_python_l10n_logger/.git" ]; then \
		echo "Submodule Python L10n logger not found. Adding submodule..."; \
		git submodule add https://github.com/jeffreycai/module_python_l10n_logger.git module_python_l10n_logger; \
	fi
	@echo "Checking out tag v1.0.0 in submodule..."; \
	git submodule update --init --recursive module_gmail_sender; \
	cd module_gmail_sender && git checkout v1.0.0

	@if [ ! -f "./AIconic/.git" ]; then \
		echo "Submodule AIconic not found. Adding submodule..."; \
		git submodule add https://github.com/jeffreycai/AIconic.git AIconic; \
	fi
	git submodule update --init --recursive module_gmail_sender;
.PHONY: check-submodule

## app command
run:
	bash shell/run.sh
.PHONY: run

stop:
	bash shell/stop.sh
.PHONY: stop

restart: stop run
.PHONY: restrat

update:
	git submodule update --init --recursive
.PHONY: update