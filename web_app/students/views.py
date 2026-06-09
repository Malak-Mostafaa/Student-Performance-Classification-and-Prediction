from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect 
from django.contrib import messages
from django.core.mail import send_mail
from courses.models import Enrollment 
from .predictor import predict_dropout, generate_recommendations
from .models import PredictionRecord
from django.http import JsonResponse 
import json

# prepare student dashboard context data
def _dashboard_context(request):
    courses = [e.course for e in Enrollment.objects.filter(student=request.user).select_related("course")]
    return {
        "student_name": request.user.username,
        "risk_status": "Not evaluated yet",
        "courses": courses,
    }

#display student dashboard with latest prediction
@login_required
def dashboard(request):
    latest_prediction = PredictionRecord.objects.filter(
        user=request.user
    ).order_by("-created_at").first()

    courses = [e.course for e in Enrollment.objects.filter(student=request.user).select_related("course")]

    context = {
        "student_name": request.user.username,
        "risk_status": latest_prediction.prediction if latest_prediction else "Not evaluated yet",
        "latest_prediction": latest_prediction,
        "courses": courses,
        "probability_percent": round(latest_prediction.probability * 100, 2) if latest_prediction else 0,
    }

    return render(request, "students/dashboard.html", context)

#generate ai result
@login_required
def run_prediction(request):
    if request.method != "POST":
        return render(request, "students/dashboard.html", _dashboard_context(request))

    try:
        #collect student input data from form
        student_data = {
            "assessments_submitted": float(request.POST.get("assessments_submitted", 0)),
            "total_weight": float(request.POST.get("total_weight", 0)),
            "active_days": float(request.POST.get("active_days", 0)),
            "avg_score": float(request.POST.get("avg_score", 0)),
            "min_score": float(request.POST.get("min_score", 0)),
            "total_clicks": float(request.POST.get("total_clicks", 0)),
            "max_score": float(request.POST.get("max_score", 0)),
            "studied_credits": float(request.POST.get("studied_credits", 0)),
            "num_of_prev_attempts": float(request.POST.get("num_of_prev_attempts", 0)),
        }
    except ValueError:
        messages.error(request, "Invalid input. Please enter numbers only.")
        return render(request, "students/dashboard.html", _dashboard_context(request))

    if any(value < 0 for value in student_data.values()):   # prevent negative values
        messages.error(request, "Values cannot be negative.")
        return render(request, "students/dashboard.html", _dashboard_context(request))

    if student_data["avg_score"] > 100 or student_data["min_score"] > 100 or student_data["max_score"] > 100: #score range
        messages.error(request, "Scores must be between 0 and 100.")
        return render(request, "students/dashboard.html", _dashboard_context(request))

    if student_data["min_score"] > student_data["max_score"]:
        messages.error(request, "Min score cannot be greater than max score.")
        return render(request, "students/dashboard.html", _dashboard_context(request))
    
    # generate prediction using trained machine learning model
    pred, prob = predict_dropout(student_data)
    recommendations = generate_recommendations(student_data, pred)   # generate recommendations

    prediction_text = "High Risk" if pred == 1 else "Low Risk"

    if prediction_text == "High Risk":
        messages.warning(request, "Alert: This student is currently at high academic risk and may need immediate support.")
        # send warning email to high risk student
        if request.user.email:
            send_mail(
                subject="High Risk Alert - Student Performance System",
                message=(
                    f"Hello {request.user.username},\n\n"
                    f"Our system has detected that you are currently at high academic risk.\n"
                    f"Please review your dashboard recommendations and suggested learning resources.\n\n"
                    f"Prediction: {prediction_text}\n"
                    f"Probability: {round(prob * 100, 2)}%\n\n"
                    f"Regards,\n"
                    f"Student Performance System"
                ),
                from_email=None,
                recipient_list=[request.user.email],
                fail_silently=True,
            )
    else:
        messages.success(request, "Good news: The student is currently in a stable academic position.")

    # save prediction result into database
    PredictionRecord.objects.create(
        user=request.user,
        prediction=prediction_text,
        probability=prob,
        assessments_submitted=student_data["assessments_submitted"],
        total_weight=student_data["total_weight"],
        active_days=student_data["active_days"],
        avg_score=student_data["avg_score"],
        min_score=student_data["min_score"],
        total_clicks=student_data["total_clicks"],
        max_score=student_data["max_score"],
        studied_credits=student_data["studied_credits"],
        num_of_prev_attempts=student_data["num_of_prev_attempts"],
    )

    context = {
        "student_name": request.user.username,
        "prediction": prediction_text,
        "score": round(prob, 2),
        "probability_percent": round(prob * 100, 2),
        "input_data": student_data,
        "recommendations": recommendations,
    }

    return render(request, "students/prediction_result.html", context)

# redirect users based on their role
@login_required
def role_based_redirect(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("instructor_dashboard")
    return redirect("dashboard")


#rule-based chatbot for student assistance
def student_chatbot(request):
    if request.method == "POST":
        data = json.loads(request.body)  # read chatbot request data

        msg = data.get("message", "").lower()
        risk_level = data.get("risk_level", "")

        if "recommend" in msg or "recommendations" in msg:
            if risk_level == "High Risk":
                reply = "You are at high risk. Focus on increasing your activity, completing assessments, and reviewing weak topics immediately."
            else:
                reply = "You are doing well. Maintain your consistency and keep engaging with the platform."

        elif "improve" in msg or "advice" in msg:
            if risk_level == "High Risk":
                reply = "To improve your performance, submit more assessments, increase activity days, and review weak topics regularly."
            else:
                reply = "Keep maintaining your good performance and continue engaging actively with the platform."

        elif "explain" in msg or "result" in msg or "why" in msg:
            if risk_level == "High Risk":
                reply = "Your prediction is High Risk because the system detected weak performance or low engagement indicators."
            else:
                reply = "Your prediction is Low Risk because your performance and engagement indicators are currently stable."

        else:
            reply = "You can ask me to explain your result, give recommendations, or suggest how to improve your performance."

        return JsonResponse({"reply": reply})

    return JsonResponse({"reply": "Invalid request"})