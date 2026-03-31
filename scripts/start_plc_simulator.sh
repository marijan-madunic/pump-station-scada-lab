#!/bin/bash

echo "Starting PLC simulator..."

cd ../plc || exit
python3 plc_simulator.py
