import streamlit as st
import sqlite3 as sq
import hashlib
from datetime import datetime
import time
import pandas as pd
import numpy as np
import streamlit as st
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
from database import insert_health_data, fetch_health_data, initialize_db, profiles_set, fetch_user_info
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
import joblib
import plotly.express as px
import random

if 'page' not in st.session_state:
    st.session_state.page = 'home_page'
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'predicted_dises' not in st.session_state:
    st.session_state.predicted_dises = None
# Utility functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()



def login(user_name, password):
    conn = sq.connect('auth.db')
    c = conn.cursor()
    hashed_password = hash_password(password)  # Hash the input password once
    c.execute("""SELECT * FROM users WHERE username = ? AND password = ?""", (user_name, hashed_password))
    user = c.fetchone()
    conn.close()  # Close the connection
    return user is not None


def signup(user_name, password):
    conn = sq.connect("auth.db")
    c = conn.cursor()
    password = hash_password(password)
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user_name, password))
        conn.commit()
        return True
    except sq.IntegrityError:
        return False
    finally:
        conn.close()  # Close the connection properly

def save_profile(user_name, full_name, age, gender, height, weight):
    try:
        with sq.connect('profiles.db', timeout=10) as conn:  # Using 'with' to automatically close connection
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO profiles (user_name, full_name, age, gender, height, weight)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_name, full_name, age, gender, height, weight))
            conn.commit()
            st.success("Profile saved successfully!")
            return True
    except sq.OperationalError as e:
        st.error(f"Database error: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

def personal_data():
    profiles_set()
    st.subheader("👤 Set Up Your Profile")
    with st.form(key="profile_form"):
        full_name = st.text_input("Full Name")
        age = st.number_input("Age", min_value=1, step=1)
        gender = st.radio("Gender", ["Male", "Female", "Other"])
        height = st.number_input("Height (in m)", min_value=1.0)
        weight = st.number_input("Weight (in kg)", min_value=1.0)
        
        submitted = st.form_submit_button("Save")
        
        
        if submitted:
            if not full_name or not age or not height or not weight:
                st.error('Please fill all the details.')
            else:
                with st.spinner("Saving data.."):
                    time.sleep(2)
                    if save_profile(st.session_state.user_name, full_name, age, gender, height, weight):
                        st.session_state.page = 'mainn_page'
                st.rerun()
    
def analyzer():
    @st.cache_resource
    def load_model_and_encoder():
        model = joblib.load("datasets/disease_predictor_model.pkl")
        mlb = joblib.load("datasets/symptoms_encoder.pkl")
        return model, mlb

    # Predict Disease
    def predict_disease(model, mlb, symptoms):
        input_data = mlb.transform([symptoms])
        probabilities = model.predict_proba(input_data)[0]
        predicted_disease_idx = probabilities.argmax()
        predicted_disease = model.classes_[predicted_disease_idx]
        return predicted_disease, probabilities

    # Streamlit app

    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Symptom Analyzer & Disease Predictor</h1>", unsafe_allow_html=True)

    # Load the dataset
    file_path = "datasets/Diseases_Symptoms.csv"
    dataset = pd.read_csv(file_path)
    dataset['Symptoms_list'] = dataset['Symptoms'].apply(lambda x: x.split(', '))

    # Load the trained model and encoder
    model, mlb = load_model_and_encoder()

    # List of all symptoms
    all_symptoms = mlb.classes_

    # Sidebar instructions
    st.sidebar.markdown("### How to Use")
    st.sidebar.write("""
    1. Select symptoms from the dropdown.
    2. Click 'Predict' to get the most likely disease and its treatment.
    3. View probabilities for top diseases in the chart.
    """)
    st.sidebar.divider()
    st.sidebar.button("Back", on_click=lambda: setattr(st.session_state, 'page', 'mainn_page'))
    # User input: Multiple Select for symptoms
    selected_symptoms = st.multiselect(
        "Select your symptoms:",
        all_symptoms,
        help="Choose symptoms that you are experiencing from the list."
    )
    print(len(all_symptoms))
    for i in  all_symptoms:
        if i in selected_symptoms:
            st.slider(f"Symptoms Severity of {i}", min_value=0, max_value=100)
    if selected_symptoms:
        st.subheader("Symptom Details")
        symptom_durations = {}
        for symptom in selected_symptoms:
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"Symptom: *{symptom}*")
            with col2:
                duration = st.number_input(
                    f"How long have you had {symptom} (in days)?",
                    min_value=1,
                    max_value=30,
                    value=1,
                    key=f"duration_{symptom}"
                )
                symptom_durations[symptom] = duration

    else:
        st.info("Please select your symptoms to provide additional details.")

    if st.button("Predict"):
        if selected_symptoms:
            # Predict the disease
            predicted_disease, probabilities = predict_disease(model, mlb, selected_symptoms)
            st.session_state.predicted_dises= predicted_disease
            # Display the most probable disease
            st.markdown(f"<h2 style='color: #FF5722;'>🩺 Most Predicted Disease: {predicted_disease}</h2>", unsafe_allow_html=True)

            # Retrieve probabilities for all diseases
            disease_probabilities = pd.DataFrame({
                "Disease": model.classes_,
                "Probability": probabilities
            }).sort_values(by="Probability", ascending=False)

            # Display bar chart for top N diseases
            top_n = 5  # Show top 5 diseases
            top_diseases = disease_probabilities.head(top_n)

            st.subheader("Top Predicted Diseases and Probabilities")
            fig = px.bar(
                top_diseases,
                x="Probability",
                y="Disease",
                orientation="h",
                color="Probability",
                color_continuous_scale="Viridis",
                title="Top Predicted Diseases",
            )
            st.plotly_chart(fig, use_container_width=True)

            # Display treatment recommendation
            treatment = dataset.loc[dataset['Name'] == predicted_disease, 'Treatments'].values
            if treatment.any():
                st.markdown(f"<h3 style='color: #4CAF50;'>💊 Recommended Treatment: {treatment[0]}</h3>", unsafe_allow_html=True)
                return True
            else:
                st.markdown("<h3 style='color: #4CAF50;'>💊 No specific treatment recommendation available.</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='color: red;'>⚠ Please select at least one symptom to proceed.</h3>", unsafe_allow_html=True)
    return True

