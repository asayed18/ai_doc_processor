#!/bin/bash
echo "Starting AI Document Processor Backend..."
cd backend
pipenv install
echo "Running database migrations..."
pipenv run alembic upgrade head
pipenv run python main.py