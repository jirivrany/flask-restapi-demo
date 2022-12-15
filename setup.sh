#!/bin/bash

export FLASK_APP=app
export FLASK_ENV=development
pip install -r requirements.txt
python db_commands.py