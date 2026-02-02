from django.contrib.auth.hashers import make_password
from django.db import IntegrityError, transaction
from django.db.models import Count

from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from rest_framework.response import Response

from datetime import datetime



from .models import EmployeeDetails, EmployeeInfo, Role,Skill,EmployeeSkill,Task,ErrorLog

from .authentication import IsManager

from .jwt_utils import authenticate_employee, create_access_token, create_refresh_token

from .serializers import RoleSerializer,SkillSerializer,EmployeeDetailsSerializer,TaskSerializer


from .utils import ApiHistory




@api_view(['POST'])
@authentication_classes([])  
@permission_classes([AllowAny])  
def login_view(request):
    try :
        username = request.data.get('username')
        password = request.data.get('password')

        authenticate_employee_user = authenticate_employee(username, password)

        print("user : " , authenticate_employee_user)
        if not authenticate_employee_user:
            return Response({"error": "Invalid credentials"}, status=401)

        # payload = {
        #     "user_id": authenticate_employee_user['user'].id,
        #     "username": authenticate_employee_user['user'].username
        # }



        payload = authenticate_employee_user
        print("payload : ",payload)
        return Response({
            "access": create_access_token(payload),
            "refresh": create_refresh_token(payload)
        })
    except Exception as e:
            ErrorLog.objects.create(
                api_name="Create_employee",
                user=request.user,
                error_message=str(e),
                request_data=request.GET.dict()
            )

            return Response(
                {"error": "Internal Server Error"},
                status=500
            )



@api_view(['POST'])
@permission_classes([IsAuthenticated, IsManager])
def CreateNewEmployee(request):
    data = request.data
    user = request.user

    if user.employee.role.role.lower() != "manager":
        return Response({"error": "Only managers can create employees"}, status=403)

    if not data:
        return Response({"error": "Request payload is empty"}, status=400)

    required_fields = ['employee_name', 'username', 'password', 'role_id', 'skills']
    missing_fields = [f for f in required_fields if f not in data]
    if missing_fields:
        return Response(
            {"error": f"Missing required fields: {', '.join(missing_fields)}"},
            status=400
        )

    try:
        with transaction.atomic():

            role = Role.objects.get(id=data['role_id'])

            skill_ids = data.get('skills', [])
            if not isinstance(skill_ids, list) or not skill_ids:
                return Response({"error": "Provide a non-empty list of skill IDs"}, status=400)

            skills = Skill.objects.filter(id__in=skill_ids)
            if skills.count() != len(skill_ids):
                return Response({"error": "One or more skill IDs are invalid"}, status=400)

            employee = EmployeeDetails.objects.create(
                employee_name=data['employee_name'],
                employee_address=data.get('employee_address', ''),
                employee_dob=data.get('employee_dob'),
                employee_status=data.get('employee_status', True),
                role=role
            )

            for skill in skills:
                EmployeeSkill.objects.create(employee=employee, skill=skill)

            user = EmployeeInfo.objects.create(
                employee=employee,
                username=data['username'],
                password=make_password(data['password'])
            )

    except Role.DoesNotExist:
        return Response({"error": "Role not found"}, status=400)

    except IntegrityError:
        return Response(
            {"error": "Username already exists"},
            status=400
        )

    except Exception as e:
            ErrorLog.objects.create(
                api_name="Create_employee",
                user=request.user,
                error_message=str(e),
                request_data=request.GET.dict()
            )

            return Response(
                {"error": "Internal Server Error"},
                status=500
            )

   
    return Response({
        "message": "Employee created successfully",
        "employee_id": employee.id,
        "username": user.username
    }, status=201)


