import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# load the prepared dataset
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "oulad_ready_for_training.csv")
df = pd.read_csv(file_path)
print("Dataset loaded successfully")


# removing columns that r not be used directly (id_students)
columns_to_drop = ["id_student", "final_result"]
for col in columns_to_drop:
    if col in df.columns:
        df.drop(columns=col, inplace=True)

# Defining x,y 
target_column = "target_dropout"
X = df.drop(columns=[target_column]) #data the model will learn from(x)
y = df[target_column]  #right answer or target (droupout=1 , not dropout=0)

print("\nTarget distribution:")
print(y.value_counts())

# convert text columns into numeric form
X = pd.get_dummies(X, drop_first=True)
print(X.head())
print("\nFeatures after encoding:", X.shape)

# split the dataset 
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y #keep class distribution(high, low) balanced 
)

print("\nTraining set shape:", X_train.shape)
print("Testing set shape:", X_test.shape)

# scale numerical features before training
scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# define models
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42), 
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "Random Forest": RandomForestClassifier(random_state=42, n_estimators=100) #100 tree
}

# train and evaluate each model
for model_name, model in models.items():
    print("\n" + "=" * 60)
    print(model_name)
    print("=" * 60)

    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)

    acc = accuracy_score(y_test, y_pred) #accuracy 

    print("Accuracy:", round(acc, 4))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred)) #precision, recall, f1 score 

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))


# Feature Importance using Random Forest
rf_model = models["Random Forest"]    # get the trained Random Forest model
# extract importance values for each feature
importances = rf_model.feature_importances_
# get feature names after encoding
feature_names = X.columns
#make table for features name and importnace 
import pandas as pd
feat_data = pd.DataFrame({               
    "feature": feature_names,
    "importance": importances
})
# sort features from most important to least
feat_data = feat_data.sort_values(by="importance", ascending=False)

# select top 10 features 
top_features = feat_data.head(10)
import matplotlib.pyplot as plt
plt.figure(figsize=(8,5))
plt.barh(top_features["feature"], top_features["importance"])
plt.gca().invert_yaxis()  #most imp in top
plt.title("Top Important Features - Random Forest")
plt.xlabel("Importance")
plt.ylabel("Features")
# save the image to use in the report
plt.savefig("feature_importance.png")
plt.show()

#saving files for Django integration
import joblib
# use  trained Random Forest model
best_model = models["Random Forest"]

joblib.dump(best_model, "random_forest_model.pkl")  # save the model as .pkl

joblib.dump(scaler, "scaler.pkl")  # save scaler

joblib.dump(X.columns.tolist(), "model_columns.pkl")   # save columns

print("\nModel, scaler, and columns saved successfully!")
