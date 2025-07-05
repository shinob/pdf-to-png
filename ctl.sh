#!/usr/bin/env bash

function init () {
  echo "Initializing pdf-to-png service..."
  sudo ln -s /var/www/pdf-to-png/pdf-to-png.service /etc/systemd/system/pdf2png.service
  sudo systemctl daemon-reload
  sudo systemctl enable pdf2png.service
  echo "Initialization complete. You can now start the service using 'ctl.sh start'."
}

function execute_command () {
  if [ -z "$1" ]; then
    echo "Error: No command provided."
    echo "Usage: $0 [init|start|stop|restart|status]"
    exit 1
  fi
  echo "Executing systemctl $1 pdf2png.service..."
  sudo systemctl "$1" pdf2png.service
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