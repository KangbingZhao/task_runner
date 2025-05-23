.PHONY: build run clean

VENV=.venv

build:
	uv venv $(VENV)
	. $(VENV)/bin/activate && uv pip install -r requirements.txt

run:
	. $(VENV)/bin/activate && python core/scheduler.py

clean:
	rm -rf $(VENV)
