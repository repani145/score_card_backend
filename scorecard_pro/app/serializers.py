# from rest_framework import serializers
# from .models import Employee
# from .validators import validate_employee_id

# class EmployeeSerializer(serializers.ModelSerializer):
#     employee_id = serializers.CharField(validators=[validate_employee_id])

#     class Meta:
#         model = Employee
#         fields = ['employee_id', 'full_name', 'department', 'position']