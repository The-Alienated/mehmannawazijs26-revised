''' The purpose of this software is to log information for Mehman Nawazi:This script will create a 
database and a table to store relevant data.

GOALS:
- one of each table, one of each item, one of each meal
- total inventory, init inventory, average use (per table)
- summary inventory of each meal, each day
- database format, easy to use
- 10 stations ++ volunteer مارقی
- initial inventory, each additional quantity (loop to allow for as much additions as 
  needed, closing inventory (subtract (init+additions)-closing)
- aggregate for each station; combine at the end
'''
#written by: Anees Ahmad Rana for Mehman Nawazi JS26
#75% written without the aid of artificial intelligence, 25% written with the aid of artificial intelligence
import sqlite3
from click import option
import streamlit as st
import pandas as pd

#BASIC SQL CODE

# define connection to a database
connection = sqlite3.connect('mehman_nawazi.db')

# create a cursor object to execute SQL commands
cursor = connection.cursor()

# create a table to log all stations and their current inventory
#name of the table is 'spreadsheet'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS spreadsheet ( 
        day INTEGER NOT NULL,
        station_id INTEGER,
        item_name TEXT NOT NULL,
        initial_inventory INTEGER NOT NULL,
        additions INTEGER NOT NULL,
        closing_inventory INTEGER NOT NULL,
        used INTEGER GENERATED ALWAYS AS (initial_inventory + additions - closing_inventory),
        PRIMARY KEY (day, station_id, item_name)
    )
''')

#finally commit the changes and close the connection
connection.commit()
print("Database and table created successfully.")

#not so BASIC STREAMLIT CODE

# basic aesthetic information for the streamlit app
LOGO_URL_LARGE = "https://i.ibb.co/0yTNybwR/logo-1.png"

st.logo(
    LOGO_URL_LARGE,
    size = "large",
)
st.title("Mehman Nawazi Inventory Management System")

#Provide the Option to Select the Day, Type of Inventory, and Station
with st.expander("Basic Information", expanded=True):
    day_option = st.selectbox(
        "What day of inventory are you logging?",
        ("Friday", "Saturday", "Sunday")
    )

    type_option = st.selectbox(
        "What type of inventory are you logging?",
        ("initial inventory", "additions", "closing inventory"),
    )

    station_option = st.selectbox(
        "What Station are you visiting?",
        ("Truck Inventory", "Station 1 - Non Spicy", "Station 2", "Station 3", "Station 4", "Station 5", "Station 6", "Station 7", "Station 8", "Station 9", "Station 10", "Volunteer Marquee", "Jalsa Salana Office"),
    )

#Provide the Option to Input the Number of Each Item at the Station
with st.expander("Log Items", expanded=True):
    cups = st.text_input("Cups", value="0", key="cups")
    plates = st.text_input("Plates", value="0", key="plates")
    bowls = st.text_input("Bowls", value="0", key="bowls")
    spoons = st.text_input("Spoons", value="0", key="spoons")
    tissues = st.text_input("Tissues", value="0", key="tissues")

with st.expander("Log Additional Items"):
    jug = st.text_input("Jugs", value="0", key="jugs")
    small_ladels = st.text_input("Small Ladels", value="0", key="small_ladels")
    rice_spoons = st.text_input("Rice Spoons", value="0", key="rice_spoons")
    hairnets = st.text_input("Hairnets", value="0", key="hairnets")
    gloves = st.text_input("Gloves", value="0", key="gloves") # Fixed typo here
    plastic_aprons = st.text_input("Plastic Aprons", value="0", key="plastic_aprons")
    cloth_aprons = st.text_input("Cloth Aprons", value="0", key="cloth_aprons")
    safety_vests = st.text_input("Safety Vests", value="0", key="safety_vests")

#Provide the Option to Submit the Data to the Database
if st.button("Submit Data"):    # insert or update the data into the database; additions should accumulate
    def upsert_item(item_name, value):
        # get existing row if any
        cursor.execute(
            "SELECT initial_inventory, additions, closing_inventory FROM spreadsheet WHERE day=? AND station_id=? AND item_name=?",
            (day_option, station_option, item_name)
        )
        row = cursor.fetchone()
        existing_initial = row[0] if row else 0
        existing_additions = row[1] if row else 0
        existing_closing = row[2] if row else 0

        # determine new values based on type_option
        if type_option == "initial inventory":
            new_initial = int(value)
            new_additions = existing_additions
            new_closing = existing_closing
        elif type_option == "additions":
            new_initial = existing_initial
            new_additions = existing_additions + int(value)
            new_closing = existing_closing
        else:  # closing inventory
            new_initial = existing_initial
            new_additions = existing_additions
            new_closing = int(value)

        cursor.execute('''
            INSERT OR REPLACE INTO spreadsheet (day, station_id, item_name, initial_inventory, additions, closing_inventory)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            day_option,
            station_option,
            item_name,
            new_initial,
            new_additions,
            new_closing
        ))

    # upsert each provided item (Updated to match your new variables!)
    upsert_item("Plates", plates)
    upsert_item("Bowls", bowls)
    upsert_item("Spoons", spoons)
    upsert_item("Cups", cups)
    upsert_item("Tissues", tissues)
    upsert_item("Jugs", jug)
    upsert_item("Small Ladels", small_ladels)
    upsert_item("Rice Spoons", rice_spoons)
    upsert_item("Hairnets", hairnets)
    upsert_item("Gloves", gloves)
    upsert_item("Plastic Aprons", plastic_aprons)
    upsert_item("Cloth Aprons", cloth_aprons)
    upsert_item("Safety Vests", safety_vests)
    
    connection.commit()
    st.success("Data submitted successfully!")

st.divider() #to better divide the segments of the app

# create a dataframe to display the current inventory from the database
df = pd.read_sql_query("SELECT * FROM spreadsheet", connection)
st.dataframe(df) 

#Add a button to hone in on the data for a specific day and station
with st.expander("Filter Data", expanded=True):
    day_filter = st.selectbox(
        "Filter by Day",
        ("All Days", "Friday", "Saturday", "Sunday")
    )

    station_filter = st.selectbox(
        "Filter by Station",
        ("All Stations", "Truck Inventory", "Station 1 - Non Spicy", "Station 2", "Station 3", "Station 4", "Station 5", "Station 6", "Station 7", "Station 8", "Station 9", "Station 10", "Volunteer Marquee", "Jalsa Salana Office")
    )

    if day_filter != "All Days":
        df = df[df["day"] == day_filter]

    if station_filter != "All Stations":
        df = df[df["station_id"] == station_filter]

    st.dataframe(df)

# Provide Option to Export the Database to CSV
def convert_for_download(df):
    return df.to_csv().encode("utf-8")
csv = convert_for_download(df)
button2 = st.download_button(
    label="Download CSV",
    data=csv,
    file_name="data.csv",
    mime="text/csv",
    icon=":material/download:",
)

with st.expander("⚠️ System Administration (Reset Options)"):
    st.warning("Resetting the database will permanently delete all logged rows.")
    confirm_reset = st.checkbox("I understand this will completely clear the current spreadsheet.")
    
    if st.button("Clear All Logs", disabled=not confirm_reset, type="primary"):
        cursor.execute("DELETE FROM spreadsheet")
        connection.commit()
        st.success("Database cleared successfully!")
        st.rerun()
