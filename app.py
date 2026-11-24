
from flask import Flask, request, render_template
import pickle
import pandas as pd
from db_connector import get_db_connection

# Creates the Flask application
app = Flask(__name__)

# Loads the trained model
with open("loan_approval_decision_tree_practice.pkl", "rb") as file:
    model = pickle.load(file)


# Creates the homepage
@app.route("/")
def home():
    return render_template("index.html")


# Creates the prediction route
@app.route("/predict", methods=["POST"])
def predict():

    # Get input values from the HTML form
    age = int(request.form["Age"])
    monthly_income = float(request.form["Monthly_Income"])
    credit_score = int(request.form["Credit_Score"])
    employment_years = int(request.form["Employment_Years"])
    loan_amount = float(request.form["Loan_Amount"])
    loan_term_months = int(request.form["Loan_Term_Months"])

    # Prepare input data for the model
    # Prepare input data with all required features
    input_data = pd.DataFrame([{
        "Age": age,
        "Monthly_Income": monthly_income,
        "Credit_Score": credit_score,
        "Employment_Years": employment_years,
        "Loan_Amount": loan_amount,
        "Loan_Term_Months": loan_term_months,
        "Existing_Loan": 0,
        "Self_Employed": 0,
        "Education_Graduate": 1,
        "Education_High School": 0,
        "Education_Postgraduate": 0,
        "Property_Area_Rural": 1,
        "Property_Area_Semiurban": 0,
        "Property_Area_Urban": 0
    }])

    # Predict loan status
    predictions = model.predict(input_data)
    prediction = "Approved" if predictions[0] == 0 else "Rejected"

    # Connect to MySQL
    db = get_db_connection()
    cursor = None

    try:
        cursor = db.cursor()

        # Insert loan details and prediction into MySQL
        sql = """
            INSERT INTO loan_predictions
            (
                age,
                monthly_income,
                credit_score,
                employment_years,
                loan_amount,
                loan_term_months,
                prediction
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            age,
            monthly_income,
            credit_score,
            employment_years,
            loan_amount,
            loan_term_months,
            prediction
        )

        cursor.execute(sql, values)
        db.commit()

    finally:
        if cursor is not None:
            cursor.close()
        db.close()

    # Display the prediction result
    return render_template(
        "result.html",
        prediction=prediction
    )


# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)
