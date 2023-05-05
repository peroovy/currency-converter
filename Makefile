up:
	docker-compose up --build -d

down:
	docker-compose down

dev:
	adev runserver app/main.py

pshell:
	PIPENV_DONT_LOAD_ENV=1 pipenv shell

lint:
	isort . & \
	flake8 --config=setup.cfg & \
	black . --config=pyproject.toml

test:
	pytest tests

unit:
	pytest tests -m unit

integration:
	pytest tests -m integration