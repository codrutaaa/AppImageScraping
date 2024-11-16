from flask import Flask, render_template, request, jsonify, send_file
import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import zipfile

app = Flask(__name__)

# Directory to save downloaded images
IMAGE_DIR = "static/downloaded_images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# Statistics Tracking
statistics = {
    "total_images": 0,
    "unique_searches": set(),
    "search_counts": {}
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/statistics")
def statistics_page():
    return render_template("statistics.html")


# In-memory tracking
statistics = {
    "total_images": 0,
    "unique_searches": set(),
    "search_counts": {},  # Tracks the count of each search term
    "scraping_history": []  # Stores scraping sessions
}

@app.route("/scrape-images", methods=["POST"])
def scrape_images():
    data = request.json
    query = data.get("query", "").lower()  # Normalize to lowercase for consistent tracking
    num_images = int(data.get("num_images", 10))

    # Track statistics
    statistics["unique_searches"].add(query)
    statistics["search_counts"][query] = statistics["search_counts"].get(query, 0) + 1
    statistics["total_images"] += num_images
    statistics["scraping_history"].append({
        "query": query,
        "num_images": num_images
    })

    # Scraping logic (unchanged)
    search_url = f"https://www.google.com/search?q={query}&tbm=isch"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    image_elements = soup.find_all("img")

    images_downloaded = 0
    image_urls = []

    for img in image_elements:
        if images_downloaded >= num_images:
            break

        img_url = img.get("src")
        if not img_url or img_url.startswith("data"):
            continue

        try:
            img_response = requests.get(img_url)
            img_obj = Image.open(BytesIO(img_response.content))

            # Save image logic
            width, height = img_obj.size
            if width > 0 and height > 0:  # Simplified dimension check
                img_filename = f"{query}_{images_downloaded}.jpg"
                img_path = os.path.join(IMAGE_DIR, img_filename)
                img_obj.save(img_path)

                image_urls.append(f"/static/downloaded_images/{img_filename}")
                images_downloaded += 1
        except Exception as e:
            print(f"Failed to download image: {e}")

    return jsonify({"status": "success", "images": image_urls})

@app.route("/download-selected", methods=["POST"])
def download_selected():
    data = request.json
    selected_images = data.get("images", [])

    if not selected_images:
        return jsonify({"status": "error", "message": "No images selected"}), 400

    zip_path = "selected_images.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for image_path in selected_images:
            image_filename = os.path.basename(image_path)
            zipf.write(os.path.join("static", "downloaded_images", image_filename), image_filename)

    return send_file(zip_path, as_attachment=True)

@app.route("/api/statistics", methods=["GET"])
def get_statistics():
    # Aggregate searches
    search_counts = statistics["search_counts"]

    # Prepare data for bar chart (sorted by search frequency)
    sorted_search_counts = sorted(search_counts.items(), key=lambda x: x[1], reverse=True)
    bar_labels = [term for term, _ in sorted_search_counts]
    bar_data = [count for _, count in sorted_search_counts]

    # Most popular search
    popular_search = bar_labels[0] if bar_labels else "N/A"

    return jsonify({
        "total_images": statistics["total_images"],
        "unique_searches": len(statistics["unique_searches"]),
        "popular_search": popular_search,
        "bar_labels": bar_labels,  # Unique terms for bar chart
        "bar_data": bar_data,      # Frequency for each term
        "pie_labels": bar_labels, # Same terms for pie chart
        "pie_data": bar_data      # Same counts for pie chart
    })

if __name__ == "__main__":
    app.run(debug=True)
