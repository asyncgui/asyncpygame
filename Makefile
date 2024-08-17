PYTEST = python -m pytest
FLAKE8 = python -m flake8

test:
	$(PYTEST) ./tests

style:
	$(FLAKE8) --count --show-source --max-complexity=10 --max-line-length=119 --statistics ./src/asyncpygame
	$(FLAKE8) --count --show-source --max-complexity=10 --max-line-length=999 --statistics ./examples ./tests

html:
	sphinx-build -b html ./sphinx ./docs

livehtml:
	sphinx-autobuild -b html ./sphinx ./docs
