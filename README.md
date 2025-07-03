# Employee Search API

## Overview

A search-only API for an HR system, built with FastAPI. Supports filtering employees by multiple attributes with org-level dynamic column config and in-memory data.

```
employee_search_api/
├── app/
│   ├── common/
│   │   ├── constant.py
│   │   ├── limit_utils.py
│   │   ├── employee_utils.py
│   │   ├── logging_config.py
│   ├── main.py
│   ├── config/
│   │   └── organization_fields_config.py
│   ├── employee_data/
│   │   └── employee_data.py
│   └── models/
│   │   ├── employee.py
│   │   ├── organization.py
├── tests/
│   └── mock_response/
│   │   ├── test_employees.json
│   │   └── test_limit_data.json
│   ├── test_api/
│   │   └── test_api.py
│   ├── test_commom/
│   │   ├── test_employee_utils.py
│   │   └── test_limit_utils.py
├── Dockerfile
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Features

* Filters: status, department, position, company, location
* Org-specific column configuration
* Rate limiting (no external libraries)
* Pagination support
* Strict filter-only search (no free-text)
* Containerized with Docker

---

## Setup & Run Locally

### 1. Create a virtual environment

```bash
python3 -m venv env
source env/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the API

```bash
uvicorn app.main:app --reload
```

Swagger UI: [http://localhost:8000/docs]

---

## Run with Docker

```bash
chmod +x run_docker.sh
./run_docker.sh
```

---

## Run Tests with Coverage
```bash 
chmod +x check.sh
./check.sh
```
---

## API Security

* Rate limiting is applied per IP and organization ID.
* Invalid status inputs are rejected with 400 errors.

---

## API Path

```
GET /resource/employees/search
```

Query Parameters:

* `organization_id` (required)
* `status`, `department`, `position`, `company`, `location` (optional)
* `skip`, `limit` for pagination

---

## Example Request

```bash
curl -X GET "http://localhost:8000/resource/employees/search?organization_id=1&status=active&limit=5"
```

