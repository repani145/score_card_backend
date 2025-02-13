from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils.timezone import now
from django.core.mail import EmailMessage
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError

from django.db import IntegrityError, DatabaseError

from authentication.models import CustomUser
from .models import Employee, EmployeeMetrics, ReportLog

import csv
import json
import pandas as pd
from io import BytesIO
from openpyxl import Workbook

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet



class EmployeeMetricsSerializer(serializers.ModelSerializer):
    hrs_wrkd_per_week = serializers.IntegerField(
        required=True, allow_null=False,
        error_messages={
            "required": "Hours worked per week is required",
            "null": "Hours worked per week cannot be null",
        }
    )
    tasks_completed = serializers.IntegerField(
        required=True, allow_null=False,
        error_messages={
            "required": "Tasks completed is required",
            "null": "Tasks completed cannot be null",
        }
    )
    sales_made = serializers.IntegerField(
        required=True, allow_null=False,
        error_messages={
            "required": "Sales made is required",
            "null": "Sales made cannot be null",
        }
    )
    error_rate = serializers.IntegerField(
        required=True, allow_null=False,
        error_messages={
            "required": "Error rate is required",
            "null": "Error rate cannot be null",
        }
    )
    customer_rating = serializers.FloatField(
        required=True, allow_null=False,
        error_messages={
            "required": "Customer rating is required",
            "null": "Customer rating cannot be null",
        }
    )
    returns_or_complaints = serializers.IntegerField(
        required=True, allow_null=False,
        error_messages={
            "required": "Returns or complaints is required",
            "null": "Returns or complaints cannot be null",
        }
    )
    deadlines_met = serializers.IntegerField(
        required=True, allow_null=False,
        error_messages={
            "required": "Deadlines met is required",
            "null": "Deadlines met cannot be null",
        }
    )
    total_deadlines = serializers.IntegerField(
        required=True, allow_null=False,
        error_messages={
            "required": "Total deadlines is required",
            "null": "Total deadlines cannot be null",
        }
    )
    project_cmple_times = serializers.IntegerField(
        required=True, allow_null=False,
        error_messages={
            "required": "Project completion times is required",
            "null": "Project completion times cannot be null",
        }
    )
    target_cmple_times = serializers.IntegerField(
        required=True, allow_null=False,
        error_messages={
            "required": "Target completion times is required",
            "null": "Target completion times cannot be null",
        }
    )

    class Meta:
        model = EmployeeMetrics
        fields = [
            "hrs_wrkd_per_week", "tasks_completed", "sales_made",
            "error_rate", "customer_rating", "returns_or_complaints",
            "deadlines_met", "total_deadlines", "project_cmple_times",
            "target_cmple_times"
        ]


