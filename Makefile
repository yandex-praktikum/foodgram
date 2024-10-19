MANAGEPY = python project/manage.py
DC = docker compose
ENV_FILE = --env-file backend/.env
APP_FILE = infra/docker-compose.yml
EXEC = docker exec -it
APP_CONTAINER = foodgram-back
FRONT_CONTAINER = foodgram-front
LOGS = docker logs


.PHONY: app
app:
	${DC} -f ${APP_FILE} up --build -d


.PHONY: app-logs
app-logs:
	${LOGS} ${APP_CONTAINER} -f 


.PHONY: front-logs
front-logs:
	${LOGS} ${FRONT_CONTAINER} -f


.PHONY: app-down
app-down:
	${DC} -f ${APP_FILE} down


.PHONY: migrate
migrate:
	${EXEC} ${APP_CONTAINER} ${MANAGEPY} migrate


.PHONY: migrations
migrations:
	${EXEC} ${APP_CONTAINER} ${MANAGEPY} makemigrations


.PHONY: superuser
superuser:
	${EXEC} ${APP_CONTAINER} ${MANAGEPY} createsuperuser


.PHONY: collectstatic
collectstatic:
	${EXEC} ${APP_CONTAINER} ${MANAGEPY} collectstatic


.PHONY: ingredient
ingredient:
	${EXEC} ${APP_CONTAINER} ${MANAGEPY} import_ingredients ./backend/data/ingredients.csv


.PHONY: tag
tag:
	${EXEC} ${APP_CONTAINER} ${MANAGEPY} import_tags ./backend/data/tags.csv