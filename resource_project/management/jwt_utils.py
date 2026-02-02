from jose import jwt
from datetime import datetime, timedelta
from django.contrib.auth.hashers import check_password
from .models import EmployeeInfo,EmployeeDetails

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def authenticate_employee(username: str, password: str):
    try:
        login_user = EmployeeInfo.objects.get(username=username)
    except EmployeeInfo.DoesNotExist:
        return None

    print("login_user object:", login_user)                     # Full EmployeeInfo object
    print("login_user.id:", login_user.id)
    print("login_user.username:", login_user.username)
    print("login_user.password (hashed):", login_user.password)
    print("login_user.employee:", login_user.employee)          # EmployeeDetails object
    print("login_user.employee.employee_name:", login_user.employee.employee_name)
    print("login_user.employee.role:", login_user.employee.role)  # Role object
    print("login_user.employee.role.id:", login_user.employee.role.id)
    print("login_user.employee.role.role:", login_user.employee.role.role)

    if check_password(password, login_user.password):
        return {
            "user_name": login_user.username,
            "user_id":login_user.id,
            "employee_name":login_user.employee.employee_name,
            "role_id": login_user.employee.role.id,
            "role_name": login_user.employee.role.role
        }

    return None


def authenticate_employee_FK(username: str, password: str):
    try:
        user = EmployeeInfo.objects.select_related('employee__role').get(username=username)
    except EmployeeInfo.DoesNotExist:
        return None

    if check_password(password, user.password):
        return {
            "user": user,
            "role_id": user.employee.role.id,
            "role_name": user.employee.role.role
        }

    return None

def authenticate_employee_old(username: str, password: str):
    try:
        user = EmployeeInfo.objects.get(username=username)

        role_id=EmployeeDetails.objects.get(employee_name=user.username)

    except EmployeeInfo.DoesNotExist:
        return None

    if check_password(password, user.password):
        return user
    return None


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
