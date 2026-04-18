# check_file.py

# This script will read the contents of the routes.py file
# and print them to the console. This tells us what is
# actually saved on the disk.

FILE_PATH = 'exercise4/routes.py'

print("--- READING FILE: " + FILE_PATH + " ---")

try:
    with open(FILE_PATH, 'r') as f:
        content = f.read()
        print(content)
except FileNotFoundError:
    print("\nERROR: The file could not be found at that path.")
except Exception as e:
    print(f"\nAn error occurred: {e}")

print("\n--- END OF FILE ---")