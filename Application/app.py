from flask import Flask, render_template, request
from pymysql import connections
import os
import random
import argparse
import boto3  # AWS SDK to interact with S3
import logging

app = Flask(__name__)

DBHOST = os.environ.get("DBHOST") or "localhost"
DBUSER = os.environ.get("DBUSER") or "root"
DBPWD = os.environ.get("DBPWD") or "password"
DATABASE = os.environ.get("DATABASE") or "employees"
COLOR_FROM_ENV = os.environ.get('APP_COLOR') or "lime"
DBPORT = int(os.environ.get("DBPORT"))
YOUR_NAME = os.getenv("YOUR_NAME", "Default Name")  # Get your name from environment variable

# Define the supported color codes (moved above all references)
color_codes = {
    "red": "#e74c3c",
    "green": "#16a085",
    "blue": "#89CFF0",
    "blue2": "#30336b",
    "pink": "#f4c2c2",
    "darkblue": "#130f40",
    "lime": "#C1FF9C",
}

# Create a connection to the MySQL database
db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD,
    db=DATABASE
)
output = {}
table = 'employee'

# AWS S3 Configuration for background image
S3_BUCKET = os.getenv('S3_BUCKET_NAME', 'background-image-project')  # Use environment variable for S3 bucket
S3_REGION = os.getenv('AWS_REGION', 'us-east-1')  # Set default AWS region to us-east-1
LOCAL_IMAGE_PATH = 'static/background.jpg'  # Local storage path for the downloaded image

# Set up logging
logging.basicConfig(level=logging.INFO)

# Generate a random color
COLOR = random.choice(list(color_codes.keys()))

@app.route("/", methods=['GET', 'POST'])
def home():
    # Retrieve the background image URL from environment variable (use default if not found)
    background_image_url = os.getenv('BACKGROUND_IMAGE_URL', 's3://background-image-project/OIP.jpeg')

    # Log the background image URL
    logging.info(f"Background Image URL: {background_image_url}")

    try:
        # Create 'static' directory if it doesn't exist to store images
        if not os.path.exists('static'):
            os.makedirs('static')

        # Set up boto3 client to interact with S3
        s3 = boto3.client('s3', region_name=S3_REGION)

        # Extract the object key from the S3 URL (this is the filename of the image)
        object_key = background_image_url.split('/')[-1]

        # Download the image from S3 and store it in the 'static/' folder
        s3.download_file(S3_BUCKET, object_key, LOCAL_IMAGE_PATH)
        logging.info(f"Downloaded image from S3: {background_image_url}")

        # Pass the local image path to the template
        background_image_url = LOCAL_IMAGE_PATH
    except Exception as e:
        logging.error(f"Failed to download image from S3: {str(e)}")
        background_image_url = None

    # Render the 'addemp' page, passing the image URL
    return render_template('addemp.html', background_image_url=background_image_url, name=YOUR_NAME)


@app.route("/about", methods=['GET', 'POST'])
def about():
    # Retrieve the background image URL from environment variable (use default if not found)
    background_image_url = os.getenv('BACKGROUND_IMAGE_URL', 's3://background-image-project/OIP.jpeg')

    # Log the background image URL
    logging.info(f"Background Image URL: {background_image_url}")

    try:
        # Create 'static' directory if it doesn't exist to store images
        if not os.path.exists('static'):
            os.makedirs('static')

        # Set up boto3 client to interact with S3
        s3 = boto3.client('s3', region_name=S3_REGION)

        # Extract the object key from the S3 URL (this is the filename of the image)
        object_key = background_image_url.split('/')[-1]

        # Download the image from S3 and store it in the 'static/' folder
        s3.download_file(S3_BUCKET, object_key, LOCAL_IMAGE_PATH)
        logging.info(f"Downloaded image from S3: {background_image_url}")

        # Pass the local image path to the template
        background_image_url = LOCAL_IMAGE_PATH
    except Exception as e:
        logging.error(f"Failed to download image from S3: {str(e)}")
        background_image_url = None

    # Render the 'about' page, passing the image URL
    return render_template('about.html', background_image_url=background_image_url, name=YOUR_NAME)

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = f"{first_name} {last_name}"
    finally:
        cursor.close()

    print("all modification done...")
    return render_template('addempoutput.html', name=emp_name, color=color_codes[COLOR])

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html", color=color_codes[COLOR], name=YOUR_NAME)

@app.route("/fetchdata", methods=['GET', 'POST'])
def FetchData():
    emp_id = request.form['emp_id']

    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location from employee where emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id,))
        result = cursor.fetchone()

        # Add No Employee found form
        output["emp_id"] = result[0]
        output["first_name"] = result[1]
        output["last_name"] = result[2]
        output["primary_skills"] = result[3]
        output["location"] = result[4]
    except Exception as e:
        print(e)
    finally:
        cursor.close()

    return render_template("getempoutput.html", id=output["emp_id"], fname=output["first_name"],
                           lname=output["last_name"], interest=output["primary_skills"], location=output["location"], name=YOUR_NAME)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)

