#!/bin/bash

set -e

# make sure your create env name will be 'env'
# if your env name is diff then change is source replace 'env' to 'your_env_name'
source env/bin/activate

export PYTHONPATH=$(pwd)

echo " Running tests with coverage..."

pytest --cov=app --cov-report=term --cov-report=html tests/

echo ""
echo " Tests complete. Coverage report generated:"
echo " Console summary above"
echo " Full HTML report: file://$(pwd)/htmlcov/index.html"
