.PHONY: init
init:
	poetry env use $(shell pyenv which python) && \
	poetry install

.PHONY: pytest
pytest:
	poetry run pytest -vv $(ARGS)

.PHONY: test
test:
	poetry run pytest $(ARGS)

.PHONY: pdb
pdb:
	poetry run pytest --pdb $(ARGS)

.PHONY: mypy
mypy: 
	poetry run mypy --ignore-missing-imports apihub_users

.PHONY: pre-commit
pre-commit: 
	pre-commit run --all-files

.PHONY: clean
clean:
	find . -name '__pycache__' -exec rm -rf {} +
