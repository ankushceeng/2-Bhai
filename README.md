# 2-Bhai

# Healthcare Tracker

Welcome to the *Healthcare Tracker*, a Streamlit-powered web application designed to help users monitor their health, analyze symptoms, and make informed decisions based on personalized insights.

## Features

- *User-Friendly Dashboard*: A clean and intuitive interface for navigating between different features.
- *Health Data Logging*: Input daily health metrics such as blood pressure, glucose levels, weight, and exercise time.
- *Symptom Analyzer*: Analyze symptoms to predict potential conditions and receive suggestions for better health.
- *Health Trends Visualization*: Visualize trends over time with interactive graphs for weight, glucose levels, and blood pressure.
- *Profile Management*: Update personal information like age, gender, height, and weight.
- *Personalized Insights*: Receive recommendations and tailored advice based on your health data.

## Tech Stack

- *Frontend*: Streamlit
- *Backend*: SQLite database for user profiles and health data storage
- *Visualization*: Matplotlib and Pandas for plotting trends

## Installation

1. Clone the repository:
   bash
   git clone https://github.com/yourusername/healthcare-tracker.git
   cd healthcare-tracker
   
2. Install the required dependencies:
   bash
   pip install -r requirements.txt
   
3. Run the application:
   bash
   streamlit run main.py
   

## Usage

1. *Login/Signup*: Create a new account or log in with your existing credentials.
2. *Log Health Data*: Enter daily metrics like blood pressure, glucose levels, and more.
3. *Analyze Symptoms*: Use the multi-select feature to choose symptoms and predict conditions. Optionally, specify how long you've been experiencing these symptoms.
4. *View Trends*: Access detailed graphs showing trends in your health metrics over time.
5. *Update Profile*: Modify your personal details for accurate recommendations.

## Screenshots

### Dashboard
![Dashboard](assets/dashboard_screenshot.png)

### Health Trends
![Trends](assets/trends_screenshot.png)

### Symptom Analyzer
![Analyzer](assets/analyzer_screenshot.png)

## Database Structure

The application uses SQLite with the following schema:

### Profiles Table
| Column      | Type    | Description              |
|-------------|---------|--------------------------|
| user_id     | INTEGER | Unique user ID          |
| user_name   | TEXT    | Username                |
| full_name   | TEXT    | Full name               |
| age         | INTEGER | Age                     |
| gender      | TEXT    | Gender                  |
| height      | REAL    | Height in cm            |
| weight      | REAL    | Weight in kg            |

### Health Data Table
| Column         | Type    | Description                 |
|----------------|---------|-----------------------------|
| id             | INTEGER | Unique record ID           |
| user_name      | TEXT    | Username                   |
| date           | DATE    | Date of data entry         |
| systolic_bp    | REAL    | Systolic blood pressure    |
| diastolic_bp   | REAL    | Diastolic blood pressure   |
| glucose        | REAL    | Glucose level             |
| weight         | REAL    | Weight in kg              |
| exercise_time  | INTEGER | Exercise duration in mins |

## Contributing

Contributions are welcome! If you'd like to improve this project, feel free to fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Streamlit team for an excellent web framework
- Hackathon organizers for inspiring the project theme
- Team members for their dedication and teamwork

---

Feel free to reach out with feedback, feature requests, or bug reports. Happy health tracking! 🚀