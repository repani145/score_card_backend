from django.urls import path
from . import views as app_views

urlpatterns = [
    path('metrics_summery',app_views.MetricsSummaryView.as_view(),name='metrics_summery'),
    path('top_scored_employees',app_views.TopScoredEmployeesView.as_view(),name='top_scored_employees'),
    path('add_employee', app_views.EmployeeCreateAPIView.as_view(), name='add_employee'),
    path('employees_metric_view',app_views.EmployeeMetricsView.as_view(),name='employees_metric_view'),
    path('add_employee_data',app_views.EmployeeMetricsCreateAPIView.as_view(),name='add_employee_data'),
    path("filtered-metrics/", app_views.FilteredMetricsAPIView.as_view(), name="filtered-metrics"),
    path("download-filtered-pdf/", app_views.DownloadFilteredPDF.as_view(), name="download_filtered_pdf"),
    path("send-metrics-email/", app_views.SendMetricsEmailView.as_view(), name="send_metrics_email"),
    path('upload_employees_metrics',app_views.UploadEmployeesMetricsView.as_view(),name='upload_employees_metrics'),
]
