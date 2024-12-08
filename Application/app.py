import boto3
from flask import Flask, render_template, request
from pymysql import connections
import os
import logging

app = Flask(__name__)

# Database Configuration
DBHOST = os.environ.get("DBHOST") or "localhost"
DBUSER = os.environ.get("DBUSER") or "root"
DBPWD = os.environ.get("DBPWD") or "password"
DATABASE = os.environ.get("DATABASE") or "employees"
DBPORT = int(os.environ.get("DBPORT", 3306))  # Default to 3306 if DBPORT is not set
YOUR_NAME = os.getenv("YOUR_NAME", "Default Name")  # Get your name from environment variable

# AWS S3 Configuration for background image
S3_BUCKET = os.getenv('S3_BUCKET_NAME', 'background-image-project')  # Use environment variable for S3 bucket
S3_REGION = os.getenv('AWS_REGION', 'us-east-1')  # Set default AWS region to us-east-1
BACKGROUND_IMAGE_KEY = os.getenv('BACKGROUND_IMAGE_KEY', 'OIP.jpeg')  # Object key from ConfigMap
LOCAL_IMAGE_PATH = 'static/background.jpg'  # Local storage path for the downloaded image

# Set up logging
logging.basicConfig(level=logging.INFO)

# Create a connection to the MySQL database
try:
    db_conn = connections.Connection(
        host=DBHOST,
        port=DBPORT,
        user=DBUSER,
        password=DBPWD,
        db=DATABASE
    )
    logging.info("Successfully connected to the database.")
except Exception as e:
    logging.error(f"Error connecting to the database: {str(e)}")
    db_conn = None

# Function to download background image from S3
def download_image_from_s3():
    try:
        # Create 'static' directory if it doesn't exist
        if not os.path.exists('static'):
            os.makedirs('static')

        # Initialize S3 client
        s3 = boto3.client('s3', region_name=S3_REGION)

        # Download image from S3 to local storage
        s3.download_file(S3_BUCKET, BACKGROUND_IMAGE_KEY, LOCAL_IMAGE_PATH)
        logging.info(f"Image successfully downloaded from S3: {S3_BUCKET}/{BACKGROUND_IMAGE_KEY}")
        return LOCAL_IMAGE_PATH
    except Exception as e:
        logging.error(f"Error downloading image from S3: {str(e)}")
        return None

@app.route("/", methods=['GET', 'POST'])
def home():
    background_image_url = download_image_from_s3()
    return render_template('addemp.html', background_image_url=background_image_url, name=YOUR_NAME)

@app.route("/about", methods=['GET', 'POST'])
def about():
    background_image_url = download_image_from_s3()
    return render_template('about.html', background_image_url=background_image_url, name=YOUR_NAME)

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

    if not db_conn:
        return "Database connection not available.", 500

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = f"{first_name} {last_name}"
    except Exception as e:
        logging.error(f"Error inserting data: {str(e)}")
        return "Failed to add employee.", 500
    finally:
        cursor.close()

    background_image_url = download_image_from_s3()
    return render_template('addempoutput.html', name=emp_name, background_image_url=background_image_url)

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    background_image_url = download_image_from_s3()
    return render_template("getemp.html", background_image_url=background_image_url, name=YOUR_NAME)

@app.route("/fetchdata", methods=['GET', 'POST'])
def FetchData():
    emp_id = request.form['emp_id']

    if not db_conn:
        return "Database connection not available.", 500

    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location FROM employee WHERE emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id,))
        result = cursor.fetchone()

        if result:
            output["emp_id"] = result[0]
            output["first_name"] = result[1]
            output["last_name"] = result[2]
            output["primary_skills"] = result[3]
            output["location"] = result[4]
        else:
            output = {
                "emp_id": "N/A",
                "first_name": "Not Found",
                "last_name": "Not Found",
                "primary_skills": "Not Found",
                "location": "Not Found",
            }
    except Exception as e:
        logging.error(f"Error fetching data: {str(e)}")
        return "Failed to fetch data.", 500
    finally:
        cursor.close()

    background_image_url = download_image_from_s3()
    return render_template(
        "getempoutput.html",
        id=output.get("emp_id", "N/A"),
        fname=output.get("first_name", "N/A"),
        lname=output.get("last_name", "N/A"),
        interest=output.get("primary_skills", "N/A"),
        location=output.get("location", "N/A"),
        background_image_url=background_image_url,
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)