class EmployeeMetricsSerializerForFilter(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    productivity_score = serializers.FloatField()
    quality_score = serializers.FloatField()
    timeliness_score = serializers.FloatField()
    total_score = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeMetrics
        fields = ['employee_name', 'productivity_score', 'quality_score', 'timeliness_score', 'total_score']

    def get_employee_name(self, obj):
        return obj.employee.full_name if obj.employee else "Unknown"

    def get_total_score(self, obj):
        return obj.final_score  # Renaming final_score to total_score


class EmployeeSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(
        required=True, allow_null=False, allow_blank=False, 
        error_messages={
            "required": "Employee ID is a required field",
            "null": "Employee ID cannot be null",
            "blank": "Employee ID cannot be empty"
        }
    )
    full_name = serializers.CharField(
        required=True, allow_null=False, allow_blank=False, 
        error_messages={
            "required": "Full name is a required field",
            "null": "Full name cannot be null",
            "blank": "Full name cannot be empty"
        }
    )
    department = serializers.CharField(
        required=True, allow_null=False, allow_blank=False, 
        error_messages={
            "required": "Department is a required field",
            "null": "Department cannot be null",
            "blank": "Department cannot be empty"
        }
    )
    position = serializers.CharField(
        required=True, allow_null=False, allow_blank=False, 
        error_messages={
            "required": "Position is a required field",
            "null": "Position cannot be null",
            "blank": "Position cannot be empty"
        }
    )

    class Meta:
        model = Employee
        fields = ['employee_id', 'full_name', 'department', 'position']

def get_tokens_for_user(user: CustomUser):
    token = RefreshToken.for_user(user)
    token["full_name"] = user.full_name
    token["email"] = user.email
    token["mobile"] = user.mobile
    token['user_type'] = user.user_type
    # token['uuid'] = user.uuid
    # print('expiry time', token.access_token['exp'])
    return {
        'refresh': str(token),
        'access': str(token.access_token),
        'expiry_time': (token.access_token['exp'] * 1000)
    }

# Create your views here.
class EmployeeMetricsView(APIView):
    def get(self, request):
        metrics = EmployeeMetrics.objects.select_related('employee').all()

        data = [
            {
                "employee_id": metric.employee.id,
                "employee_name": metric.employee.full_name,
                "productivity_score": metric.productivity_score,
                "quality_score": metric.quality_score,
                "timeliness_score": metric.timeliness_score,
                "total_score": metric.final_score,
            }
            for metric in metrics
        ]

        return Response({"success": 1, "message": "Employee metrics retrieved", "data": data}, status=status.HTTP_200_OK)

#for dashboard
class MetricsSummaryView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self, request):
        metrics = EmployeeMetrics.objects.all()

        total_scores = []
        category_scores = {"productivity": [], "quality": [], "timeliness": []}

        for metric in metrics:
            total_scores.append(metric.final_score)
            category_scores["productivity"].append(metric.productivity_score)
            category_scores["quality"].append(metric.quality_score)
            category_scores["timeliness"].append(metric.timeliness_score)

        summary = {
            "average_total_score": sum(total_scores) / len(total_scores) if total_scores else 0,
            "category_breakdown": {
                "productivity": sum(category_scores["productivity"]) / len(category_scores["productivity"]) if category_scores["productivity"] else 0,
                "quality": sum(category_scores["quality"]) / len(category_scores["quality"]) if category_scores["quality"] else 0,
                "timeliness": sum(category_scores["timeliness"]) / len(category_scores["timeliness"]) if category_scores["timeliness"] else 0
            }
        }

        return Response({"success": 1, "message": "Metrics summary retrieved", "data": summary}, status=status.HTTP_200_OK)

#for dashboard
class TopScoredEmployeesView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self, request):
        top_employees = EmployeeMetrics.objects.select_related('employee').order_by('-final_score')[:10]

        data = [
            {
                "employee_id": emp.employee.id,
                "employee_name": emp.employee.full_name,
                "final_score": emp.final_score,
                "productivity_score": emp.productivity_score,
                "quality_score": emp.quality_score,
                "timeliness_score": emp.timeliness_score,
            }
            for emp in top_employees
        ]

        return Response({"success": 1, "message": "Top 10 employees retrieved", "data": data}, status=status.HTTP_200_OK)



