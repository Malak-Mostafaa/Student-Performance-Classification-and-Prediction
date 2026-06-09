from django.urls import path
from . import views

# URL routes for instructor dashboard and report export
urlpatterns = [
    path("dashboard/", views.instructor_dashboard, name="instructor_dashboard"),# instructor dashboard page
    path("export-csv/", views.export_predictions_csv, name="export_predictions_csv"), # export prediction records as CSV report
    path("export-pdf/", views.export_predictions_pdf, name="export_predictions_pdf"), # export prediction records as PDF report
]