# Protected API
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsManager])
def CreateNewEmployeee(request):

    try:
        data = request.data

        user=request.user

        print("data , user , ",data,user)

        
        if user.employee.role.role.lower() != "manager":
            return Response({"error": "Only managers can create employees"}, status=403)
        
        
        if not data:
            return Response({"error": "Request payload is empty"}, status=400)

        required_fields = ['employee_name', 'username', 'password', 'role_id','skills']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                status=400
            )

        try:
            role = Role.objects.get(id=data['role_id'])
        except Role.DoesNotExist:
            return Response({"error": "Role not found"}, status=400)

        skill_ids = data.get('skills', [])
        if not isinstance(skill_ids, list) or not skill_ids:
            return Response({"error": "Please provide a non-empty list of skill IDs"}, status=400)

        existing_skills = Skill.objects.filter(id__in=skill_ids)
        if existing_skills.count() != len(skill_ids):
            return Response({"error": "One or more skill IDs are invalid"}, status=400)

        
        employee = EmployeeDetails.objects.create(
            employee_name=data['employee_name'],
            employee_address=data.get('employee_address', ''),
            employee_dob=data.get('employee_dob', None),
            employee_status=data.get('employee_status', True),
            role=role
        )

        for skill in existing_skills:
            EmployeeSkill.objects.create(employee=employee, skill=skill)

        hashed_password = make_password(data['password'])
        user = EmployeeInfo.objects.create(
            employee=employee,
            username=data['username'],
            password=hashed_password
        )

        return Response({
            "message": "Employee created successfully",
            "employee_id": employee.id,
            "username": user.username
        }, status=201)

    except Exception as e:
        ErrorLog.objects.create(
            api_name="Create_employeee",
            error_message=str(e),
            request_data=request.GET.dict()
        )

        return Response(
            {"error": "Internal Server Error"},
            status=500
        )



@api_view(['GET'])
@permission_classes([IsAuthenticated, IsManager])
def role_list(request):
    roles = Role.objects.all()
    serializer = RoleSerializer(roles, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsManager])
def skill_list(request):
    roles = Skill.objects.all()
    serializer = SkillSerializer(roles, many=True)
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated, IsManager])
def employee_list(request):
    roles = EmployeeDetails.objects.all()
    serializer = EmployeeDetailsSerializer(roles, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_skills_old(request):
    """
    Add skills from a list.
    Expected payload: {"skills": ["Python", "AI", "Django"]}
    """

    data =request.data

    skill_ids = request.data.get('skills', [])

    if not isinstance(skill_ids, list) or not skill_ids:
        return Response({"error": "Please provide a non-empty list of skills"}, status=400)
    
    existing_skills = Skill.objects.filter(id__in=skill_ids)
    if existing_skills.count() != len(skill_ids):
        return Response({"error": "One or more skill IDs are invalid"}, status=400)

    added_skills = []
    already_exist = []

    for skill_id in skill_ids:
        if not skill_id:
            continue

        _, created = EmployeeSkill.objects.get_or_create(employee=data['user_id'],skill=skill_id)
        if created:
            added_skills.append(skill_id)
        else:
            already_exist.append(skill_id)

    return Response({
        "added_skills": added_skills,
        "already_exist": already_exist,
        "message": f"{len(added_skills)} new skills added."
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsManager])
def add_skills(request):
    try:

        data = request.data
        print("Request user is  : ",request.user)
        employee_id = data.get('employee_id')
        skill_ids = data.get('skills', [])

        if not employee_id:
            return Response({"error": "employee_id is required"}, status=400)

        try:
            employee = EmployeeDetails.objects.get(id=employee_id)
        except EmployeeDetails.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)

        if not isinstance(skill_ids, list) or not skill_ids:
            return Response({"error": "Provide non-empty skill list"}, status=400)

        skills = Skill.objects.filter(id__in=skill_ids)
        if skills.count() != len(skill_ids):
            return Response({"error": "One or more skill IDs invalid"}, status=400)

        added = []
        already = []

        for skill in skills:
            obj, created = EmployeeSkill.objects.get_or_create(
                employee=employee,
                skill=skill
            )
            if created:
                added.append(skill.id)
            else:
                already.append(skill.id)

        return Response({
            "added_skills": added,
            "already_exist": already
        }, status=200)
    
    except Exception as e:
        ErrorLog.objects.create(
            api_name="add_skills",
            user=request.user,
            error_message=str(e),
            request_data=request.GET.dict()
        )

        return Response(
            {"error": "Internal Server Error"},
            status=500
        )



