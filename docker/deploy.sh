#!/bin/bash

ACTION=$1
OPTION=$2
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

cleanup() {
  echo "Removing old containers and images..."
  docker system prune -f
  if [ $? -ne 0 ]; then
    echo "${RED}ERROR:${NC} Failed to clean up Docker resources. Exiting..."
  else
    echo "${GREEN}SUCCESS:${NC} Cleanup completed."
  fi
}

start_app() {
  echo "Starting docker with app..."
  docker-compose --env-file .env -f docker/docker-compose.app.yml up --build -d
  if [ $? -ne 0 ]; then
    echo "${RED}ERROR:${NC} Failed to start the app. Exiting..."
  else
    echo "${GREEN}SUCCESS:${NC} App has been started."
  fi
}

start_env() {
  echo "Starting docker containers with all environment: clickhouse..."
  docker-compose --env-file .env -f docker/docker-compose.env.yml up --build -d
  if [ $? -ne 0 ]; then
    echo "${RED}ERROR:${NC} Failed to start the environment. Exiting..."
  else
    echo "${GREEN}SUCCESS:${NC} Environment has been started."
  fi
}

stop_app() {
  echo "Stopping app..."
  docker-compose --env-file .env -f docker/docker-compose.app.yml down
  if [ $? -ne 0 ]; then
    echo "${RED}ERROR:${NC} Failed to stop app..."
  else
    echo "${GREEN}SUCCESS:${NC} App has been stopped."
  fi
}

stop_env() {
  echo "Stopping containers with environment..."
  docker-compose --env-file .env -f docker/docker-compose.env.yml down
  if [ $? -ne 0 ]; then
    echo "${RED}ERROR:${NC} Failed to stop containers with environment..."
  else
    echo "${GREEN}SUCCESS:${NC} Environment has been stopped."
  fi
}

case $ACTION in
  up)
    case $OPTION in
      --app)
        start_app
        ;;
      --env)
        start_env
        ;;
      --all)
        start_env
        start_app
        ;;
      *)
        echo "${RED}INVALID OPTION.${NC} Usage: $0 up {--app|--env|--all}"
        ;;
    esac
    ;;
  stop)
    case $OPTION in
      --app)
        stop_app
        ;;
      --env)
        stop_env
        ;;
      --all)
        stop_app
        stop_env
        ;;
      *)
        echo "${RED}INVALID OPTION.${NC} Usage: $0 stop {--app|--env|--all}"
        ;;
    esac
    ;;
  clean)
    cleanup
    ;;
  *)
    echo "${RED}INVALID COMMAND.${NC} Usage: $0 {up|stop|clean} [--app|--env|--all]"
    ;;
esac
