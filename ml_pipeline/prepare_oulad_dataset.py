import os
import pandas as pd
from collections import defaultdict

# get current working folder 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print("Working folder:", BASE_DIR)
print("Available files:", os.listdir(BASE_DIR))


# 1. load main student data
# this file contains final result for each student
students_df = pd.read_csv(os.path.join(BASE_DIR, "studentInfo.csv"))
print("\nStudents dataset shape:", students_df.shape)

print("\nFinal result distribution:")
print(students_df["final_result"].value_counts())


# create target column
# student withdrew=1 
# student completed=0
students_df["target_dropout"] = (
    students_df["final_result"] == "Withdrawn"
).astype(int)

print("\nDropout distribution:")
print(students_df["target_dropout"].value_counts())


# 2. load assessment data
assessments_df = pd.read_csv(os.path.join(BASE_DIR, "assessments.csv"))
student_assessment_df = pd.read_csv(os.path.join(BASE_DIR, "studentAssessment.csv"))

print("\nAssessments shape:", assessments_df.shape)
print("StudentAssessment shape:", student_assessment_df.shape)


# merge assessments with student scores
merged_assessments = student_assessment_df.merge(
    assessments_df,
    on="id_assessment",
    how="left"
)
print("\nMerged assessments shape:", merged_assessments.shape)


# clean numeric columns 
merged_assessments["score"] = pd.to_numeric(
    merged_assessments["score"],
    errors="coerce"
)

merged_assessments["weight"] = pd.to_numeric(
    merged_assessments["weight"],
    errors="coerce"
).fillna(0)


#  feature engineering 
assessment_features = merged_assessments.groupby(
    ["id_student", "code_module", "code_presentation"]
).agg(
    assessments_submitted=("id_assessment", "count"),
    avg_score=("score", "mean"),
    max_score=("score", "max"),
    min_score=("score", "min"),
    total_weight=("weight", "sum"),
).reset_index()

print("\nAssessment features created:", assessment_features.shape)


# merge with student info
model_df = students_df.merge(
    assessment_features,
    on=["id_student", "code_module", "code_presentation"],
    how="left"
)

print("\nAfter merging assessments:", model_df.shape)


# 3. process VLE (student activity) chunks was used to avoid memory issues
click_sum = defaultdict(int)
active_days = defaultdict(set)
chunksize = 300000  
print("\nProcessing studentVle data...")

for chunk in pd.read_csv(
    os.path.join(BASE_DIR, "studentVle.csv"),
    chunksize=chunksize
):
    keys = list(zip(
        chunk["id_student"],
        chunk["code_module"],
        chunk["code_presentation"]
    ))

    clicks = chunk["sum_click"].tolist()
    days = chunk["date"].tolist()

    for k, c, d in zip(keys, clicks, days):
        click_sum[k] += int(c)  # total no of clicks for each student
        active_days[k].add(int(d))
print("Finished processing VLE data")


# convert VLE data into dataframe
vle_features = pd.DataFrame(
    [
        (k[0], k[1], k[2], click_sum[k], len(active_days[k]))
        for k in click_sum
    ],
    columns=[
        "id_student",
        "code_module",
        "code_presentation",
        "total_clicks",
        "active_days"
    ]
)

print("\nVLE features shape:", vle_features.shape)


# merge VLE features
model_df = model_df.merge(
    vle_features,
    on=["id_student", "code_module", "code_presentation"],
    how="left"
)

print("\nAfter adding VLE features:", model_df.shape)


# 4. handle missing values fill with 0 because missing means no activity
print("\nChecking missing values before filling...")
print(model_df.isna().sum().sum())

model_df = model_df.fillna(0)

print("Missing values after filling:")
print(model_df.isna().sum().sum())


# 5. save final dataset
output_path = os.path.join(BASE_DIR, "oulad_ready_for_training.csv")

model_df.to_csv(output_path, index=False)

print("\nDataset saved successfully!")
print("Saved file path:", output_path)

