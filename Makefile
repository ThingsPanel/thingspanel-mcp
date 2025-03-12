.PHONY: install build test run docker-build docker-run docker-stop clean

install:
	pip install -e ".[dev,lint]"

build:
	pip install build
	python -m build

test:
	pytest

run:
	thingspanel-mcp

docker-build:
	docker build -t thingspanel-mcp:latest .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

clean:
	rm -rf build/ dist/ *.egg-info/
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete 