
from rest_framework import serializers
from .models import Role,Skill,EmployeeDetails,Task

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'role']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'skill']


class EmployeeDetailsSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    skills = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeDetails
        fields = [
            'id',
            'employee_name',
            'employee_address',
            'employee_dob',
            'employee_status',
            'role',
            'skills'
        ]

    def get_skills(self, obj):
        skills = Skill.objects.filter(employeeskill__employee=obj)
        return SkillSerializer(skills, many=True).data


class TaskSerializer(serializers.ModelSerializer):
    task_assigned_to_name = serializers.CharField(
        source="task_assigned_to.employee_name",
        read_only=True
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "task_subject",
            "task_description",
            "assigned_from_date",
            "assigned_to_date",
            "task_assigned_to",
            "task_assigned_to_name"
        ]