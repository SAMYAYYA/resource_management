# resource_project/create_random_employees.py
import os
import django
import random
import string
import pandas as pd

# ✅ Correct Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resource_project.settings')
django.setup()

from management.models import EmployeeDetails, EmployeeInfo, Role, Skill, EmployeeSkill
from django.contrib.auth.hashers import make_password

# Configuration
NUM_EMPLOYEES = 50
ROLE_EXCLUDE_ID = 1
SKILL_IDS = list(range(1, 21))  # assuming skill IDs 1 to 20 exist

# Get roles except role_id 1
roles = Role.objects.exclude(id=ROLE_EXCLUDE_ID)

employee_data_list = []

for _ in range(NUM_EMPLOYEES):
    # Random employee name
    employee_name = "Emp_" + ''.join(random.choices(string.ascii_uppercase, k=5))

    # Random username
    username = "user_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))

    # Random password
    password = ''.join(random.choices(string.ascii_letters + string.digits + "@#$!", k=8))

    # Random role
    role = random.choice(roles)

    # Create EmployeeDetails
    employee = EmployeeDetails.objects.create(
        employee_name=employee_name,
        employee_status=True,
        role=role
    )

    # Create EmployeeInfo with hashed password
    EmployeeInfo.objects.create(
        employee=employee,
        username=username,
        password=make_password(password)
    )

    # Assign 3–5 random skills
    num_skills = random.randint(3, 5)
    skills_to_assign = random.sample(SKILL_IDS, num_skills)
    for skill_id in skills_to_assign:
        skill = Skill.objects.get(id=skill_id)
        EmployeeSkill.objects.create(employee=employee, skill=skill)

    # Store data for Excel
    employee_data_list.append({
        "Employee Name": employee_name,
        "Username": username,
        "Password": password,
        "Role": role.role,
        "Skills": ', '.join([Skill.objects.get(id=s).skill for s in skills_to_assign])
    })

# Save to Excel
df = pd.DataFrame(employee_data_list)
df.to_excel("employees.xlsx", index=False)

print(f"✅ {NUM_EMPLOYEES} random employees created and saved to employees.xlsx")
