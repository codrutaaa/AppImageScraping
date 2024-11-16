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

# Track downloaded images per query
# Track downloaded images per query
downloaded_images = {}

@app.route("/scrape-images", methods=["POST"])
def scrape_images():
    try:
        data = request.json
        query = data.get("query", "").lower()
        num_images = int(data.get("num_images", 10))
        style = data.get("style", "").lower()
        use_case = data.get("use_case", "").lower()
        categories = data.get("categories", [])
        min_width = int(data.get("min_width", 0))
        min_height = int(data.get("min_height", 0))
        max_width = int(data.get("max_width", 10000))
        max_height = int(data.get("max_height", 10000))

        # Modify query with filters
        if style:
            query += f" {style}"
        if use_case:
            query += f" {use_case}"
        if categories:
            query += " " + " ".join(categories)

        print(f"Scraping for query: {query}, filters: {data}")

        # Initialize tracking for query if not exists
        if query not in downloaded_images:
            downloaded_images[query] = set()

        # Scrape images
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

            # Skip already downloaded images
            if img_url in downloaded_images[query]:
                continue

            try:
                img_response = requests.get(img_url)
                img_obj = Image.open(BytesIO(img_response.content))

                # Check resolution
                width, height = img_obj.size
                if min_width <= width <= max_width and min_height <= height <= max_height:
                    img_filename = f"{query}_{images_downloaded}.jpg"
                    img_path = os.path.join(IMAGE_DIR, img_filename)
                    img_obj.save(img_path)

                    image_urls.append(f"/static/downloaded_images/{img_filename}")
                    downloaded_images[query].add(img_url)  # Mark as downloaded
                    images_downloaded += 1
            except Exception as e:
                print(f"Error downloading image: {e}")

        return jsonify({"status": "success", "images": image_urls})
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500



@app.route("/download-selected", methods=["POST"])
def download_selected():
    try:
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

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

import csv
from flask import Response
@app.route("/download-statistics", methods=["GET"])
def download_statistics():
    # Prepare statistics data
    stats = {
        "total_images": statistics["total_images"],
        "unique_searches": len(statistics["unique_searches"]),
        "popular_search": max(statistics["search_counts"], key=statistics["search_counts"].get, default="N/A"),
        "search_counts": statistics["search_counts"]
    }

    # Create CSV content with improved formatting
    csv_filename = "enhanced_statistics.csv"
    csv_content = []

    # Section 1: Overall Statistics
    csv_content.append(["Overall Statistics"])
    csv_content.append(["Metric", "Value"])
    csv_content.append(["Total Images Scraped", stats["total_images"]])
    csv_content.append(["Unique Searches", stats["unique_searches"]])
    csv_content.append(["Most Popular Search", stats["popular_search"]])
    csv_content.append([])  # Add an empty row for spacing

    # Section 2: Detailed Search Counts
    csv_content.append(["Search Term Statistics"])
    csv_content.append(["Search Term", "Number of Searches"])
    for term, count in stats["search_counts"].items():
        csv_content.append([term, count])
    csv_content.append([])  # Add an empty row for spacing

    # Stream the CSV file as a response
    def generate():
        for row in csv_content:
            yield ",".join(map(str, row)) + "\n"

    response = Response(generate(), mimetype="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={csv_filename}"
    return response

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
