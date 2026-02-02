"""
URL configuration for resource_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.urls import path
from .views import (
    CreateNewEmployee,
    role_list,
    login_view,
    skill_list,
    add_skills,
    employee_list,
    task_list,
    create_task,     
    assign_task, 
    resource_available_list_date,resource_available_list_skill,resource_available_list_task_id    
)

urlpatterns = [
    path('api/create_employee/', CreateNewEmployee, name='create-employee'),
    path('api/login_employee/', login_view, name='login-employee'),
    path('api/roles/', role_list, name='role-list'),
    path('api/skills/', skill_list, name='skill-list'),
    path('api/employees/', employee_list, name='employee-list'),
    path('api/add_skills/', add_skills, name='add-skills'),
    path('api/tasks/', task_list, name='task-list'),  
    path('api/create_task/', create_task, name='create-task'),
    path('api/assign_task/', assign_task, name='assign-task'),   
    # path('api/resource_available/', resource_available_list, name='resource-available'),
    path(
    "api/resource_available/skill/",
    resource_available_list_skill,
    name="resource_available_list_skill"
    ),
    path(
        "api/resource_available/date/",
        resource_available_list_date,
        name="resource_available_list_date"
    ),
    path(
        "api/resource_available/task/",
        resource_available_list_task_id,
        name="resource_available_list_task_id"
    )

]

