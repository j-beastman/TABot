# .PHONY: all clean datarobot_models

# all: install lint data/combined_data.csv

install:
	poetry install

# test:
# 	poetry run pytest

format:
	poetry run autopep8 --in-place --aggressive --aggressive --recursive streamlit
	poetry run isort --profile black streamlit
	poetry run black streamlit
	make lint

lint:
	poetry run isort --check --profile black streamlit
	poetry run black --check streamlit
	poetry run flake8 streamlit
	#poetry run pycodestyle
	#poetry run pylint streamlit

# clean:
# 	@$(RM) -rf data/*

run_site:
	poetry run streamlit run app.py


get_piazza_data:
	poetry run python piazza_data.py


load_docs:
	poetry run python load_docs.py