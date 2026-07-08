from fastapi import APIRouter, Depends

from app.core.auth import auth_client, require_role, ROLES_CLAIM

salary_router = APIRouter(prefix="/salary", tags=["salary"])

# Dummy in-memory salary data for testing RBAC
EMPLOYEES = [
    {"id": "EMP001", "name": "Arjun Mehta", "role": "Admin", "salary": 4200000, "manager_id": None},
    {"id": "EMP003", "name": "Karthik Raja", "role": "Manager", "salary": 2800000, "manager_id": "EMP001"},
    {"id": "EMP004", "name": "Divya Krishnan", "role": "Employee", "salary": 1800000, "manager_id": "EMP003"},
    {"id": "EMP005", "name": "Rahul Nair", "role": "Employee", "salary": 1350000, "manager_id": "EMP003"},
]


@salary_router.get("/all")
async def get_all_salaries(
    auth_session=Depends(require_role("Admin")),
):
    """Only Admins can see every salary."""
    return {"employees": EMPLOYEES}


@salary_router.get("/team")
async def get_team_salaries(
    auth_session=Depends(require_role("Admin", "Manager")),
):
    """Admins and Managers can see team-level salaries."""
    user = auth_session.get("user") or {}
    return {
        "requested_by": user.get("email"),
        "employees": EMPLOYEES,  # in a real app, filter by manager_id
    }


@salary_router.get("/me")
async def get_my_salary(
    auth_session=Depends(auth_client.require_session),
):
    """Any logged-in user can see their own info (mocked lookup by email)."""
    user = auth_session.get("user") or {}
    return {
        "email": user.get("email"),
        "roles": user.get(ROLES_CLAIM, []),
        "note": "In a real app, look up this user's own salary record here.",
    }