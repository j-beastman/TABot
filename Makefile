# all: install lint data/combined_data.csv
FORMAT_DIRS := ./datachad ./piazza-api ./deeplake

install:
	poetry install

format:
	poetry run autopep8 --in-place --aggressive --recursive $(FORMAT_DIRS)
	poetry run isort --profile black $(FORMAT_DIRS)
	poetry run black $(FORMAT_DIRS)
	make lint
# Lint target
lint:
	poetry run isort --check --profile black $(FORMAT_DIRS)
	poetry run black --check $(FORMAT_DIRS)
	poetry run flake8 $(FORMAT_DIRS)

# clean:
# 	@$(RM) -rf data/*

run_site:
	poetry run streamlit run app.py


get_piazza_data:
	poetry run python piazza_data.py


load_docs:
	poetry run python load_docs.py