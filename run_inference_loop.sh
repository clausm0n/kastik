#!/bin/bash

LOG_FILE="inference.log"

while true; do
    output=$(python run_inference.py)
    echo -ne "$output\r"
    echo "$output" >> "$LOG_FILE"
    sleep 15
done
