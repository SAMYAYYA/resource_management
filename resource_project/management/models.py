from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q, F


class Role(models.Model):
    role = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.role

    

class Skill(models.Model):
    skill = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.skill

    

class EmployeeDetails(models.Model):
    employee_name = models.CharField(max_length=100)
    employee_address = models.TextField(null=True, blank=True)
    employee_dob = models.DateField(null=True, blank=True)
    employee_status = models.BooleanField(default=True)


    role = models.ForeignKey(
        Role,
        on_delete=models.RESTRICT,
        related_name="employees"
    )

    def __str__(self):
        return self.employee_name

    


class EmployeeSkill(models.Model):
    employee = models.ForeignKey(EmployeeDetails, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('employee', 'skill')

    def __str__(self):
        return f"{self.employee} - {self.skill}"

    


class Task(models.Model):
    task_subject = models.CharField(max_length=200)
    task_description = models.TextField(null=True, blank=True)
    assigned_from_date = models.DateField(null=True, blank=True)
    assigned_to_date = models.DateField(null=True, blank=True)    
    dead_line = models.DateField()  

    task_assigned_to = models.ForeignKey(
        EmployeeDetails,
        on_delete=models.RESTRICT,
        related_name="tasks",
        null=True,    
        blank=True
    )

    required_skills = models.ManyToManyField(
        Skill,
        related_name="tasks",
        blank=True
    )

    def clean(self):
        if self.assigned_from_date and self.assigned_to_date:
            if self.assigned_from_date > self.assigned_to_date:
                raise ValidationError("From date cannot be after To date")
        if self.dead_line and self.assigned_to_date:
            if self.dead_line < self.assigned_to_date:
                raise ValidationError("Deadline cannot be before assigned_to_date")

    def __str__(self):
        return self.task_subject




class EmployeeInfo(models.Model):
    employee = models.OneToOneField(
        EmployeeDetails,
        on_delete=models.CASCADE,
        related_name="login_info"
    )
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    login_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username
    
    @property
    def is_authenticated(self):
        # DRF/permissions uses this
        return True


class ErrorLog(models.Model):
    api_name = models.CharField(max_length=100)

    user = models.CharField(max_length=100, null=True, blank=True)

    error_message = models.TextField()
    request_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.api_name} - user:{self.user_id}"

class ApiHistory(models.Model):
    user_id = models.IntegerField(null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)

    api_name = models.CharField(max_length=200)
    method = models.CharField(max_length=10)

    request_data = models.JSONField(null=True, blank=True)
    response_data = models.JSONField(null=True, blank=True)

    status_code = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)



    def __str__(self):
        return f"{self.api_name} | {self.method} | {self.status_code}"
