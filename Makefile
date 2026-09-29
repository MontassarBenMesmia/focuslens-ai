.PHONY: install test run docker clean

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest

run:
	uvicorn focuslens.api:app --reload

docker:
	docker compose up --build

clean:
	docker compose down
