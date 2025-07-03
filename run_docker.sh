#!/bin/bash

echo " Stopping any existing container..."
docker stop employee_search_container 2>/dev/null
docker rm employee_search_container 2>/dev/null

echo " Building Docker image..."
docker build -t employee-search .

echo " Running Docker container..."
docker run -d -p 8000:8000 --name employee_search_container employee-search

echo " Your API is live at: http://localhost:8000/docs"