# to add single employee
class EmployeeCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            print(request.data)

            serializer = EmployeeSerializer(data=request.data)
            if serializer.is_valid():
                y = serializer.save()
                # print('serializer.save() ===>>',y.id)
                return Response(
                    {
                        "success": 1,
                        "message": "Employee added successfully",
                        "data": serializer.data,
                        "employee_id":y.id
                    },
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                {
                    "success": 0,
                    "message": "Validation failed",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except ValidationError as e:
            return Response(
                {"success": 0, "message": "Validation error", "errors": e.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except IntegrityError as e:
            return Response(
                {"success": 0, "message": "Database error. Possible duplicate entry."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return Response(
                {"success": 0, "message": "An unexpected error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )



#add single employee data
class EmployeeMetricsCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            employee_id = request.data.get("employee_id")
            if not employee_id:
                return Response({"success": 0, "message": "Employee ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            employee = get_object_or_404(Employee, id=employee_id)

            # Ensure metrics do not already exist for this employee
            if EmployeeMetrics.objects.filter(employee=employee).exists():
                return Response({"success": 0, "message": "Metrics for this employee already exist"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = EmployeeMetricsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(employee=employee)
                return Response({"success": 1, "message": "Employee metrics added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            
            return Response({"success": 0, "message": "Invalid data", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"success": 0, "message": "An error occurred", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#for filter table
class FilteredMetricsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            category = request.query_params.get("category", "").lower()
            count_param = request.query_params.get("count", None)

            if not category:
                return Response(
                    {"success": 0, "message": "Category parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Determine the count limit
            count = None
            if count_param:
                try:
                    count = int(count_param)
                    if count <= 0:
                        return Response(
                            {"success": 0, "message": "Count must be a positive integer."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                except ValueError:
                    return Response(
                        {"success": 0, "message": "Invalid count value. Must be an integer."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Select the model based on category
            if category == "employees":
                queryset = EmployeeMetrics.objects.all()

            elif category == "projects":
                try:
                    from .models import ProjectMetrics
                    queryset = ProjectMetrics.objects.all()
                except ImportError:
                    return Response(
                        {"success": 0, "message": "Project metrics model not found."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            elif category == "departments":
                try:
                    from .models import DepartmentMetrics
                    queryset = DepartmentMetrics.objects.all()
                except ImportError:
                    return Response(
                        {"success": 0, "message": "Department metrics model not found."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            else:
                return Response(
                    {"success": 0, "message": "Invalid category. Choose from 'employees', 'projects', or 'departments'."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Apply count limit if specified
            if count is not None:
                queryset = queryset[:count]

            serializer = EmployeeMetricsSerializerForFilter(queryset, many=True)

            response_data = {
                "success": 1,
                "message": f"{category.capitalize()} metrics retrieved successfully",
                "data": serializer.data,
                "returned_count": len(serializer.data)
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except DatabaseError:
            return Response(
                {"success": 0, "message": "Database error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response(
                {"success": 0, "message": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


#to dowmload pdf
class DownloadFilteredPDF(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        category = request.query_params.get("category", "").lower()
        count_param = request.query_params.get("count", None)

        # ✅ Validate count
        count = None
        if count_param:
            try:
                count = int(count_param)
                if count <= 0:
                    return Response(
                        {"success": 0, "message": "Count must be a positive integer."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {"success": 0, "message": "Invalid count value. Must be an integer."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # ✅ Fetch data based on category
        if category == "employees":
            queryset = EmployeeMetrics.objects.all()
            serializer = EmployeeMetricsSerializerForFilter(queryset[:count] if count else queryset, many=True)
            data = serializer.data
        elif category == "projects":
            queryset = ProjectMetrics.objects.all()
            data = queryset.values("project_name", "progress_score", "quality_score", "timeliness_score", "final_score")
        elif category == "departments":
            queryset = DepartmentMetrics.objects.all()
            data = queryset.values("department_name", "efficiency_score", "quality_score", "timeliness_score", "final_score")
        else:
            return Response(
                {"success": 0, "message": "Invalid category. Choose 'employees', 'projects', or 'departments'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Create PDF response
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{category}_metrics.pdf"'

        # ✅ Set up the document
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []

        styles = getSampleStyleSheet()
        title = Paragraph(f"<b>{category.capitalize()} Metrics Report</b>", styles["Title"])
        elements.append(title)

        # ✅ Employees - Table Format
        if category == "employees":
            table_data = [
                ["Employee Name", "Productivity Score (%)", "Quality Score (%)", "Timeliness Score (%)", "Total Score (%)"]
            ]

            for item in data:
                table_data.append([
                    item["employee_name"], 
                    f"{item['productivity_score']}%",
                    f"{item['quality_score']}%",
                    f"{item['timeliness_score']}%",
                    f"{item['total_score']}%"
                ])

            table = Table(table_data, colWidths=[120, 100, 100, 100, 100])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            elements.append(table)

        # ✅ Projects & Departments - Simple List Format
        else:
            for item in data:
                text = Paragraph(f"{item}", styles["Normal"])
                elements.append(text)

        # ✅ Build PDF
        doc.build(elements)
        return response




@method_decorator(csrf_exempt, name='dispatch')
class SendMetricsEmailView(View):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            email = data.get("email")
            category = data.get("category")
            count = int(data.get("count", 10))

            if not email:
                return JsonResponse({"success": False, "message": "Email is required"}, status=400)

            # Fetch actual data from the database
            metrics = EmployeeMetrics.objects.all()[:count]

            if not metrics.exists():
                return JsonResponse({"success": False, "message": "No data available."}, status=404)

            # Serialize data
            serialized_data = EmployeeMetricsSerializerForFilter(metrics, many=True).data

            # Generate PDF and Excel files
            pdf_buffer = self.generate_pdf(category, serialized_data)
            excel_buffer = self.generate_excel(category, serialized_data)

            # Send email with both files attached
            if self.send_email(email, category, pdf_buffer, excel_buffer):
                ReportLog.objects.create(email=email, category=category, datetime=now())
                return JsonResponse({"success": True, "message": "Email sent successfully!"})
            else:
                return JsonResponse({"success": False, "message": "Failed to send email"}, status=500)

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error: {str(e)}"}, status=500)

    def generate_pdf(self, category, metrics):
        """
        Generate a PDF report dynamically with actual employee data.
        """
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)
        pdf.setTitle(f"{category.capitalize()} Metrics Report")

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(200, 800, f"{category.capitalize()} Metrics Report")

        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, 780, f"Report Category: {category}")
        pdf.drawString(50, 760, f"Records Count: {len(metrics)}")

        y_position = 740
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y_position, "Employee Name")
        pdf.drawString(250, y_position, "Productivity")
        pdf.drawString(350, y_position, "Quality")
        pdf.drawString(450, y_position, "Timeliness")
        y_position -= 20

        pdf.setFont("Helvetica", 10)
        for emp in metrics:
            pdf.drawString(50, y_position, emp["employee_name"])
            pdf.drawString(250, y_position, f"{emp['productivity_score']}%")
            pdf.drawString(350, y_position, f"{emp['quality_score']}%")
            pdf.drawString(450, y_position, f"{emp['timeliness_score']}%")
            y_position -= 20

            if y_position < 50:
                pdf.showPage()
                y_position = 800

        pdf.save()
        buffer.seek(0)
        return buffer

    def generate_excel(self, category, metrics):
        """
        Generate an Excel report dynamically with actual data.
        """
        buffer = BytesIO()
        df = pd.DataFrame(metrics)

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Metrics", index=False)

        buffer.seek(0)
        return buffer

    def send_email(self, email, category, pdf_buffer, excel_buffer):
        """
        Send an email with the generated PDF and Excel attached.
        """
        try:
            mail = EmailMessage(
                subject=f"{category.capitalize()} Metrics Report From Symplotel ScoreCard",
                body=f"Attached are the {category} metrics reports (PDF & Excel).",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )
            mail.attach(f"{category}_metrics_report.pdf", pdf_buffer.getvalue(), "application/pdf")
            mail.attach(f"{category}_metrics_report.xlsx", excel_buffer.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            mail.send()
            return True
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False


class UploadEmployeesMetricsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'success': 0, 'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        # Save file temporarily
        file_path = default_storage.save(f'uploads/{file.name}', ContentFile(file.read()))

        # Check file extension
        if file.name.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file.name.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            return Response({'success': 0, 'error': 'Invalid file format. Upload CSV or Excel file.'}, status=status.HTTP_400_BAD_REQUEST)

        duplicate_entries = []
        
        for _, row in df.iterrows():
            try:
                employee, created = Employee.objects.update_or_create(
                    employee_id=row['employee_id'],
                    defaults={
                        "full_name": row['full_name'],
                        "department": row['department'],
                        "position": row['position']
                    }
                )

                metrics, created = EmployeeMetrics.objects.update_or_create(
                    employee=employee,
                    defaults={
                        "hrs_wrkd_per_week": row['hrs_wrkd_per_week'],
                        "tasks_completed": row['tasks_completed'],
                        "sales_made": row['sales_made'],
                        "error_rate": row['error_rate'],
                        "customer_rating": row['customer_rating'],
                        "returns_or_complaints": row['returns_or_complaints'],
                        "deadlines_met": row['deadlines_met'],
                        "total_deadlines": row['total_deadlines'],
                        "project_cmple_times": row['project_cmple_times'],
                        "target_cmple_times": row['target_cmple_times'],
                    }
                )
                
                metrics.save()

                if not created:
                    duplicate_entries.append(row.to_dict())

            except Exception as e:
                return Response({'success': 0, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if duplicate_entries:
            output = BytesIO()
            wb = Workbook()
            ws = wb.active
            ws.append(df.columns.tolist())
            for entry in duplicate_entries:
                ws.append(list(entry.values()))
            wb.save(output)
            output.seek(0)
            response = Response({'success': 1, 'message': 'Employee metrics uploaded successfully', 'duplicates': 'File attached'}, status=status.HTTP_201_CREATED)
            response['Content-Disposition'] = 'attachment; filename=duplicate_entries.xlsx'
            response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.content = output.getvalue()
            return response

        return Response({'success': 1, 'message': 'Employee metrics uploaded successfully'}, status=status.HTTP_201_CREATED)