def doctor_rec():
    # Load the dataset
    file_path = 'datasets/Disease precaution.csv'  # Update with the correct path if needed
    disease_precautions = pd.read_csv(file_path)

    # Expanded doctor data
    doctors = [
        {"name": "Dr. Suman Thapa", "specialty": "General Medicine", "email": "suman.thapa@gmail.com", "phone": "9801234567"},
        {"name": "Dr. Anju Shrestha", "specialty": "Cardiology", "email": "anju.shrestha@gmail.com", "phone": "9807654321"},
        {"name": "Dr. Rajesh Adhikari", "specialty": "Dermatology", "email": "rajesh.adhikari@gmail.com", "phone": "9801112233"},
        {"name": "Dr. Nima Gurung", "specialty": "Endocrinology", "email": "nima.gurung@gmail.com", "phone": "9802223344"},
        {"name": "Dr. Priya Maharjan", "specialty": "Pediatrics", "email": "priya.maharjan@gmail.com", "phone": "9803334455"},
        {"name": "Dr. Ravi Khadka", "specialty": "Neurology", "email": "ravi.khadka@gmail.com", "phone": "9804445566"},
        {"name": "Dr. Maya Lama", "specialty": "Infectious Diseases", "email": "maya.lama@gmail.com", "phone": "9805556677"},
        {"name": "Dr. Dipendra Shah", "specialty": "Hematology", "email": "dipendra.shah@gmail.com", "phone": "9806667788"},
        {"name": "Dr. Kabita Koirala", "specialty": "Pulmonology", "email": "kabita.koirala@gmail.com", "phone": "9807778899"},
        {"name": "Dr. Ramesh Sharma", "specialty": "Nephrology", "email": "ramesh.sharma@gmail.com", "phone": "9808889900"},
        {"name": "Dr. Shreya Tamang", "specialty": "Gastroenterology", "email": "shreya.tamang@gmail.com", "phone": "9809991010"},
        {"name": "Dr. Bikash Gurung", "specialty": "Oncology", "email": "bikash.gurung@gmail.com", "phone": "9801011121"},
        {"name": "Dr. Alina Bhandari", "specialty": "Rheumatology", "email": "alina.bhandari@gmail.com", "phone": "9801213141"},
        {"name": "Dr. Kiran Bhattarai", "specialty": "Ophthalmology", "email": "kiran.bhattarai@gmail.com", "phone": "9801415161"},
        {"name": "Dr. Sarita Pokharel", "specialty": "ENT", "email": "sarita.pokharel@gmail.com", "phone": "9801617181"}
    ]

    # Mock hospital data
    hospitals = [
        {"name": "Norvic International Hospital", "address": "Thapathali, Kathmandu", "phone": "+977 1 4252922"},
        {"name": "Grande International Hospital", "address": "Dhapasi, Kathmandu", "phone": "+977 1 4381047"},
        {"name": "Manipal Teaching Hospital", "address": "Pokhara, Nepal", "phone": "+977 61 526416"},
        {"name": "Bir Hospital", "address": "Ratna Park, Kathmandu", "phone": "+977 1 4221119"},
        {"name": "Patan Hospital", "address": "Lagankhel, Lalitpur", "phone": "+977 1 5522278"},
        {"name": "Nepal Medical College Teaching Hospital", "address": "Attarkhel, Kathmandu", "phone": "+977 1 4911008"},
        {"name": "B&B Hospital", "address": "Gwarko, Lalitpur", "phone": "+977 1 5533206"},
        {"name": "KIST Medical College", "address": "Imadol, Lalitpur", "phone": "+977 1 5201681"}
    ]

    # Function to display recommendations and suggestions
    def recommendations_and_suggestions():
        st.title("🧬 Recommendations and Suggestions")

        # Ask user to input the disease
        disease_input = st.session_state.predicted_dises
        
        if st.button("Get Recommendations"):
            #show recommended doctors
                st.subheader("Recommended Doctors")
                st.write(f"Specialized Doctors for {disease_input.capitalize()}:")
                selected_doctors = random.sample(doctors, k=min(3, 5))

                for doc in selected_doctors:
                    st.markdown(f"""
                    - {doc['name']}  
                    Specialty: {doc['specialty']}  
                    Email: {doc['email']}  
                    Phone: {doc['phone']}  
                    """)

                # Show nearby hospitals
                st.subheader("Nearby Hospitals")
                st.write("Hospitals you can visit:")
                for hospital in hospitals:
                    st.markdown(f"""
                    - {hospital['name']}  
                    Address: {hospital['address']}  
                    Phone: {hospital['phone']}  
                    """)
                
                # Additional Call-to-action
                st.markdown("""
                ---
                For further guidance, consult your nearest healthcare professional.
                """)
    recommendations_and_suggestions()

