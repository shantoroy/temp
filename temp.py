def extract_activity_dates(sheet, headers):
    """
    Extracts a dictionary where keys are activity names and values are lists of dates
    on which the activity is scheduled.

    Args:
        sheet: OpenPyxl worksheet object.
        headers: List of column headers.

    Returns:
        dict: A dictionary with activity names as keys and lists of dates as values.
    """
    # Identify the date columns (columns beyond the fixed headers)
    date_columns = headers[2:]  # Assuming first two columns are not dates

    # Initialize the dictionary to store activities and their dates
    activity_dates = {}

    # Iterate over rows starting from the 6th row
    for row in sheet.iter_rows(min_row=6, values_only=True):
        activity_name = row[0]  # Assuming "Task Name" is the first column
        if not activity_name:
            continue  # Skip rows without an activity name

        # Collect dates for this activity
        dates = [
            date_columns[i - 2]  # Offset index to match date columns
            for i, cell_value in enumerate(row[2:], start=2)
            if cell_value is not None  # Only consider non-empty cells
        ]

        # Add to the dictionary
        activity_dates[activity_name] = dates

    return activity_dates


# Usage Example
# Extract headers from the 5th row
headers = [cell.value for cell in sheet[5]]

# Generate the dictionary of activity dates
activity_dates = extract_activity_dates(sheet, headers)

# Display the result
for activity, dates in activity_dates.items():
    print(f"Activity: {activity}, Dates: {dates}")
