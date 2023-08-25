# all: install lint data/combined_data.csv
FORMAT_DIRS := ./datachad ./deeplake

install:
	poetry install

format:
	autopep8 --in-place --aggressive --recursive $(FORMAT_DIRS)
	isort --profile black $(FORMAT_DIRS)
	black $(FORMAT_DIRS)
	make lint
# Lint target
lint:
	isort --check --profile black $(FORMAT_DIRS)
	black --check $(FORMAT_DIRS)
	flake8 $(FORMAT_DIRS)

# clean:
# 	@$(RM) -rf data/*

run_site:
	cd streamlit && streamlit run app.py


get_piazza_data:
	python deeplake/helpers/piazza_scrape.py

get_cs40_data:
	python deeplake/helpers/cs40_scraper.py


load_docs:
	python deeplake/update_deeplake.py