def sympotms_analyzer():
    if analyzer():
        doctor_rec()


def fetch_profile(user_name):
    try:
        with sq.connect('profiles.db') as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT full_name, age, gender, height, weight 
                FROM profiles WHERE user_name = ?
            """, (user_name,))
            return cursor.fetchone()
    except Exception as e:
        st.error(f"Error fetching profile: {e}")
        return None

def update_profile_in_db(user_name, full_name, age, gender, height, weight):
    try:
        with sq.connect('profiles.db') as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE profiles 
                SET full_name = ?, age = ?, gender = ?, height = ?, weight = ?
                WHERE user_name = ?
            """, (full_name, age, gender, height, weight, user_name))
            conn.commit()
            st.success("Profile updated successfully!")
            return True
    except Exception as e:
        st.error(f"Error updating profile: {e}")
        return False

def update_profile():
    profiles_set()
    st.sidebar.markdown("### Navigations")
    st.sidebar.divider()
    st.sidebar.button("Back", on_click=lambda: setattr(st.session_state, 'page', 'mainn_page'))
    st.subheader("Update Your Profile")

    user_name = st.session_state.user_name
    profile = fetch_profile(user_name)

    if profile:
        full_name, age, gender, height, weight = profile
        with st.form(key="update_profile_form"):
            full_name = st.text_input("Full Name", value=full_name)
            age = st.number_input("Age", min_value=1, step=1, value=age)
            gender = st.radio("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(gender))
            height = st.number_input("Height (in m)", min_value=1.0, step=0.1, value=height)
            weight = st.number_input("Weight (in kg)", min_value=1.0, step=0.1, value=weight)
            
            submitted = st.form_submit_button("Update")

            if submitted:
                if update_profile_in_db(user_name, full_name, age, gender, height, weight):
                    st.session_state.page = 'mainn_page'
                    st.rerun()
    else:
        st.warning("Profile not found. Please set up your profile first.")




def get_random_quote():
            quotes = [
                "Take care of your body. It’s the only place you have to live. – Jim Rohn",
                "Health is the crown on the well person’s head that only the ill person can see. – Robin Sharma",
                "Your health is an investment, not an expense. – Unknown",
                "A healthy outside starts from the inside. – Robert Urich",
                "It is health that is real wealth and not pieces of gold and silver. – Mahatma Gandhi",
                "To enjoy the glow of good health, you must exercise. – Gene Tunney",
                "The groundwork for all happiness is good health. – Leigh Hunt",
                "Wellness is not a medical fix but a way of living. – Greg Anderson",
                "You don’t have to be extreme, just consistent. – Unknown",
                "Every time you eat or drink, you are either feeding disease or fighting it. – Heather Morgan",
                "The greatest wealth is health. – Virgil",
                "Health is a state of body. Wellness is a state of being. – J. Stanford",
                "A fit body, a calm mind, a house full of love. These things cannot be bought—they must be earned. – Naval Ravikant",
                "Take care of yourself – you are your greatest asset. – Unknown",
                "Physical fitness is the first requisite of happiness. – Joseph Pilates"
            ]
            return random.choice(quotes)

def main_page():
    st.sidebar.markdown(f"# Welcome {(st.session_state.user_name).upper()}!")
    st.sidebar.markdown("### Navigations")
    st.sidebar.divider()
    st.sidebar.button('Symptoms Analyzer', on_click=lambda: setattr(st.session_state, 'page', 'symptoms_analyzer'))
    st.sidebar.button('History Trend', on_click=lambda: setattr(st.session_state, 'page', 'history'))
    st.sidebar.button('Update Profile', on_click=lambda: setattr(st.session_state, 'page', 'update_profile'))
    st.sidebar.button("Logout", on_click=lambda: setattr(st.session_state, 'page', 'logout'))
    st.markdown("# DASHBOARD")
    st.write()
    st.markdown(
    """
    <hr style="border: 1px solid red; margin: 20px 0;">
    """,
    unsafe_allow_html=True
)
    st.markdown("""
    <style>
        .big-font {
            font-size: 24px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)
    st.write()
    col1, col2, col3 = st.columns(3)
    with col1:
        

# Example usage in the dashboard

        quote = get_random_quote()
        st.markdown(f"## 🌟 Health Tip of the Day:\n> ### {quote}")
    
    with col3:
        st.subheader("User Info")
        # Fetch user data
        user_info = fetch_user_info(st.session_state.user_name)
        if user_info:
            # Display user data
            for key, value in user_info.items():
                st.markdown(f"#### {key}: {value}")
        else:
            st.warning("No personal data found for this user.")
def login1():
    st.title('Login Page')
    st.sidebar.markdown("### Navigation")
    st.sidebar.divider()
    st.sidebar.button("Back", on_click=lambda: setattr(st.session_state, 'page', 'home_page'))
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    st.button("Login", on_click=lambda: proceed(username, password))
    def proceed(username, password):
        if not username or not password:
            st.error("Please enter the username or password!")
        
        else:
            user_id = login(username, password)
            if user_id:
                st.session_state.page = 'mainn_page'
                st.session_state.user_name = username
            else:
                st.error("Invalid username or password.")
def history_tracker():
    # App Title
    st.sidebar.markdown("### Navigations")
    st.sidebar.button("Back", on_click=lambda: setattr(st.session_state, 'page', 'mainn_page'))
    st.sidebar.divider()
    st.title(f"Trend Analysis of {(st.session_state.user_name).upper()}📈!!")

    # Sidebar: User Input Section
    st.sidebar.header("Enter Your today's Health Data")
    today = datetime.today()

    # Input Widgets
    weight = st.sidebar.number_input("Weight (kg)", min_value=30.0, max_value=200.0, step=0.1)
    bp_systolic = st.sidebar.number_input("Systolic BP (mmHg)", min_value=80, max_value=200, step=1)
    bp_diastolic = st.sidebar.number_input("Diastolic BP (mmHg)", min_value=40, max_value=120, step=1)
    glucose_level = st.sidebar.number_input("Glucose Level (mg/dL)", min_value=50.0, max_value=500.0, step=0.1)
    exercise_time = st.sidebar.number_input("Exercise Time (minutes)", min_value=0, max_value=300, step=1)
    if st.sidebar.button("Submit"):
        insert_health_data(st.session_state.user_name ,today, weight, bp_systolic, bp_diastolic, glucose_level, exercise_time)
        st.sidebar.success("Data Submitted Successfully!")

    data = fetch_health_data(st.session_state.user_name)
    # Fetch and display data
    if data:
        df = pd.DataFrame(data, columns=["ID", "User Name", "Date", "Weight", "Systolic BP", "Diastolic BP", "Glucose", "Exercise Time"])
        df["Date"] = pd.to_datetime(df["Date"])
        st.dataframe(df)
        
        # Plotting Trends with Dual Y-Axis
        st.subheader("Trends Over Time (Dual Y-Axis)")
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        ax2 = ax1.twinx()  # Create a twin y-axis
        # Left Y-Axis (Weight and Glucose)
        ax1.plot(df["Date"], df["Weight"], marker="o", label="Weight (kg)", color="blue", linewidth=2)
        ax1.plot(df["Date"], df["Glucose"], marker="o", label="Glucose Level (mg/dL)", color="red", linewidth=2)
        ax1.set_ylabel("Weight (kg) / Glucose Level (mg/dL)", fontsize=12)
        
        # Right Y-Axis (Systolic and Diastolic BP)
        ax2.plot(df["Date"], df["Systolic BP"], marker="o", label="Systolic BP (mmHg)", color="green", linewidth=2, linestyle="--")
        ax2.plot(df["Date"], df["Diastolic BP"], marker="o", label="Diastolic BP (mmHg)", color="orange", linewidth=2, linestyle="--")
        ax2.set_ylabel("Blood Pressure (mmHg)", fontsize=12)
        
        # Titles and Legends
        ax1.set_title("Trends of Health Metrics", fontsize=16)
        ax1.set_xlabel("Date", fontsize=12)
        ax1.legend(loc="upper left")
        ax2.legend(loc="upper right")
        ax1.grid(True)
        
        fig.tight_layout()
        st.pyplot(fig)
    else:
        st.warning("No data found. Please submit your health data.")

def signup1():
    st.title('SignUp Page')
    st.sidebar.markdown("### Navigation")
    st.sidebar.divider()
    st.sidebar.button("Back", on_click=lambda: setattr(st.session_state, 'page', 'home_page'))
    initialize_db()
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    st.button("Signup", on_click=lambda: proceed())
    def proceed():
        with st.spinner("Creating account..."):
            time.sleep(1.5)
        if password == confirm_password:
            if signup(username, password):
                st.session_state.user_name = username
                st.session_state.page = 'personal_data'
            else:
                st.error("Username already exists.")
        else:
            st.error("Passwords do not match.")

# Main page logic
# Main page logic
if st.session_state.page == 'home_page':
    # Set page configuration
    st.set_page_config(page_title="Healthcare App", layout="centered")
    
    # Custom CSS for styling
    st.markdown("""
    <style>
        body {
            background-color: #f7f9fc;
        }
        .header-title {
            font-size: 32px;
            font-weight: bold;
            color: #2e7bcf;
            text-align: center;
            margin-top: 20px;
        }
        .sub-text {
            font-size: 18px;
            color: #555;
            text-align: center;
            margin-bottom: 40px;
        }
        .feature-box {
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            margin-top: 30px;
        }
        .feature {
            background-color: #fff;
            border-radius: 10px;
            padding: 20px;
            margin: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            flex: 1 1 calc(30% - 20px);
            max-width: calc(30% - 20px);
            min-width: 200px;
        }
        .feature h3 {
            color: #2e7bcf;
            font-size: 20px;
        }
        .feature p {
            color: #555;
            font-size: 16px;
        }
        .button-container {
            text-align: center;
            margin-top: 30px;
        }
        .custom-button {
            background-color: #2e7bcf;
            color: #fff;
            border: none;
            padding: 15px 30px;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        .custom-button:hover {
            background-color: #1b4a80;
        }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="header-title">Welcome to Your Healthcare Tracker!</div>', unsafe_allow_html=True)
    st.markdown(
    """
    <hr style="border: 1px solid red; margin: 20px 0;">
    """,
    unsafe_allow_html=True
)
    col1, col2, col3 = st.columns(3)
    with col2:
        st.image('static/logo1.jpg',use_container_width=True)


    st.markdown('<div class="text">Manage your health with ease, track symptoms, and make informed decisions with insightful analytics.</div>', unsafe_allow_html=True)

    # Feature boxes
    st.markdown("""
    <div class="feature-box">
        <div class="feature">
            <h3>Track Your Health Data</h3>
            <p>Easily log and monitor daily health metrics like blood pressure, sugar levels, and more.</p>
        </div>
        <div class="feature">
            <h3>Symptom Analyzer</h3>
            <p>Predict potential conditions with our advanced symptom analysis tool.</p>
        </div>
        <div class="feature">
            <h3>Personalized Insights</h3>
            <p>Visualize health trends to make better lifestyle and medical decisions.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Call to action
    
    st.sidebar.markdown("### Navigations")
    st.sidebar.divider()
    st.sidebar.button("Login", on_click=lambda: setattr(st.session_state, 'page', 'login'))
    st.sidebar.button("SignUp", on_click=lambda: setattr(st.session_state, 'page', 'sign_up'))
    
elif st.session_state.page == 'login':
    login1()
elif st.session_state.page =='sign_up':
    signup1()
elif st.session_state.page == 'personal_data':
    personal_data()
elif st.session_state.page == 'mainn_page':
    main_page()
elif st.session_state.page == 'symptoms_analyzer':
    sympotms_analyzer()
elif st.session_state.page == 'update_profile':
    update_profile()
elif st.session_state.page == 'logout':
    st.markdown("### Sure, you want to logout?")
    col1, col2 = st.columns(2)
    with col1:
    
        st.button("Confirm", on_click=lambda: setattr(st.session_state, 'page', 'home_page'))
    with col2:
        st.button('No', on_click=lambda: setattr(st.session_state, 'page', 'mainn_page'))
elif st.session_state.page == 'history':
    history_tracker()