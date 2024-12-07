import argparse
import sqlite3
import urllib.request
import re
import os
from pypdf import PdfReader

def fetchincidents(url):
    # Setting headers for the download request
    headers = {
        'User-Agent': ("Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 "
                       "(KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17")
    }
    
    # File path for the downloaded PDF
    pdf_path = "/tmp/daily_incident_summary.pdf"
    
    try:
        # Requesting and saving the PDF
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request) as response, open(pdf_path, 'wb') as file:
            file.write(response.read())
            
        return pdf_path
    except Exception as e:
        print(f"Error downloading PDF: {e}")
        return None

def extractincidents(pdf_file_path):
    #print("Extracting incidents from the PDF...")
    reader = PdfReader(pdf_file_path)
    incidents = []

    # Regex patterns to capture each field
    date_time_pattern = r'(\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2})'
    incident_number_pattern = r'(\d{4}-\d{5,8})'
    location_pattern = r"([A-Z0-9][\w\s./,;'()-]*?(?:RAMP\s\d+\sRAMP)?(?=\s(?:911|MVA|COP|EMS|[A-Z][a-z/])))"
    nature_pattern = r'(911(?:\s+[A-Z][a-zA-Z\s]+(?:/[A-Za-z\s]+)*)?|[A-Z][a-zA-Z\s]+(?:/[A-Za-z\s]+)*)'
    ori_pattern = r'(OK\d+|EMSSTAT|\d{5})'

    # Combining the full row pattern
    row_pattern = re.compile(
        rf"{date_time_pattern}\s+{incident_number_pattern}\s+{location_pattern}\s+{nature_pattern}\s+{ori_pattern}"
    )

    try:
        for page in reader.pages:
            text = page.extract_text(extraction_mode="layout", layout_mode_space_vertically=False)
            text = re.sub(r'\s+', ' ', text)  # normalize whitespace
            
            # find all matches using improved row pattern
            for match in row_pattern.findall(text):
                incident = {
                    "incident_time": match[0].strip(),
                    "incident_number": match[1].strip(),
                    "location": match[2].strip(),
                    "nature": match[3].strip(),
                    "incident_ori": match[4].strip()
                }

                # Post-processing check for "Fraud" and "Robinson"
                line = ' '.join(match)
                if "Vandalism" in line:
                    incident["nature"] = "Vandalism"  # Force the nature to be 'Larceny'
                
                incidents.append(incident)
        
        return incidents
    except Exception as e:
        print(f"Error extracting incidents: {e}")
        return []




def createdb():
    resources_dir = 'resources'
    db_path = os.path.join(resources_dir, 'normanpd.db')
    
    # create 'resources' dir if missed
    if not os.path.exists(resources_dir):
        os.makedirs(resources_dir)
    
    # delete existing db
    if os.path.exists(db_path):
        os.remove(db_path)

    # Create db
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # create 'incidents' table without duplicates
    c.execute('''
        CREATE TABLE incidents (
            incident_time TEXT,
            incident_number TEXT,
            incident_location TEXT,
            nature TEXT,
            incident_ori TEXT
        )
    ''')

    conn.commit()
    #print(f"Database created at {db_path}")
    return conn

def populatedb(db, data):
    if not data:
        return
    
    c = db.cursor()
    
    # Debug print to verify data before insertion
    c.executemany('''
        INSERT INTO incidents (incident_time, incident_number, incident_location, nature, incident_ori)
        VALUES (:incident_time, :incident_number, :location, :nature, :incident_ori)
    ''', data)
    
    db.commit()
 
def status(db):
    c = db.cursor()
    # Fetching and counting incidents by 'nature', including duplicates
    c.execute('''
        SELECT nature, COUNT(*) as count
        FROM incidents
        GROUP BY nature
        ORDER BY nature ASC
    ''')
    
    results = c.fetchall()
    if not results:
        print("No data available in the database.")
    else:
        for row in results:
            print(f"{row[0]}|{row[1]}")


def head(db, n=400):
    c = db.cursor()
    
    # Fetch the top `n` rows from the incidents table
    c.execute('''
        SELECT incident_time, incident_number, incident_location, nature, incident_ori
        FROM incidents
        LIMIT ?
    ''', (n,))
    
    rows = c.fetchall()
    
    if not rows:
        print(f"No data available in the database to display the top {n} rows.")
    else:
        print(f"Top {n} rows from the incidents database:")
        print(f"{'Date / Time':<20} {'Incident Number':<20} {'Location':<30} {'Nature':<30} {'Incident ORI':<10}")
        print("-" * 110)
        for row in rows:
            print(f"{row[0]:<20} {row[1]:<20} {row[2]:<30} {row[3]:<30} {row[4]:<10}")


def main(url):
    # Fetch data
    pdf_path = fetchincidents(url)

    if not pdf_path:
        return
    
    # Extract incidents
    incidents = extractincidents(pdf_path)
    if not incidents:
        return
    
    # Create DB
    db = createdb()
    
    # Populate DB
    populatedb(db, incidents)
    #head(db)
    # Show status
    status(db)
    db.close()

if __name__ == '__main__':
    # Argument parsing for command line usage
    parser = argparse.ArgumentParser()
    parser.add_argument("--incidents", type=str, required=True, 
                         help="Incident summary URL.")
     
    args = parser.parse_args()
    if args.incidents:
        main(args.incidents)
