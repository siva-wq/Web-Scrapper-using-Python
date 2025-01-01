import requests  # To send HTTP requests and fetch webpage content
from bs4 import BeautifulSoup  # For parsing and extracting data from HTML
from io import BytesIO  # To handle in-memory binary streams
from PyPDF2 import PdfReader  # For reading and extracting text from PDF files

# Input regulation and year
r = int(input("Enter regulation (19,20): "))  # Prompt user for regulation (19 or 20)
y = input("Enter year (1, 2, 3, or 4): ")  # Prompt user for year (1st, 2nd, 3rd, or 4th)

# Mapping the numeric year to string format used in the URL
year_mapping = {1: "i", 2: "ii", 3: "iii", 4: "iv"}
y = year_mapping.get(int(y))  # Convert numeric year to URL-compatible string
if r == 19:
    y = "i-year"

# URL to fetch the question papers based on regulation and year
url = "replace" #replace

# Function to extract subject names from the webpage
def extract_subject_names(url):
    response = requests.get(url)  # Send an HTTP GET request to fetch the webpage
    soup = BeautifulSoup(response.text, 'html.parser')  # Parse the HTML content
    subject_names = [td.text.strip() for td in soup.find_all('td') if td.text.strip()]  # Extract text from <td> elements
    return [name for name in subject_names if len(name) > 9]  # Filter names with sufficient length (likely subject names)

# Function to scrape PDF links for a specific subject
def scrape_pdf_links(url, subject_code):
    response = requests.get(url)  # Fetch the webpage
    soup = BeautifulSoup(response.text, 'html.parser')  # Parse the HTML content
    return [
        # Find all links that open in a new tab
        link['href'] for link in soup.find_all('a', href=True, target='replace')  # replace
        if subject_code.lower() in link['href'].lower()  # Filter links containing the subject code
    ]

# Function to extract questions from a PDF file
def extract_questions_from_pdf(pdf_url):
    response = requests.get(pdf_url)  # Fetch the PDF content
    pdf_reader = PdfReader(BytesIO(response.content))  # Read the PDF using PyPDF2
    questions_by_unit = {}  # Dictionary to store questions by unit

    for page in pdf_reader.pages:  # Iterate through each page in the PDF
        text = page.extract_text()  # Extract text from the page
        units = text.split("UNIT")  # Split text into units
        for unit_text in units[1:]:  # Skip the first part (before "UNIT 1")
            unit_number = unit_text[:10].strip()  # Extract the unit number (first 10 characters)
            questions_by_unit.setdefault(unit_number, [])  # Initialize a list for this unit if not already present
            # Extract questions for part (a) and part (b)
            a_questions = extract_questions(unit_text, "a)", "b)")
            b_questions = extract_questions(unit_text, "b)", "(OR)")
            questions_by_unit[unit_number].extend(a_questions + b_questions)  # Add questions to the unit
    return questions_by_unit

# Helper function to extract questions based on delimiters
def extract_questions(text, start_delim, end_delim):
    questions = []  # List to store extracted questions
    start_pos = 0  # Starting position for search
    while True:
        pos_a = text.find(start_delim, start_pos)  # Find the starting delimiter
        pos_b = text.find(end_delim, pos_a + len(start_delim))  # Find the ending delimiter
        if pos_a == -1:  # If no more starting delimiter is found, break the loop
            break
        # Extract the question between delimiters
        question = text[pos_a:pos_b].strip() if pos_b != -1 else text[pos_a:].strip()
        questions.append(question)  # Add the question to the list
        start_pos = pos_b if pos_b != -1 else len(text)  # Update the search position
    return questions

# Main logic of the program
subjects = extract_subject_names(url)  # Extract the list of subjects from the webpage
if not subjects:  # If no subjects are found, display a message and exit
    print("No subjects found. Please check the URL or webpage structure.")
    exit()

# Display the available subjects to the user
print("Subjects available:")
for idx, subject in enumerate(subjects):  # Enumerate to show index and subject name
    print(f"{idx}: {subject}")

# Prompt user to select a subject by index
subject_code = subjects[int(input("Select a subject by index: "))]

# Scrape PDF links for the selected subject
pdf_links = scrape_pdf_links(url, subject_code)
if not pdf_links:  # If no PDFs are found, display a message and exit
    print(f"No PDFs found for subject '{subject_code}'.")
    exit()

print(f"You selected {subject_code}\n\nFound {len(pdf_links)} PDF(s).\n\n")   #pdf count 

# Prompt user to select an action
action = input("Select action:\n1. Common questions\n2. All questions\n")
if action == '1':
    subject_data = {}  # Dictionary to store all questions by unit across PDFs
    for pdf_url in pdf_links:  # Process each PDF link
        questions_by_unit = extract_questions_from_pdf(pdf_url)  # Extract questions by unit
        for unit, questions in questions_by_unit.items():
            subject_data.setdefault(unit, []).append(questions)  # Group questions by unit
    # Identify common questions for each unit
    common_questions = {}
    for unit, questions in subject_data.items():
        # Flatten the list of lists for the unit
        flattened_questions = [q for sublist in questions for q in sublist]
    
        # Use a dictionary to count occurrences
        question_count = {}
        for q in flattened_questions:
            question_count[q] = question_count.get(q, 0) + 1
    
        # Find common questions (appear more than once)
        common_questions[unit] = [q for q, count in question_count.items() if count > 1]

    # Display common questions by unit
    print("Common Questions by Unit:")
    for unit, questions in common_questions.items():
        print(f"UNIT {unit}:")
        for question in questions:
            print(question)
else:
    # Display all questions from each PDF
    for pdf_url in pdf_links:
        questions_by_unit = extract_questions_from_pdf(pdf_url)  # Extract questions by unit
        for unit, questions in questions_by_unit.items():
            print(f"UNIT {unit}:")
            for question in questions:
                print(question)
