pre: format check pre-commit

format:
	poetry run isort src/
	poetry run isort tests/
	poetry run ruff format src/
	poetry run ruff format tests/


check:
	poetry run isort src/ --check
	poetry run isort tests/ --check
	poetry run ruff check src/
	poetry run ruff check tests/
	# poetry run mypy src/

pre-commit:
	# poetry run pre-commit run --all-files
	poetry run pre-commit run -a --show-diff-on-failure --color always

mypy:
	poetry run mypy src/

deptry:
    # вернёт неиспользуемые зависимости
	poetry run deptry .

tests:
	# без mark "local": tests -m "not local"
	poetry run pytest --cov-report xml --cov-report term --cov src -n 4 tests

exe:
	# пример:
	# -F - один файл;
	pyinstaller -F -n draw_frames.exe pyinstaller main.py
