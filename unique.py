import csv

CSV_FILE_PATH = 'atom_connections.csv'

def print_unique_values_from_csv(file_name):
    unique_values = set()  # Set to store unique values
    
    try:
        with open(file_name, mode='r', newline='') as file:
            reader = csv.reader(file)
            
            # Iterate over rows and add each value to the set
            for row in reader:
                for value in row:
                    unique_values.add(value.strip())  # Add the stripped value to remove extra whitespace

        # Print out the unique values
        print("Unique values in the CSV file:")
        for value in unique_values:
            print(value)
    
    except Exception as e:
        print(f"Error reading the CSV file: {e}")

# Example usage:
print_unique_values_from_csv(CSV_FILE_PATH)
