from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render   #html 
from django.http import HttpResponse  #for csv, pdf files
from django.contrib.auth.models import User
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas  
import csv
from students.models import PredictionRecord

# check if the logged-in user is an instructor
def is_instructor(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_instructor)
def instructor_dashboard(request):
    search_query = request.GET.get("search", "")      # get search and filter values from request
    risk_filter = request.GET.get("risk", "all")       
    student_search = request.GET.get("student_search", "")

    all_predictions = PredictionRecord.objects.order_by("-created_at") # get all prediction records ordered by latest first

    # filter predictions by student username
    if search_query:
        all_predictions = all_predictions.filter(user__username__icontains=search_query)
    #filter prediction by risk level 
    if risk_filter == "high":
        all_predictions = all_predictions.filter(prediction="High Risk")
    elif risk_filter == "low":
        all_predictions = all_predictions.filter(prediction="Low Risk")

    students_list = User.objects.filter(is_staff=False, is_superuser=False).order_by("username")
    if student_search:
        students_list = students_list.filter(username__icontains=student_search) #student list for view

    total_predictions = PredictionRecord.objects.count()  
    high_risk_count = PredictionRecord.objects.filter(prediction="High Risk").count()
    low_risk_count = PredictionRecord.objects.filter(prediction="Low Risk").count()
    
    #prepare data for instructor dashboard template 
    context = {
        "instructor_name": request.user.username,
        "total_predictions": total_predictions,
        "high_risk_count": high_risk_count,
        "low_risk_count": low_risk_count,
        "recent_predictions": all_predictions[:10],
        "chart_data": {
            "high": high_risk_count,
            "low": low_risk_count,
        },
        "search_query": search_query,
        "risk_filter": risk_filter,
        "students_list": students_list[:12],
        "student_search": student_search,
    }

    return render(request, "instructors/dashboard.html", context)

# export prediction records as CSV file
@login_required
@user_passes_test(is_instructor)
def export_predictions_csv(request):
    response = HttpResponse(content_type="text/csv")  #create csv 
    response["Content-Disposition"] = 'attachment; filename="prediction_report.csv"'

    writer = csv.writer(response)  #write csv rows, headers 
    writer.writerow(["Student", "Prediction", "Probability (%)", "Avg Score", "Active Days", "Total Clicks", "Created At"])
    #get prediction records with user data 
    records = PredictionRecord.objects.select_related("user").order_by("-created_at")
    for record in records:
        writer.writerow([
            record.user.username,
            record.prediction,
            round(record.probability * 100, 2),
            record.avg_score,
            record.active_days,
            record.total_clicks,
            record.created_at.strftime("%Y-%m-%d %H:%M"),
        ])

    return response

# export prediction records as PDF file
@login_required
@user_passes_test(is_instructor)
def export_predictions_pdf(request):
    response = HttpResponse(content_type="application/pdf")  #create pdf response 
    response["Content-Disposition"] = 'attachment; filename="prediction_report.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    y = 750

    p.setFont("Helvetica-Bold", 16)
    p.drawString(190, y, "Student Prediction Report")
    y -= 40
    
    # get prediction records and calculate summary values
    predictions = PredictionRecord.objects.select_related("user").order_by("-created_at")
    high = predictions.filter(prediction="High Risk").count()
    low = predictions.filter(prediction="Low Risk").count()

    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"Instructor: {request.user.username}")
    y -= 20
    p.drawString(50, y, f"Total Predictions: {predictions.count()}")
    y -= 20
    p.drawString(50, y, f"High Risk: {high}")
    y -= 20
    p.drawString(50, y, f"Low Risk: {low}")
    y -= 40

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Recent Predictions:")
    y -= 20

    p.setFont("Helvetica", 10)
    for record in predictions[:10]:
        text = f"{record.user.username} | {record.prediction} | {round(record.probability * 100, 2)}%"
        p.drawString(50, y, text)
        y -= 15
        if y < 50:
            p.showPage()
            p.setFont("Helvetica", 10)
            y = 750

    p.save()
    return response
