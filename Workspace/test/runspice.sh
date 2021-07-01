#!/bin/bash

# SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
start="$(date -u +%s.%N)"
ngspice -b run_control.sp -o run_log;end="$(date -u +%s.%N)"
echo $( echo "$end - $start" | bc -l )