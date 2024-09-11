# lighthouse-server
Main service for LLM Monitoring Service — LightHouse


# PROD BUILD
1. Создайте файл .env из примера .env.example и заполните его.
2. Развертывание:
   - Если необходимо поднять вместе с приложением еще и clickhouse: `source docker/deploy.sh up --all`
   - Если только сам сервер: `source docker/deploy.sh up --app`


# DEV BUILD
1. `conda create -n lighthouse_server python=3.11`
2. `conda activate lighthouse_server`
3. `pip install -r requirements/dev.txt`
4. `pre-commit install` — установка прекоммитов
5. `pre-commit run --all-files` — проверка кодстайла (будет запускаться автоматически при коммитах)

Также для тестирования можно поднять свой clickhouse: `source docker/deploy.sh up --env`

Для локального тестирования использовать также `source docker/deploy.sh up --app`

Clickhouse при локальном тестировании останавливать каждый раз не нужно, поэтому используем остановку только сервера: `source docker/deploy.sh stop --app`
