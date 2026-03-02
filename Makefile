.SILENT:

VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest

$(VENV):
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

test: $(VENV)
	$(PYTEST) test_ff_luck.py -v

THROUGH_WEEK_ARG = $(if $(THROUGH_WEEK),--through-week $(THROUGH_WEEK),)
DEBUG_ARG = $(if $(DEBUG),--debug,)

run: $(VENV)
	$(PYTHON) ff_luck.py --league-id $(LEAGUE_ID) --year $(YEAR) $(THROUGH_WEEK_ARG) $(DEBUG_ARG)

clean:
	rm -rf $(VENV) .pytest_cache __pycache__
