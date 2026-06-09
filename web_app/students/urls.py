from django.urls import path
from . import views

# URL routes for student dashboard and prediction system
urlpatterns = [
    path("", views.dashboard, name="dashboard"), # student dashboard page
    path("predict/", views.run_prediction, name="run_prediction"),   # run AI prediction
    path("redirect-dashboard/", views.role_based_redirect, name="role_based_redirect"), # redirect users based on their role
    path("student-chatbot/", views.student_chatbot, name="student_chatbot"),
]
