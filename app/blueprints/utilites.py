from datetime import datetime

def get_formatted_date():
    # Get today's date
    today = datetime.today()
    
    # Format date as '12 March 2024'
    formatted_date = today.strftime('%d %B %Y')
    
    return formatted_date

def parse_values_bytype(atype, astr):
    """parse three type of inputs
        single value
        a list of values: ","
        a range: start:stop:step
    """

    if ":" in astr:
        start, stop, step = map(int, astr.split(":"))
        alist = list(range(start,stop,step))
        if not stop in alist:
            alist.append(stop)
        alist = map(str, alist)
        alist = list(alist)
    elif "," in astr:
        alist = astr.split(",")
    else:
        alist = [astr]
    
    return alist

import json
import os

def append_to_json(file_path, new_data):
    """
    Appends new data to a JSON file. If the file doesn't exist, it creates a new one.

    :param file_path: Path to the JSON file.
    :param new_data: Data to append (must be a dictionary or list).
    """
    if os.path.exists(file_path):
        # Load existing data
        with open(file_path, 'r') as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
    else:
        # If the file doesn't exist, initialize with an empty list
        existing_data = []

    # Append new data
    if isinstance(existing_data, list):
        existing_data.append(new_data)
    elif isinstance(existing_data, dict):
        existing_data.update(new_data)
    else:
        raise ValueError("Existing JSON data must be a list or dictionary.")

    # Write updated data back to the file
    with open(file_path, 'w') as file:
        json.dump(existing_data, file, indent=4)

def main():
    print("Today:", get_formatted_date())

if __name__=="__main__":
    main()
