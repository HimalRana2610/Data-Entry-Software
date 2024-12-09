import PySimpleGUI as sg
import sqlite3
from datetime import datetime

# Create a database or connect to one
conn = sqlite3.connect('data_entries.db')
c = conn.cursor()

# Create a table if it doesn't exist
c.execute("""CREATE TABLE IF NOT EXISTS entries (
            sr_no INTEGER PRIMARY KEY,
            date TEXT,
            party_name TEXT,
            amount REAL
            )""")
conn.commit()

# Function to insert data into the table
def insert_data(date, party_name, amount):
    with conn:
        c.execute("INSERT INTO entries (date, party_name, amount) VALUES (?, ?, ?)",
                  (date, party_name, amount))

# Function to get the next serial number
def get_next_sr_no():
    c.execute("SELECT MAX(sr_no) FROM entries")
    result = c.fetchone()[0]
    if result is None:
        return 1
    else:
        return result + 1

# Function to fetch all data from the table
def fetch_all_data():
    c.execute("SELECT * FROM entries")
    return c.fetchall()

# Function to delete a row by serial number
def delete_data(sr_no):
    with conn:
        c.execute("DELETE FROM entries WHERE sr_no=?", (sr_no,))
        conn.commit()

# Function to move focus to the next input field
def focus_next_input(event, current_key, keys_list):
    if event == 'Enter':
        try:
            current_index = keys_list.index(current_key)
            next_key = keys_list[current_index + 1]
            window[next_key].SetFocus()
        except (ValueError, IndexError):
            pass  # Do nothing if there's no next field

# Function to create the window layout
def create_layout():
    layout = [
        [sg.Text('Serial No.'), sg.InputText(key='-SR_NO-', size=(10, 1), disabled=True, default_text=get_next_sr_no())],
        [sg.Text('Date'), sg.InputText(key='-DATE-', size=(20, 1)), sg.CalendarButton('Choose Date', target='-DATE-', format='%d-%m-%Y')],
        [sg.Text('Party Name'), sg.InputText(key='-PARTY_NAME-', size=(40, 1))],
        [sg.Text('Amount'), sg.InputText(key='-AMOUNT-', size=(20, 1))],
        [sg.Button('Submit'), sg.Button('View Data'), sg.Button('Delete Data'), sg.Button('Exit')]
    ]
    return layout

# Function to create the data view window
def create_data_view_window(data):
    headings = ["Serial No.", "Date", "Party Name", "Amount"]
    layout = [
        [sg.Table(values=data, headings=headings, display_row_numbers=False, auto_size_columns=True, num_rows=min(25, len(data)), key='-TABLE-', enable_events=True)],
        [sg.Button('Delete Selected'), sg.Button('Close')]
    ]
    return sg.Window('View Data', layout, modal=True, size=(800, 600))  # Set the size of the data view window

# Create the main window
window = sg.Window('Data Entry Form', create_layout(), size=(600, 400))  # Set the size of the main window

# List of input field keys
input_keys = ['-SR_NO-', '-DATE-', '-PARTY_NAME-', '-AMOUNT-']

# Event loop to process events and get the values of the inputs
while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break

    if event == 'Submit':
        try:
            sr_no = get_next_sr_no()
            date = values['-DATE-']
            party_name = values['-PARTY_NAME-']
            amount = float(values['-AMOUNT-'])

            # Insert data into the database
            insert_data(date, party_name, amount)
            
            # Update the Serial Number field for the next entry
            window['-SR_NO-'].update(get_next_sr_no())

            sg.popup('Data Entered Successfully')
            
            # Clear the input fields
            window['-DATE-'].update('')
            window['-PARTY_NAME-'].update('')
            window['-AMOUNT-'].update('')
        except ValueError:
            sg.popup('Invalid input! Please enter a valid amount.')

    if event == 'View Data':
        data = fetch_all_data()
        data_window = create_data_view_window(data)
        while True:
            event_data, values_data = data_window.read()
            if event_data == sg.WINDOW_CLOSED or event_data == 'Close':
                break

            if event_data == 'Delete Selected':
                selected_row = values_data['-TABLE-']
                if selected_row:
                    sr_no = data[selected_row[0]][0]
                    delete_data(sr_no)
                    data = fetch_all_data()
                    data_window['-TABLE-'].update(values=data)
                    sg.popup('Data Deleted Successfully')

        data_window.close()

    # Move focus to the next input field when Enter is pressed
    for key in input_keys:
        if event == key and window.FindElementWithFocus():
            focus_next_input('Enter', key, input_keys)
            break

# Close the main window and database connection
window.close()
conn.close()
