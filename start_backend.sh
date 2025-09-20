#!/bin/bash
echo "Starting AI Document Processor Backend..."
cd backend
python -m pip install -r requirements.txt
python main.py