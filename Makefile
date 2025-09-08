build: ## Build the base image
	docker compose build

up: ## Up container
	docker compose up

stop: ## Stop container
	docker compose stop

down: ## Down container
	docker compose down

up-d: ## Up container
	docker compose up -d

up-build: ## Build the base image
	docker compose up --build

makemigrations: ## Run django makemigrations command
	docker compose run web python manage.py makemigrations

migrate: ## Run django migrate command
	docker compose run web python manage.py migrate

shell: ## Run django shell command
	docker compose run web python manage.py shell

# ARGS=/app/fixtures/departments.json or /app/fixtures/products.json
load-fixtures:
	docker compose run web python manage.py loaddata $(ARGS)

test: ## Run django test command ARGS=--fixtures -v for scenario details
	docker compose run web pytest $(ARGS)

# docker exec ed2c09e98e46 python manage.py loaddata /app/fixtures/task_status.json
# make docker-exec CONTAINER_ID=inventory_container ARGS=bash
docker-exec: ## Run command in container make docker-exec CONTAINER_ID=244ff84b4b81 ARGS=bash
	docker exec -it $(CONTAINER_ID) $(ARGS)

#make docker-attach CONTAINER_ID=8be173a0b68a
docker-attach: ## docker attach
	docker attach --detach-keys ctrl-d $(CONTAINER_ID)

create-superuser:
	docker compose run web python manage.py createsuperuser

reset-db:
	docker compose run web python manage.py flush --noinput

dump-data:
	docker compose run web python manage.py dumpdata --indent 4 -o ${output} ${model}

docker-exec-web:
	docker compose exec web bash