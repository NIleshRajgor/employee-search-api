from fastapi import HTTPException
from app.employee_data.employee_data import employees, organizations
from app.config.organization_fields_config import org_column_config
from app.common.logging_config import get_json_logger, log_json_exceptions

logger = get_json_logger()

class EmployeeSearchService:
    def __init__(self, organization_id: int, filters: dict):
        self.organization_id = organization_id
        self.filters = filters
        self.org = self._validate_organization()
        self.employees = self._get_employees_for_org()

    def _validate_organization(self):
        org = next((o for o in organizations if o.id == self.organization_id), None)
        if not org:
            logger.error(f"Organization not found: {self.organization_id}")
            raise HTTPException(
                status_code=404, detail=f"Invalid organization ID: {self.organization_id}"
            )
        logger.info(f"Organization validated: {org.name} (ID: {org.id})")
        return org

    def _get_employees_for_org(self):
        org_employees = [e for e in employees if e.organization_id == self.organization_id]
        logger.info(f"Found {len(org_employees)} employees for org ID {self.organization_id}")
        return org_employees

    def _apply_filters(self):
        result = self.employees

        # Handle name search first
        search_term = self.filters.pop("search", None)
        if search_term:
            search_term_lower = search_term.lower()
            result = [
                e for e in result
                if search_term_lower in e.first_name.lower() or search_term_lower in e.last_name.lower()
            ]
            if not result:
                logger.warning(f"No employees found matching search: {search_term}")
                raise HTTPException(
                    status_code=404,
                    detail=f"No employees found matching search: '{search_term}'"
                )

        for key, value in self.filters.items():
            if not hasattr(result[0], key):
                logger.error(f"Invalid filter field: {key}")
                raise HTTPException(
                    status_code=400, detail=f"Invalid filter field: {key}"
                )

            if key == "status":
                values = [v.strip().lower() for v in value.split(",")]
                result = [e for e in result if getattr(e, key, "").lower() in values]
            else:
                result = [e for e in result if getattr(e, key, "").lower() == value.lower()]

            if not result:
                logger.warning(f"No employees found for filter: {key} = '{value}'")
                raise HTTPException(
                    status_code=404,
                    detail=f"No employees found for filter: {key} = '{value}'",
                )
        return result

    def _format_output(self, filtered_employees):
        columns = org_column_config.get(self.organization_id)
        if not columns:
            return [e.__dict__ for e in filtered_employees]
        return [
            {col: getattr(e, col) for col in columns if hasattr(e, col)}
            for e in filtered_employees
        ]

    @log_json_exceptions
    def run(self, page: int, page_size: int):
        filtered = self._apply_filters()
        total = len(filtered)

        start = (page - 1) * page_size
        end = start + page_size
        paginated_employees = filtered[start:end]

        logger.info(f"Returning {len(paginated_employees)} out of {total} employees (Page {page})")
        return self._format_output(paginated_employees), total
