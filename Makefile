.PHONY: init run clean test docker-build

VENV=.venv

init:
	uv venv $(VENV)
	. $(VENV)/bin/activate && uv pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

run:
	PYTHONPATH=. . $(VENV)/bin/activate && python core/scheduler.py

clean:
	rm -rf $(VENV)

test:
	. $(VENV)/bin/activate && python -m unittest discover -s tests

docker-build:
	docker build -t notion-runner-image .
