import streamlit as st
import pandas as pd
import sqlite3
import time
import subprocess



# Connect to your database
def load_data():
    conn = sqlite3.connect('rfid_data.db')  # Replace with your actual database
    df = pd.read_sql_query("SELECT * FROM rfid_data", conn)  # Adjust the query as needed
    conn.close()
    
    # Sort the DataFrame by timestamp in descending order
    # Replace 'timestamp' with the actual name of your time-related column
    df = df.sort_values(by='timestamp', ascending=False)
    
    return df

# Load custom CSS
def load_css():
    st.markdown("""
    <style>
        /* General body styles */
        body {
            background-color: #f8f9fa;
            color: #212529;
            font-family: 'Arial', sans-serif;
        }
        /* Table styles */
        .streamlit-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 20px;  /* Adjusted font size */
        }
        .streamlit-table th {
            background-color: #337ab7;
            color: white;
            text-align: left;
            vertical-align: middle;
            padding: 10px;  /* Adjusted padding for header */
        }
        .streamlit-table td {
            background-color: #fdfdfd;
            border: 1px solid #dee2e6;
            padding: 10px;  /* Adjusted padding for cells */
        }
        .streamlit-table tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .streamlit-table tr:hover {
            background-color: #e2e6ea;
        }
    </style>
    """, unsafe_allow_html=True)


def main():
    # Main Streamlit App
    load_css()  # Load custom CSS

    st.title("RFID and Facial Recognition Data")
    st.subheader("Live data from the RFID database")

    # Create a placeholder for the table
    placeholder = st.empty()

    # Automatic refresh logic
    while True:
        # Load fresh data
        df = load_data()

        # Display the data in the placeholder
        with placeholder.container():
            st.write("<div class='streamlit-table'>", unsafe_allow_html=True)  # Open div for table styling
            st.dataframe(df.style.set_table_attributes('class="streamlit-table"'), use_container_width=True)
            st.write("</div>", unsafe_allow_html=True)  # Close div for table styling

            # Optional: Show some metrics like total number of records  
            st.write(f"Total Records: {len(df)}")

        # Sleep for 2 seconds before the next refresh
        time.sleep(2)


if __name__ == "__main__":
    main()

