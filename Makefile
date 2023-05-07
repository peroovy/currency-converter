up:
	docker-compose up --build -d

build:
	docker-compose build

down:
	docker-compose down

# $s [service name]
logs:
	docker-compose logs $s

test:
	make build
	docker-compose run app pytest tests
	make down

unit:
	make build
	docker-compose run app pytest tests -m unit
	make down

integration:
	make build
	docker-compose run app pytest tests -m integration
	make down

dev:
	adev runserver app/main.py

pshell:
	PIPENV_DONT_LOAD_ENV=1 pipenv shell

lint:
	isort . & \
	flake8 --config=setup.cfg & \
	black . --config=pyproject.toml