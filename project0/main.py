import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend for matplotlib
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score  # For dynamic cluster determination
from flask import Flask, request, render_template, redirect, url_for
from norman import fetchincidents, extractincidents  # Reuse Project 0 module
import umap  # For dimensionality reduction

app = Flask(__name__)
UPLOAD_FOLDER = './uploads'
STATIC_FOLDER = './project0/static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        urls = request.form.get('urls', '').splitlines()  # Accept multiple URLs
        pdf_paths = [fetchincidents(url) for url in urls if url.strip()]

        # Process uploaded files
        files = request.files.getlist('files')
        for file in files:
            if file.filename.endswith('.pdf'):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
                pdf_paths.append(filepath)

        if pdf_paths:
            return redirect(url_for("process_files", filepaths=",".join(pdf_paths)))

    return render_template("upload.html")


@app.route("/process", methods=["GET"])
def process_files():
    filepaths = request.args.get("filepaths")

    if not filepaths:
        return "No files provided.", 400

    filepaths = filepaths.split(",")
    all_incidents = []

    # Process each file
    for filepath in filepaths:
        incidents = extractincidents(filepath)
        if incidents:
            all_incidents.extend(incidents)

    if not all_incidents:
        return "No incidents found.", 400

    data = pd.DataFrame(all_incidents)

    # Ensure the static directory exists
    if not os.path.exists(STATIC_FOLDER):
        os.makedirs(STATIC_FOLDER)

    # Visualization 1: Bar Graph
    bar_output_path = os.path.join(STATIC_FOLDER, 'incident_bar_graph.png')
    try:
        nature_counts = data['nature'].value_counts()
        plt.figure(figsize=(10, 6))
        nature_counts.plot(kind='bar', color='skyblue', edgecolor='black')
        plt.title("Incidents by Nature")
        plt.xlabel("Nature of Incident")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig(bar_output_path)
        plt.close()
    except Exception as e:
        print(f"Error saving bar graph: {e}")

    # Visualization 2: Scatter Plot for Nature-Based Clustering
    scatter_output_path = os.path.join(STATIC_FOLDER, 'incident_scatter_plot.png')
    cluster_summaries = []

    try:
        # Use TF-IDF to vectorize incident types dynamically
        vectorizer = TfidfVectorizer(stop_words='english')
        nature_vectors = vectorizer.fit_transform(data['nature'])

        # Determine the number of clusters dynamically based on silhouette score
        num_categories = determine_optimal_clusters(nature_vectors)
        print(f"Dynamic clusters for incident categories: {num_categories}")

        # Perform KMeans clustering on TF-IDF vectors
        kmeans_nature = KMeans(n_clusters=num_categories, random_state=0)
        data['category'] = kmeans_nature.fit_predict(nature_vectors)

        # Calculate counts and unique incident types for each cluster
        cluster_counts = data['category'].value_counts()
        cluster_incidents = data.groupby('category')['nature'].apply(lambda x: x.value_counts().to_dict())

        # Create summaries for each cluster
        cluster_summaries = []
        for cluster in range(num_categories):
            incidents = cluster_incidents.get(cluster, {})
            cleaned_incidents = {incident: count for incident, count in incidents.items() if not pd.isna(count) and count > 0}

            cluster_summary = {
                'cluster': cluster,
                'count': cluster_counts.get(cluster, 0),
                'types': cleaned_incidents
            }
            cluster_summaries.append(cluster_summary)

        # Reduce TF-IDF vectors to 2D using UMAP for scatter plot
        reducer = umap.UMAP(random_state=0)
        embeddings_2d = reducer.fit_transform(nature_vectors.toarray())

        # Plot Scatter Plot
        plt.figure(figsize=(12, 8))
        for cluster in range(num_categories):
            cluster_points = embeddings_2d[data['category'] == cluster]
            plt.scatter(cluster_points[:, 0], cluster_points[:, 1], label=f"Cluster {cluster} ({cluster_counts[cluster]} incidents)")

            # Annotate clusters with counts
            cluster_center = cluster_points.mean(axis=0)
            plt.annotate(f"Cluster {cluster}\nCount: {cluster_counts[cluster]}",
                        xy=(cluster_center[0], cluster_center[1]),
                        xytext=(cluster_center[0] + 0.5, cluster_center[1] + 0.5),
                        arrowprops=dict(facecolor='black', shrink=0.05),
                        fontsize=10,
                        bbox=dict(boxstyle="round,pad=0.3", edgecolor='black', facecolor='white'))

        plt.title("Scatter Plot of Incident Types (Based on Nature)")
        plt.xlabel("UMAP Dimension 1")
        plt.ylabel("UMAP Dimension 2")
        plt.legend()
        plt.tight_layout()
        plt.savefig(scatter_output_path)
        plt.close()
    except Exception as e:
        print(f"Error saving scatter plot: {e}")

    # Visualization 3: Heatmap of Incident Frequency by Hour
    heatmap_output_path = os.path.join(STATIC_FOLDER, 'incident_heatmap.png')
    try:
        # Group incidents by nature and hour of the day
        data['hour'] = pd.to_datetime(data['incident_time']).dt.hour
        heatmap_data = data.groupby(['nature', 'hour']).size().unstack(fill_value=0)

        # Plot the heatmap
        plt.figure(figsize=(12, 8))
        plt.imshow(heatmap_data, aspect='auto', cmap='coolwarm', interpolation='nearest')
        plt.colorbar(label='Frequency')
        plt.xticks(range(24), [f"{hour}:00" for hour in range(24)], rotation=45)
        plt.yticks(range(len(heatmap_data.index)), heatmap_data.index)
        plt.title("Heatmap of Incident Frequency by Hour")
        plt.xlabel("Hour of the Day")
        plt.ylabel("Incident Type")
        plt.tight_layout()
        plt.savefig(heatmap_output_path)
    except Exception as e:
        print(f"Error saving heatmap: {e}")
    finally:
        plt.close()

    return render_template(
        "visualize.html",
        total_incidents=len(data),
        cluster_summaries=cluster_summaries,
        scatter_image=url_for('static', filename='incident_scatter_plot.png'),
        bar_image=url_for('static', filename='incident_bar_graph.png'),
        heatmap_image=url_for('static', filename='incident_heatmap.png')
    )


def determine_optimal_clusters(data, max_clusters=10):
    """Determine the optimal number of clusters using silhouette score."""
    best_score = -1
    best_k = 2

    for k in range(2, max_clusters + 1):
        kmeans = KMeans(n_clusters=k, random_state=0)
        labels = kmeans.fit_predict(data)
        score = silhouette_score(data, labels)

        if score > best_score:
            best_score = score
            best_k = k

    return best_k


if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