@api_view(['GET'])
@permission_classes([IsAuthenticated, IsManager])
def task_list(request):
    tasks = Task.objects.select_related("task_assigned_to").all()
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def employee_tasks(request, employee_id):
    tasks = Task.objects.filter(task_assigned_to_id=employee_id)
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsManager])
def resource_available_list_skill(request):
    """
    Get employees free between from_date and to_date.
    Optional: filter by skills (partial or full match).
    """

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    skills_param = request.GET.get("skills", "")  # optional

    if not from_date or not to_date:
        return Response({"error": "from_date and to_date are required"}, status=400)

    skill_ids = [int(s) for s in skills_param.split(",") if s.isdigit()]
    

    print("to_date : ",to_date)
    print("from_date : ",from_date)
    # busy_employee_ids = Task.objects.filter(
    #     assigned_from_date__lte=to_date,
    #     assigned_to_date__gte=from_date
    # ).values_list("task_assigned_to_id", flat=True)

    busy_employee_ids = Task.objects.filter(
    task_assigned_to__isnull=False,
    assigned_from_date__lte=to_date,
    assigned_to_date__gte=from_date
    ).values_list("task_assigned_to_id", flat=True)

    print("busy_employee_ids ",busy_employee_ids)

    free_employees = EmployeeDetails.objects.exclude(
        id__in=busy_employee_ids
    ).exclude(
        role_id=1   # remove managers
    )


    message = "Employees free in given time range"

    if skill_ids:
        # full_match = free_employees.filter(
        #     employeeskill__skill_id__in=skill_ids
        # ).annotate(
        #     skill_count=Count("employeeskill__skill_id", distinct=True)
        # ).filter(skill_count=len(skill_ids))

        skill_filtered = free_employees.filter(
            employeeskill__skill_id__in=skill_ids
        )
        # print("skill_filtered:")
        # for emp in skill_filtered:
        #     print(emp.id, emp.employee_name, emp.role.role)

        skill_annotated = skill_filtered.annotate(
            skill_count=Count("employeeskill__skill_id", distinct=True)
        )
        # print("skill_annotated:")
        # for emp in skill_annotated:
        #     print(emp.id, emp.employee_name, emp.role.role, emp.skill_count)

        full_match = skill_annotated.filter(
            skill_count=len(skill_ids)
        )
        # print("full_match:")
        # for emp in full_match:
        #     print(emp.id, emp.employee_name, emp.role.role, emp.skill_count)


        if full_match.exists():
            free_employees = full_match
            message += f" with all {len(skill_ids)} required skills"
        else:
            partial_match = free_employees.filter(
                employeeskill__skill_id__in=skill_ids
            ).annotate(
                matched_skills=Count("employeeskill__skill_id", distinct=True)
            ).order_by("-matched_skills")

            free_employees = partial_match
            message += " with partial skill match"

        serializer = EmployeeDetailsSerializer(free_employees, many=True)

        return Response({
            "message": message,
            "total": free_employees.count(),
            "employees": serializer.data
        })
    
    return Response({
            "message": "No Employee's are not available "
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsManager])
def resource_available_list_date(request):
    """
    Get employees free between from_date and to_date.
    Optional: filter by skills (partial or full match).
    """

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    if not from_date or not to_date:
        return Response({"error": "from_date and to_date are required"}, status=400)

    print("to_date : ",to_date)
    print("from_date : ",from_date)

    busy_employee_ids = Task.objects.filter(
    task_assigned_to__isnull=False,
    assigned_from_date__isnull=False,
    assigned_to_date__isnull=False,
    assigned_from_date__lte=to_date,
    assigned_to_date__gte=from_date
    ).values_list("task_assigned_to_id", flat=True)

    # free_employees = EmployeeDetails.objects.exclude(id__in=busy_employee_ids)

    free_employees = EmployeeDetails.objects.exclude(
        id__in=busy_employee_ids
    ).exclude(
        role_id=1   # remove managers
    )

    message = "Employees free in given time range"

    serializer = EmployeeDetailsSerializer(free_employees, many=True)

    return Response({
        "message": message,
        "total": free_employees.count(),
        "employees": serializer.data
    })




@api_view(['GET'])
@permission_classes([IsAuthenticated, IsManager])
def resource_available_list_task_id(request):
    """
    Get employees free between from_date and to_date
    AND matching required skills of a task
    """

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    task_id = request.GET.get("task_id")

    if not from_date or not to_date or not task_id:
        return Response(
            {"error": "from_date, to_date and task_id are required"},
            status=400
        )

    busy_employee_ids = Task.objects.filter(
        task_assigned_to__isnull=False,
        assigned_from_date__isnull=False,
        assigned_to_date__isnull=False,
        assigned_from_date__lte=to_date,
        assigned_to_date__gte=from_date
    ).values_list("task_assigned_to_id", flat=True)

    free_employees = EmployeeDetails.objects.exclude(id__in=busy_employee_ids)

    message = "Employees free in given time range"

    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({"error": "Invalid task_id"}, status=404)

    print("task resource_available_list_task_id : ",task)

    skill_ids = list(task.required_skills.values_list("id", flat=True))

    print("skill_ids resource_available_list_task_id : ",skill_ids)

    if skill_ids:
        skill_filtered = free_employees.filter(
            employeeskill__skill_id__in=skill_ids
        )

        skill_annotated = skill_filtered.annotate(
            skill_count=Count("employeeskill__skill_id", distinct=True)
        )

        full_match = skill_annotated.filter(
            skill_count=len(skill_ids)
        )

        if full_match.exists():
            free_employees = full_match
            message += f" with all {len(skill_ids)} required skills"
        else:
            free_employees = free_employees.filter(
                employeeskill__skill_id__in=skill_ids
            ).annotate(
                matched_skills=Count("employeeskill__skill_id", distinct=True)
            ).order_by("-matched_skills")

            message += " with partial skill match"

        serializer = EmployeeDetailsSerializer(free_employees, many=True)

        return Response({
            "message": message,
            "total": free_employees.count(),
            "employees": serializer.data
        })
    return Response({
            "message": "For this Task No required Skills "
        })



