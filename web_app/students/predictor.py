import os
import joblib
import pandas as pd
from django.conf import settings

# load saved machine learning model and preprocessing files
model = joblib.load(os.path.join(settings.BASE_DIR, "random_forest_model.pkl")) 
scaler = joblib.load(os.path.join(settings.BASE_DIR, "scaler.pkl"))
model_columns = joblib.load(os.path.join(settings.BASE_DIR, "model_columns.pkl"))


def predict_dropout(student_data):
    input_df = pd.DataFrame([student_data]) # convert student input into dataframe for prediction

    # ensure input columns match the training columns
    for col in model_columns: 
        if col not in input_df.columns:
            input_df[col] = 0

    input_df = input_df[model_columns]
    scaled_input = scaler.transform(input_df)
    # generate model prediction and dropout probability
    prediction = model.predict(scaled_input)[0]    # Random Forest threshold (0.5) internally   
    probability = model.predict_proba(scaled_input)[0][1]

    risk_score = 0
    if student_data["avg_score"] < 50:
        risk_score += 2
    if student_data["active_days"] < 5:
        risk_score += 2
    if student_data["total_clicks"] < 100:
        risk_score += 2
    if student_data["assessments_submitted"] < 3:
        risk_score += 1
    if student_data["num_of_prev_attempts"] > 0:
        risk_score += 1

    if risk_score >= 5:
        prediction = 1
        probability = max(probability, 0.80)

    return prediction, probability

# generate personalized recommendations based on prediction result and input values
def generate_recommendations(student_data, prediction):
    recommendations = []

    if prediction == 1:
        recommendations.append({
            "text": "You are currently at high risk. Please review your academic progress carefully.",
            "link": ""
        })
        if student_data["avg_score"] < 50:
            recommendations.append({
                "text": "Your average score is low. Review weak topics and improve your understanding of the course basics.",
                "link": "https://www.youtube.com/watch?v=Lt54CX9DmS4"
            })
        if student_data["active_days"] < 5:
            recommendations.append({
                "text": "Your platform activity is low. Try to study more regularly and build a daily learning routine.",
                "link": "https://www.youtube.com/watch?v=BsLC5eIjcag"
            })
        if student_data["total_clicks"] < 100:
            recommendations.append({
                "text": "Your interaction with the learning platform is limited. Spend more time reviewing course materials and using active learning techniques.",
                "link": "https://www.youtube.com/watch?v=RrKbJRRlavg"
            })
        if student_data["assessments_submitted"] < 3:
            recommendations.append({
                "text": "You submitted few assessments. Try to complete more tasks on time and manage assignment deadlines carefully.",
                "link": "https://www.youtube.com/watch?v=cUpXwoHF5x4"
            })
        if student_data["num_of_prev_attempts"] > 0:
            recommendations.append({
                "text": "Since you have previous attempts, review past mistakes and use better study strategies.",
                "link": "https://www.youtube.com/watch?v=GxAWyTwJMXQ"
            })
    else:
        recommendations.append({
            "text": "You are currently in a good position. Keep maintaining your learning progress.",
            "link": ""
        })
        if student_data["avg_score"] >= 80:
            recommendations.append({
                "text": "Your academic performance is strong. Keep following your current study strategy.",
                "link": "https://www.youtube.com/watch?v=1bszFX_XcbU"
            })
        if student_data["active_days"] >= 10:
            recommendations.append({
                "text": "Your engagement level is good. Continue participating actively on the platform.",
                "link": "https://www.youtube.com/watch?v=BsLC5eIjcag"
            })
        if student_data["total_clicks"] >= 150:
            recommendations.append({
                "text": "You are interacting well with the learning materials. Keep exploring course resources and active learning methods.",
                "link": "https://www.youtube.com/watch?v=RrKbJRRlavg"
            })
        if student_data["avg_score"] < 70:
            recommendations.append({
                "text": "Although your current risk is low, improving your average score will make your performance more stable.",
                "link": "https://www.youtube.com/watch?v=Lt54CX9DmS4"
            })

    return recommendations
