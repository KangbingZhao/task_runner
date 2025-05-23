.PHONY: init run clean

VENV=.venv

init:
	uv venv $(VENV)
	. $(VENV)/bin/activate && uv pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

run:
	PYTHONPATH=. . $(VENV)/bin/activate && python core/scheduler.py

clean:
	rm -rf $(VENV)