@api_view(['POST'])
@permission_classes([IsAuthenticated, IsManager])
def create_task(request):
    """
    Create a task template with a deadline but no assignment yet.
    Payload:
    {
        "task_subject": "Build Dashboard",
        "task_description": "Develop analytics dashboard",
        "dead_line": "2026-02-15"
    }
    """

    try:

        data = request.data

        required_fields = ['task_subject', 'dead_line','required_skills']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return Response({"error": f"Missing fields: {', '.join(missing_fields)}"}, status=400)

        # Validate deadline
        try:
            dead_line = datetime.strptime(data['dead_line'], "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Invalid date format for dead_line, use YYYY-MM-DD"}, status=400)

        skill_ids = data.get('required_skills')

        if not isinstance(skill_ids, list):
            return Response(
                {"error": "required_skills must be a list of skill IDs"},
                status=400
            )

        valid_skills = Skill.objects.filter(id__in=skill_ids)
        if valid_skills.count() != len(skill_ids):
            return Response(
                {"error": "One or more skill IDs are invalid"},
                status=400
            )

        # ---------- ATOMIC SAVE ----------
        with transaction.atomic():
            task = Task.objects.create(
                task_subject=data['task_subject'],
                task_description=data.get('task_description', ''),
                dead_line=dead_line
            )

            task.required_skills.set(valid_skills)

        return Response(
            {
                "message": "Task created successfully",
                "task_id": task.id
            },
            status=201
        )
    
    except Exception as e:
            ErrorLog.objects.create(
                api_name="create_task",
                user=request.user,
                error_message=str(e),
                request_data=request.GET.dict()
            )

            return Response(
                {"error": "Internal Server Error"},
                status=500
            )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsManager])
def assign_task(request):
    """
    Assign an existing task to an employee with a date range.
    Payload:
    {
        "task_id": 1,
        "employee_id": 5,
        "assigned_from_date": "2026-02-01",
        "assigned_to_date": "2026-02-05"
    }
    """

    try:
        data = request.data

        required_fields = ['task_id', 'employee_id', 'assigned_from_date', 'assigned_to_date']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return Response({"error": f"Missing fields: {', '.join(missing_fields)}"}, status=400)

        
        try:
            task = Task.objects.get(id=data['task_id'])
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=404)

        
        try:
            employee = EmployeeDetails.objects.get(id=data['employee_id'])
        except EmployeeDetails.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)

        
        try:
            from_date = datetime.strptime(data['assigned_from_date'], "%Y-%m-%d").date()
            to_date = datetime.strptime(data['assigned_to_date'], "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Invalid date format, use YYYY-MM-DD"}, status=400)

        
        if from_date > to_date:
            return Response({"error": "assigned_from_date cannot be after assigned_to_date"}, status=400)

        
        overlapping_tasks = Task.objects.filter(
            task_assigned_to=employee,
            assigned_from_date__lte=to_date,
            assigned_to_date__gte=from_date
        )
        if overlapping_tasks.exists():
            return Response({"error": f"Employee is busy in this date range"}, status=400)

        
        task.task_assigned_to = employee
        task.assigned_from_date = from_date
        task.assigned_to_date = to_date
        task.save()

        return Response({
            "message": "Task assigned successfully",
            "task_id": task.id,
            "employee_id": employee.id
        }, status=200)

    except Exception as e:
            ErrorLog.objects.create(
                api_name="Assign_task",
                error_message=str(e),
                request_data=request.GET.dict()
            )

            return Response(
                {"error": "Internal Server Error"},
                status=500
            )


