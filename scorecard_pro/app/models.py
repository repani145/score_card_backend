from django.db import models
from authentication.models import CustomUser

class Employee(models.Model):
    employee_id = models.CharField(max_length=10, unique=True)
    full_name = models.CharField(max_length=255)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)

    class Meta:
        db_table = "employees"

    def __str__(self):
        return f"{self.employee_id} - {self.full_name}"

class EmployeeMetrics(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, unique=True)
    hrs_wrkd_per_week = models.IntegerField(null=False, blank=False)
    tasks_completed = models.IntegerField(null=False, blank=False)
    sales_made = models.IntegerField(null=False, blank=False)
    productivity_score = models.FloatField(default=0.0, blank=False)

    error_rate = models.IntegerField(null=False, blank=False)
    customer_rating = models.FloatField(null=False, blank=False)
    returns_or_complaints = models.IntegerField(null=False, blank=False)
    quality_score = models.FloatField(default=0.0, blank=False)

    deadlines_met = models.IntegerField(null=False, blank=False)
    total_deadlines = models.IntegerField(null=False, blank=False)
    project_cmple_times = models.IntegerField(null=False, blank=False)
    target_cmple_times = models.IntegerField(null=False, blank=False)
    timeliness_score = models.FloatField(default=0.0, blank=False)

    final_score = models.FloatField(default=0.0, blank=False)

    class Meta:
        db_table = "employee_metrics"

    def save(self, *args, **kwargs):
        # Productivity Score
        if self.hrs_wrkd_per_week > 0:
            tasks_per_hour = (self.tasks_completed / self.hrs_wrkd_per_week) * 100
            sales_efficiency = (self.sales_made / self.hrs_wrkd_per_week) * 100
            self.productivity_score = ((tasks_per_hour + sales_efficiency) / 2)
            print('productivity_score = ',self.productivity_score)
        else:
            self.productivity_score = 0  

        # Quality Score
        error_score = 100 - self.error_rate  
        customer_feedback = self.customer_rating * 20  
        complaint_rate = 100 - ((self.returns_or_complaints / self.tasks_completed) * 100) if self.tasks_completed else 100
        self.quality_score = (error_score + customer_feedback + complaint_rate) / 3  
        print('quality_score = ',self.quality_score)

        # Timeliness Score
        deadlines_met_percentage = (self.deadlines_met / self.total_deadlines) * 100 if self.total_deadlines else 0
        completion_efficiency = (self.target_cmple_times / self.project_cmple_times) * 100 if self.project_cmple_times else 100
        self.timeliness_score = (deadlines_met_percentage + completion_efficiency) / 2  
        print('timeliness_score = ',self.timeliness_score)

        # Final Score Calculation (Using Weights)
        PRODUCTIVITY_WEIGHT = 0.4
        QUALITY_WEIGHT = 0.3
        TIMELINESS_WEIGHT = 0.3

        self.final_score = (
            (self.productivity_score * PRODUCTIVITY_WEIGHT) +
            (self.quality_score * QUALITY_WEIGHT) +
            (self.timeliness_score * TIMELINESS_WEIGHT)
        )

        super().save(*args, **kwargs)



class ReportLog(models.Model):
    email = models.EmailField()
    category = models.CharField(max_length=50)
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.category} - {self.datetime}"