VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest

$(VENV):
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

test: $(VENV)
	$(PYTEST) test_ff_luck.py -v

run: $(VENV)
	$(PYTHON) ff_luck.py

clean:
	rm -rf $(VENV) .pytest_cache __pycache__
