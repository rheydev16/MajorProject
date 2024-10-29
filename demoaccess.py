import serial
import sqlite3
import time
from datetime import datetime
import cv2
import face_recognition
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import subprocess
import threading


def rfid_reader():
    # Set up serial communication (adjust 'COM6' for your actual port)
    ser = serial.Serial('COM4', 9600, timeout=1)
    time.sleep(2)  # Wait for serial connection to establish

    # Set up SQLite database connection
    conn = sqlite3.connect('rfid_data.db')
    cursor = conn.cursor()

    # Create a table to store RFID data if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rfid_data (
        rfid_name TEXT NOT NULL,
        timestamp DATETIME DEFAULT (datetime('now', 'localtime')),
        access_status TEXT NOT NULL
    )
    ''')
    conn.commit()

    # Initialize known face encodings and names
    known_face_encodings = []
    known_face_names = []

    # Load known faces and their names here
    known_person1_image = face_recognition.load_image_file("reference.jpg")
    known_person1_encoding = face_recognition.face_encodings(known_person1_image)[0]

    # Add the known face encodings and names
    known_face_encodings.append(known_person1_encoding)
    known_face_names.append("Wedo")  # Add your known person's name here

    def store_rfid_data(name, access_status):
        # Insert RFID name, timestamp, and access status into the database
        local_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get local time in desired format
        cursor.execute('INSERT INTO rfid_data (rfid_name, timestamp, access_status) VALUES (?, ?, ?)', 
                    (name, local_time, access_status))
        conn.commit()
        # Optionally print the inserted data
        # print(f"Inserted RFID Name: {name}, Access Status: {access_status}, Timestamp: {local_time}")  

    def recognize_face():
        # Start capturing video from the webcam
        video_capture = cv2.VideoCapture(0)
        
        # Capture a single frame of video
        ret, frame = video_capture.read()

        if not ret:
            print("Failed to capture image from webcam.")
            return None

        # Find all face locations and face encodings in the current frame
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        # Variable to store match information
        found_match = False
        name = "Unknown"

        if face_encodings:  # Check if face_encodings list is not empty
            # Loop through each face found in the frame
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # Check if the face matches any known faces
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]
                    print(f"Match found: {name}")  # Print match in the terminal
                    found_match = True  # Set match found to true
                    break  # Exit the loop if a match is found

            # Only draw the rectangle and put text if a face was found
            if found_match:
                # Draw a box around the face and label with the name
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                print("Face recognition successful.")
        else:
            print("No face found in the image.")

        # Display the resulting frame for a few seconds
        cv2.imshow("Video", frame)
        cv2.waitKey(3000)  # Display for 3 seconds

        # Release the video capture object
        video_capture.release()
        cv2.destroyAllWindows()

        return name  # Return the recognized name

    def send_email(subject, content):
        # Email Configuration
        sender_email = "weedska11@gmail.com"
        receiver_email = "rheyrabusa200116@gmail.com"
        app_password = "cwvc nixu dldy wfxt"  # Use the App Password generated from Google

        # Create a multipart email message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject

        # Attach the email content
        message.attach(MIMEText(content, "plain"))

        try:
            # Connect to Gmail's SMTP server
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
                server.login(sender_email, app_password)  # Use App Password for login
                server.sendmail(sender_email, receiver_email, message.as_string())  # Send the email
                print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {str(e)}")

    while True:
        if ser.in_waiting > 0:
            # Read the RFID UID and name from the serial connection
            rfid_data = ser.readline().decode('utf-8').strip()
            print(f"Received RFID data: '{rfid_data}'")  # Debug print to check received data
            
            # Split and validate the data
            rfid_parts = rfid_data.split(' ')
            if len(rfid_parts) == 2:  # Ensure exactly two parts are received
                rfid_uid, rfid_name = rfid_parts  # Split UID and name
                print(f"RFID UID read: {rfid_uid}, Name: {rfid_name}")  # Print the read UID and name

                # Call face recognition and check if the names match
                recognized_name = recognize_face()

                # Check if the names match
                if (rfid_name.lower() == "wedo" and recognized_name.lower() != "wedo") or \
                (rfid_name.lower() == "john" and recognized_name.lower() != "john"):
                    access_status = "Denied"
                    print("Access Denied")
                    subject = "Access Denied Notification"
                    content = f"Access Denied for {rfid_name}.\nFace recognition result: {recognized_name}."
                    send_email(subject, content)  # Send email notification
                else:
                    access_status = "Granted"
                    print("Access Granted")

                # Store name and access status in the database
                store_rfid_data(rfid_name, access_status)
            else:
                print("Invalid RFID data format received.")
        
        time.sleep(1)

def run_streamlit():
    subprocess.run(["streamlit", "run", "demoapp.py"])
    

def main():
    # Create threads for RFID reader and Streamlit
    rfid_thread = threading.Thread(target=rfid_reader)
    streamlit_thread = threading.Thread(target=run_streamlit)

    # Start both threads
    rfid_thread.start()
    streamlit_thread.start()

    # Keep the main thread alive while the other threads are running
    rfid_thread.join()
    streamlit_thread.join()

if __name__ == "__main__":
    main()

# Close the SQLite connection and serial port when done
# Note: These lines will never be reached in the infinite loop,
# but for a real application, ensure a safe exit mechanism.
# conn.close()
# ser.close()
