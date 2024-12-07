import os
import pytest
from project0.norman import fetchincidents

# Test URL and expected PDF path
url = "https://www.normanok.gov/sites/default/files/documents/2024-08/2024-08-01_daily_incident_summary.pdf"
pdf_path = "/tmp/daily_incident_summary.pdf"

def test_f():
    # Fetch the PDF
    d_path = fetchincidents(url)
    
    # Validate the file was downloaded correctly
    assert d_path == pdf_path
    assert os.path.exists(d_path)
    
    # Clean up after test
    if os.path.exists(d_path):
        os.remove(d_path)
