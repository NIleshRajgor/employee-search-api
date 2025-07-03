from fastapi import FastAPI, Request, HTTPException, Query
from app.common.limit_utils import is_rate_limited
from app.common.employee_utils import EmployeeSearchService
from app.common.logging_config import get_json_logger, log_json_exceptions

app = FastAPI(title="Employee Search API")
ALLOWED_STATUSES = {"active", "not started", "terminated"}
logger = get_json_logger()

@log_json_exceptions
@app.get("/resource/employees/search")
async def search(
    request: Request,
    organization_id: int = Query(..., description="Organization ID"),
    search: str = Query(None, description="Search term for first or last name"),
    status: str = Query(None, description="Employee status (active,not started,terminated)"),
    department: str = Query(None, description="Department name(ex:-AcmeCorp)"),
    position: str = Query(None, description="Job position"),
    location: str = Query(None, description="Employee location"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of results per page"),
):
    ip = request.client.host
    logger.info(f"Search requested from IP: {ip}, org_id: {organization_id}")

    if is_rate_limited(organization_id, ip):
        logger.warning(f"Rate limit exceeded for IP: {ip}, org_id: {organization_id}")
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    filters = {}
    if status:
        statuses = [s.strip().lower() for s in status.split(",")]
        invalid = [s for s in statuses if s not in ALLOWED_STATUSES]
        if invalid:
            logger.error(f"Invalid status values: {invalid}")
            raise HTTPException(
                status_code=400,
                detail=(f"Invalid status value(s): {', '.join(invalid)}. "
                        f"Allowed: {', '.join(ALLOWED_STATUSES)}"),
            )
        filters["status"] = status

    if department:
        filters["department"] = department
    if position:
        filters["position"] = position
    if location:
        filters["location"] = location
    if search:
        filters["search"] = search 

    try:
        result, total = EmployeeSearchService(organization_id, filters).run(page, page_size)
        return {
            "results": result,
            "page": page,
            "page_size": page_size,
            "total": total
        }
    except HTTPException as http_err:
        logger.error(f"HTTP error during employee search. Reason: {http_err.detail}")
        raise http_err
    except Exception as e:
        logger.error(f"Unexpected error during employee search: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        )

@app.get("/health")
def health_check():
    return {"status": "ok"}
