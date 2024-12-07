## Project: cis6930fa24-project3

### Name: Vijay Kumar Reddy Gade

---

### **What is this Project About?**

This project is all about processing incident report PDFs or URLs and making sense of the data through meaningful visualizations. It allows users to upload or provide URLs for incident reports, processes the data, and generates insightful visuals like bar charts, scatter plots, and heatmaps. The goal is to help analyze incident trends dynamically and visually.

---

### **How to Install**

1. **Install Pipenv**  
   First, you'll need Pipenv to manage dependencies. Install it using this command:  
   ```bash
   pip install pipenv
   ```

2. **Install the Required Dependencies**  
   Navigate to the project directory and run:  
   ```bash
   pipenv install
   ```

3. **Run the Application**  
   Start the application with the following command:  
   ```bash
   pipenv run python project0/main.py
   ```

---

### **How Does It Work?**

Once the application is running, open your browser and go to `http://127.0.0.1:5000`. Here’s what you can do:

- **Upload Incident Reports**  
  - Enter one or more URLs for incident reports.
  - Or, upload PDFs containing incident data.

- **Visualizations**  
  After processing, the application generates:
  1. **Bar Chart**: See how many incidents occurred for each type.
  2. **Scatter Plot**: View clusters of incident types in a reduced dimensional space using UMAP.
  3. **Heatmap**: Understand how incidents are distributed across different hours of the day.

---

### **How to Use It**

#### 1. Upload Your Data
Provide URLs or PDFs through the upload page. The app processes the reports and redirects you to the visualization page.

#### 2. Check Out the Visualizations
- **Bar Chart**: Understand the frequency of incidents by type.
- **Scatter Plot**: See dynamic clusters of similar incidents grouped together.
- **Heatmap**: Analyze incident trends by time of day and type.

#### 3. Interactive Features
- Navigate to view individual plots like the bar chart, scatter plot, or heatmap.
- Get a summary of clusters and incident types.

---

### **What Does Each Function Do?**

- **`upload_file`**: Handles the upload of URLs or PDFs and sends the data for processing.
- **`process_files`**: Processes the uploaded reports, generates visualizations, and summarizes incident clusters.
- **`fetchincidents`**: Downloads incident reports from provided URLs.
- **`extractincidents`**: Extracts meaningful data from uploaded incident PDFs.
- **`suggest_optimal_clusters`**: Dynamically calculates the best number of clusters using silhouette scores.

---


[![Watch the video](https://img.youtu.be/vi/wppA5VPP4x0/0.jpg)](https://youtu.be/wppA5VPP4x0)

---
### **Are There Any Bugs?**

Yes, there are a few known issues:
1. **Missed Incidents**: If multiple URLs or PDFs are processed simultaneously, the system might miss one or two incidents.
2. **Heatmap Scaling**: When incidents are sparse, the heatmap might look a little off.

---

### **Some Assumptions**

1. URLs provided for incident reports are valid and accessible.
2. PDFs follow a standard format that allows for consistent data extraction.

---

### **Challenges Faced**

1. Figuring out dynamic clustering with silhouette scores was tricky. It took some time to get it right, especially with larger datasets.
2. Making sure data was extracted accurately from different PDFs required a lot of testing.
3. Scaling visualizations for large data volumes while keeping them clear and readable was a bit of a challenge.

---

### **Future Improvements**

1. **Speeding Up Processing**  
   Parallelize the processing of multiple PDFs and URLs to make it faster.

2. **Better Visualizations**  
   Introduce more interactive charts using tools like Plotly or Dash.

3. **Enhanced Error Handling**  
   Add better messages for unsupported file formats or inaccessible URLs.

---
