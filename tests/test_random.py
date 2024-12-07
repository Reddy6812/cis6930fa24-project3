import os
import pytest
import sqlite3
from project0.norman import extractincidents, createdb, populatedb, status, fetchincidents

# Test PDF URL and database path
pdf_url = "https://www.normanok.gov/sites/default/files/documents/2024-08/2024-08-01_daily_incident_summary.pdf"
db_path = "resources/normanpd.db"

# Expected test data for validation
expected_data = [
    {
        "incident_time": "8/1/2024 0:04",
        "incident_number": "2024-00055419",
        "location": "1345 W LINDSEY ST",
        "nature": "Traffic Stop",
        "incident_ori": "OK0140200"
    },
    {
        "incident_time": "8/1/2024 11:16",
        "incident_number": "2024-00015398",
        "location": "900 N PORTER AVE",
        "nature": "Abdominal Pains/Problems",
        "incident_ori": "EMSSTAT"
    }
]

@pytest.fixture(scope="module")
def s_pdf():
    # Download the PDF before running tests
    pdf = fetchincidents(pdf_url)
    return pdf

def test_e(s_pdf):
    # Extract incidents from the PDF
    incs = extractincidents(s_pdf)

    # Filter incidents that match expected data
    f_incs = [i for i in incs if i['incident_number'] in [e['incident_number'] for e in expected_data]]
    
    # Validate the number of incidents and their data
    assert len(f_incs) == len(expected_data)
    
    # Compare fields of each incident
    for i in range(len(expected_data)):
        assert f_incs[i]['incident_time'] == expected_data[i]['incident_time']
        assert f_incs[i]['incident_number'] == expected_data[i]['incident_number']
        assert f_incs[i]['location'] == expected_data[i]['location']
        assert f_incs[i]['nature'] == expected_data[i]['nature']
        assert f_incs[i]['incident_ori'] == expected_data[i]['incident_ori']

def test_db():
    # Create a fresh database and clear existing records
    db = createdb()
    c = db.cursor()
    c.execute('DELETE FROM incidents')
    db.commit()

    # Populate the database with expected test data
    populatedb(db, expected_data)
    
    # Validate data was inserted correctly
    c.execute('SELECT * FROM incidents')
    rows = c.fetchall()
    assert len(rows) == len(expected_data)

    # Compare each row's data with expected values
    for i, r in enumerate(rows):
        assert r[0] == expected_data[i]['incident_time']
        assert r[1] == expected_data[i]['incident_number']
        assert r[2] == expected_data[i]['location']
        assert r[3] == expected_data[i]['nature']
        assert r[4] == expected_data[i]['incident_ori']
    
    # Clean up the test database
    db.close()
    if os.path.exists(db_path):
        os.remove(db_path)

def test_status(capsys):
    # Recreate the test database and insert data
    db = createdb()
    c = db.cursor()
    c.execute('DELETE FROM incidents')
    db.commit()
    populatedb(db, expected_data)
    
    # Capture the status function output
    status(db)
    captured = capsys.readouterr().out.splitlines()
    exp_out = ["Abdominal Pains/Problems|1", "Traffic Stop|1"]
    
    # Filter relevant lines and compare to expected output
    rel_lines = [l.strip() for l in captured if '|' in l]
    assert rel_lines == exp_out
    
    # Clean up after the test
    db.close()
    if os.path.exists(db_path):
        os.remove(db_path)
