#!/bin/bash

count=0
started=false

while [ $count -lt 3 ] && [ "$started" = false ]; do
  ((count++))
  echo "[$STAGE_NAME] Starting container [Attempt: $count]"

  testStart=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000)

  if [ "$testStart" -eq 200 ]; then
    started=true
  else
    sleep 1
  fi
done

if [ "$count" = 3 ]; then
  exit 1
fi
