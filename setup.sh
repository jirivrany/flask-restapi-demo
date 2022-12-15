#!/bin/bash

export FLASK_APP=app
export FLASK_DEBUG=True
pip install -r requirements.txt
python db_commands.py