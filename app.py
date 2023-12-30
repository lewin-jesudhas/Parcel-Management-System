#Importing the necessary modules
from flask import Flask, render_template, request, redirect, url_for
import csv
import pickle
import random
import string
import os
import datetime
# import cv2
import json
import re
from JSONHandler import JSONHandler
from qr_generation import get_tracking_number, create_tracking_number
from QRHandler import QRHandler
import Validations

detector = cv2.QRCodeDetector()

app = Flask(__name__)

JSON_HANDLER_INSTANCE = JSONHandler()

@app.route('/')
def reroute():
    #Routing to the homepage
    return render_template("homepage.html")


@app.route('/employee/login', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'POST':
        employee_id = request.form['Employee ID']
        password = request.form['Password']

        # Validate employee ID using regex
        employee_id_strategy = Validations.RegexEmployeeIDValidation()
        password_strategy = Validations.RegexPasswordValidation()

        password_context = Validations.ValidationContext(password_strategy, password)
        employee_context = Validations.ValidationContext(employee_id_strategy, employee_id)

        if not (password_context.validate() and employee_context.validate()):
            return render_template('dashboard.html', error="Invalid Employee ID or Password format.")

        # Check if the employee ID exists in the JSON data
        with open('employee_data.json', 'r') as file:
            employees = JSON_HANDLER_INSTANCE.load(file)

            if employee_id in employees.items and employees[employee_id] == password:
                return render_template('dashboard.html', employee={'Employee ID': employee_id, 'Password': password})

        error = 'Invalid employee ID or password'
        return render_template('login.html', error=error)

    return render_template('login.html')



@app.route('/employee/generateid', methods=['GET', 'POST'])
def generate_id():
    #Generating usernames and passwords for new employees
    if request.method == 'POST':
        num_new_employees = int(request.form['num_employees'])

        for _ in range(num_new_employees):
            emp = Employee()
            i = iter(emp)
            employee_id, password = next(i)
            employee_data[employee_id] = password

        store_employee_data()

        return render_template('result.html', employee_data=employee_data.items())

    return render_template('index.html')


def generate_password(length=8):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


# Function to create a new employee
class Employee:
    def __iter__(self):
        return self
        
    def __next__(self):
        employee_id = str(len(employee_data) + 1)
        password = generate_password()
        return employee_id, password


def load_employee_data():
    file_path = 'employee_data.json'
    try:
        with open(file_path, 'r') as file:
            employee_data.update(JSON_HANDLER_INSTANCE.load(file))
    except (FileNotFoundError, json.JSONDecodeError):
        # Handle cases where the file doesn't exist or is empty or has invalid JSON format
        print("JSON file is empty, does not exist, or has invalid format.")


def store_employee_data():
    file_path = 'employee_data.json'

    with open(file_path, 'w') as file:
        JSON_HANDLER_INSTANCE.dump(employee_data, file)   

#Continue from here
@app.route('/employee/datewisedelivery')
def display_delivery_data():
    with open('date_delivery.json', 'r') as file:
        # Load the entire JSON file
        data = JSON_HANDLER_INSTANCE.load(file)

    # Assuming the data is a dictionary where keys are tracking IDs and values are delivery details
    deliveries = [{"Tracking ID": tracking_id, **details} for tracking_id, details in data.items()]

    return render_template('date_display.html', deliveries=deliveries)


# @app.route('/employee/reschedule')
# def display_details():
#     # Read the contents of the file
#     with open('rescheduled_details.txt', 'r') as file:
#         content = file.read()

#     # Split the content into separate details
#     details = content.strip().split('\n\n')

#     return render_template('reschedule_display.html', details=details)


@app.route('/employee/customerdetails')
def customer_details():
    return render_template('write_file_test.html')


@app.route('/employee/submit', methods=['POST'])
def submit():
    try:
        create_tracking_number()
        track_id = get_tracking_number()
        sender_name = request.form['sender_name']
        sender_phone = request.form['sender_phone']
        sender_location = request.form['sender_location']
        receiver_address = request.form['receiver_address']
        receiver_phone = request.form['receiver_phone']
        current_location = request.form['current_location']

        # Define a regex pattern for exactly 10 digits
        phone_number_pattern = re.compile(r'^\d{10}$')

        # Validate sender_phone
        if not phone_number_pattern.match(sender_phone):
            raise ValueError("Invalid sender phone number format")

        # Validate receiver_phone
        if not phone_number_pattern.match(receiver_phone):
            raise ValueError("Invalid receiver phone number format")
        # Create a dictionary to hold the tracking details
        tracking_data = {
            track_id: [
                sender_name,
                sender_phone,
                sender_location,
                receiver_address,
                receiver_phone,
                current_location
            ]
        }

        old_data = JSON_HANDLER_INSTANCE.load(open('data.json', 'r'))
        old_data.update(tracking_data)
        # Convert the dictionary to a JSON string
        JSON_HANDLER_INSTANCE.dump(old_data, open('data.json', 'w'))

        return render_template("dashboard.html")

    except ValueError as e:
        # Pass the error message to the template
        return render_template("details_customer.html", error_message=str(e))


def write_tracking_details(tracking_id, sender_name, sender_phone, sender_location, receiver_address, receiver_phone, current_location):
    # Create a dictionary to hold the tracking details
    current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    tracking_data = {
        tracking_id:{
        "Sender Name": sender_name,
        "Sender Phone": sender_phone,
        "Sender Location": sender_location,
        "Receiver Address": receiver_address,
        "Receiver Phone": receiver_phone,
        "Current Location": current_location,
        "Date": current_date,
        "Status": "Delivered"}
    }
    old_data2 = JSON_HANDLER_INSTANCE.load(open('date_delivery.json', 'r'))
    old_data2.update(tracking_data)
    # Convert the dictionary to a JSON string
    JSON_HANDLER_INSTANCE.dump(old_data2, open('date_delivery.json', 'w'))
    # Convert the dictionary to a JSON string
    #json_data = JSON_HANDLER_INSTANCE.dumps(tracking_data)

@app.route('/employee/readqr')
def readqr():
    return render_template('qr_read.html')


@app.route('/employee/scan_qr', methods=['POST'])
def scan_qr():
    # Scanning the QR code at the time of delivery
    tracking_data = []
    
    with open('data.json', 'r') as file:
        #Error may be this
        tracking_data = JSON_HANDLER_INSTANCE.load(file)

    qr = QRHandler(tracking_data)

    result = qr.scan_qr()

    if result is None:
        return render_template('otperror.html')
    else:
        return render_template('otpverification.html', otp=result["otp"], tracking_id=result["tracking_id"])


@app.route('/employee/otp_verification', methods=['POST'])
def otp_verification():
    #To check if the OTP entered is correct
    entered_otp = int(request.form['otp'])
    original_otp = int(request.form['original_otp'])
    tracking_id = request.form['tracking_id']

    if entered_otp == original_otp:
        tracking_info = get_tracking_info(tracking_id)
        if tracking_info:
            write_tracking_details(*tracking_info)
            return render_template('otpsuccess.html', tracking_id=tracking_id)

    return render_template('otperror.html')


def get_tracking_info(tracking_id):
    with open('data.json', 'r') as file:
        tracking_data = JSON_HANDLER_INSTANCE.load(file)

    tracking_info = tracking_data.get(tracking_id)
    
    if tracking_info:
        return (
            tracking_id,
            tracking_info[0],  # Sender Name
            tracking_info[1],  # Sender Phone
            tracking_info[2],  # Sender Location
            tracking_info[3],  # Receiver Address
            tracking_info[4],  # Receiver Phone
            tracking_info[5]   # Current Location
        )
    return None


@app.route('/employee/scanqrlocation')
def scanqrlocation():
    return '''
    <h1>QR Code Detection</h1>
    <form action="/employee/process" method="POST">
        <label for="location">Current Location:</label>
        <input type="text" id="location" name="location" required>
        <br>
        <input type="submit" value="Submit">
    </form>
    '''


@app.route('/employee/process', methods=['POST'])
def process():
    location = request.form['location']

    # Read the existing contents of data.json
    with open('data.json', 'r') as file:
        tracking_data = JSON_HANDLER_INSTANCE.load(file)

    # Initialize the webcam
    cap = cv2.VideoCapture(0)

    # Variable to keep track of whether QR code is detected
    qr_code_detected = False

    while True:
        # Capture frames from the webcam
        ret, frame = cap.read()

        if not ret:
            break

        # Convert the frame to grayscale for QR code detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect and decode the QR code
        data, bbox, _ = detector.detectAndDecode(gray)

        # Check if there is a QR code in the frame
        if bbox is not None:
            # Display the frame with lines
            for i in range(len(bbox)):
                # Draw all lines
                cv2.line(frame, tuple(bbox[i][0].astype(int)), tuple(bbox[(i+1) % len(bbox)][0].astype(int)), color=(255, 0, 0), thickness=2)

            if data:
                print("[+] QR Code detected, data:", data)
                qr_code_detected = True

                # Update the location for the detected tracking ID
                if data in tracking_data:
                    tracking_data[data][5] = location  # Update the current_location field

                    # Write the updated contents back to data.json
                    with open('data.json', 'w') as file:
                        JSON_HANDLER_INSTANCE.dump(tracking_data, file)

                    break

        if qr_code_detected:
            break

    # Release the webcam
    cap.release()

    return 'QR code detection completed.'



class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def insert(self, data):
        # To insert the addresses and phone numbers
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

class HashMap:
    # The tracking ID is the key and the Linked List is the value
    '''
    in the has map the key is the unique tracking id and the linked
    list contains the details such as sender and receiver addresses, 
    phone numbers and location.'''
    def __init__(self):
        self.hashmap = {}

    def put(self, key, value):
        self.hashmap[key] = value

    def get(self, key):
        return self.hashmap.get(key)

    def remove(self, key):
        if key in self.map:
            del self.map[key]

    def contains_key(self, key):
        return key in self.map

    def keys(self):
        return self.map.keys()

    def values(self):
        return self.map.values()

    def items(self):
        return self.map.items()

    def add_sender(self, key, sender):
        if key in self.map:
            self.map[key]["Sender"] = sender
        else:
            self.map[key] = {"Sender": sender}

    def add_receiver(self, key, receiver):
        if key in self.map:
            self.map[key]["Receiver"] = receiver
        else:
            self.map[key] = {"Receiver": receiver}

    def remove_sender(self, key):
        if key in self.map and "Sender" in self.map[key]:
            del self.map[key]["Sender"]

    def remove_receiver(self, key):
        if key in self.map and "Receiver" in self.map[key]:
            del self.map[key]["Receiver"]

hashmap = HashMap()

# Populate the HashMap with data from the JSON file
def populate_hashmap(filename):
    with open(filename, 'r') as file:
        data = JSON_HANDLER_INSTANCE.load(file)

    for tracking_id, details in data.items():
        hashmap.put(tracking_id, details)


@app.route('/home')
def homepage():
    #Landing Page
    return render_template("frontpage.html")


# Route for the index page
@app.route('/trackparcel', methods=["GET"])
def trackparcel():
    #To redirect to page where the tracking ID is entered
    return render_template('landing.html')


@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")


@app.route("/contact")
def contactus():
    return render_template("contactus.html")


@app.route("/feedback", methods=["GET"])
def feedback():
    return render_template("rating.html")


@app.route('/submit_review', methods=['POST'])
def submit_review():
    name = request.form['name']
    rating = request.form['rating']
    review = request.form['review']
    feedback = request.form['feedback']

    # Create a dictionary to hold the review data
    review_data = {
        "Name": name,
        "Rating": rating,
        "Review": review,
        "Feedback": feedback
    }

    # Convert the dictionary to a JSON string
    json_data = JSON_HANDLER_INSTANCE.dumps(review_data)
    #print(json_data)

    # Save the JSON data to a file
    try:
        with open('reviews.json', 'a') as file:
            file.write(json_data + '\n')
    except Exception as e:
        print(f"Error: {e}")

    return "Thank you for your review!"


# Route for handling the form submission
@app.route('/track', methods=['POST'])
def track():
    tracking_id = request.form['tracking_id']
    return redirect(url_for('details', tracking_id=tracking_id))


# Route for displaying the parcel details
@app.route('/details/<tracking_id>')
def details(tracking_id):
    #Searching for the details with the help of a hashmap
    data = hashmap.get(tracking_id)
    print(data)
    if data is not None:
        return render_template('details_customer.html', data=data)
    else:
        return render_template('error.html', tracking_id=tracking_id)

#Driver Code
if __name__ == '__main__':
        # Initialize the employee data dictionary
    employee_data = {}
    # Load existing employee data from the CSV file
    load_employee_data()
    #filename = 'data.json'
    filename='data.json'
    populate_hashmap(filename)
    app.run(debug=True)