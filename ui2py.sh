#!/bin/bash

for i in *.ui; do
	pyuic5 "$i" > "${i%.ui}_ui.py"
done
