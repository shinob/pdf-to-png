#!/usr/bin/env bash

# Define the service name and the service file in the current directory
SERVICE_NAME="pdf2png.service" # This is the name systemd will use
SERVICE_FILE="pdf-to-png.service" # This is the actual file in this directory

# Get the absolute path to the service file in the current directory
SERVICE_FILE_PATH="$(pwd)/${SERVICE_FILE}"

# Define the target path for the systemd service file
SYSTEMD_SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}"

function init () {
  echo "Initializing ${SERVICE_NAME} service..."
  # Check if the service file exists in the current directory
  if [ ! -f "${SERVICE_FILE_PATH}" ]; then
    echo "Error: Service file '${SERVICE_FILE}' not found at '${SERVICE_FILE_PATH}'."
    echo "Please ensure '${SERVICE_FILE}' exists in the current directory."
    exit 1
  fi

  # Create a symbolic link to the systemd directory
  echo "Creating symbolic link from '${SERVICE_FILE_PATH}' to '${SYSTEMD_SERVICE_PATH}'..."
  sudo ln -s "${SERVICE_FILE_PATH}" "${SYSTEMD_SERVICE_PATH}"

  echo "Reloading systemd daemon..."
  sudo systemctl daemon-reload

  echo "Enabling ${SERVICE_NAME} service..."
  sudo systemctl enable "${SERVICE_NAME}"

  echo "Initialization complete. You can now start the service using '$0 start'."
}

function execute_command () {
  if [ -z "$1" ]; then
    echo "Error: No command provided."
    echo "Usage: $0 [init|start|stop|restart|status]"
    exit 1
  fi
  echo "Executing systemctl $1 ${SERVICE_NAME}..."
  sudo systemctl "$1" "${SERVICE_NAME}"
}

case "$1" in
  "init" )
    init
    ;;
  "start" | "stop" | "restart" | "status" )
    execute_command "$1"
    ;;
  "" )
    echo "Usage: $0 [init|start|stop|restart|status]"
    exit 0
    ;;
  * )
    echo "Error: Invalid command '$1'."
    echo "Usage: $0 [init|start|stop|restart|status]"
    exit 1
    ;;
esac
