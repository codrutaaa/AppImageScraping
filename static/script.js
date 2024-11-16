document.getElementById("scrape-form").addEventListener("submit", async function (event) {
    event.preventDefault();

    const query = document.getElementById("query").value;
    const num_images = document.getElementById("num_images").value;
    const min_width = document.getElementById("min_width").value;
    const min_height = document.getElementById("min_height").value;
    const max_width = document.getElementById("max_width").value;
    const max_height = document.getElementById("max_height").value;

    const data = {
        query,
        num_images,
        min_width,
        min_height,
        max_width,
        max_height
    };

    try {
        const response = await fetch("/scrape-images", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        // Clear previous images
        const imageList = document.getElementById("image-list");
        imageList.innerHTML = "";

        if (result.status === "success") {
            result.images.forEach((imagePath, index) => {
                const container = document.createElement("div");
                container.classList.add("image-container");

                const img = document.createElement("img");
                img.src = imagePath;
                img.alt = "Scraped Image";

                const checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.value = imagePath;
                checkbox.id = `image-${index}`;
                checkbox.classList.add("image-checkbox");

                const label = document.createElement("label");
                label.htmlFor = `image-${index}`;
                label.textContent = "Select";

                container.appendChild(img);
                container.appendChild(checkbox);
                container.appendChild(label);
                imageList.appendChild(container);
            });

            document.getElementById("download-selected").style.display = "block";
        } else {
            alert("Error: " + result.message);
        }
    } catch (error) {
        console.error("Error:", error);
    }
});

document.getElementById("download-selected").addEventListener("click", async function () {
    const selectedImages = Array.from(document.querySelectorAll(".image-checkbox:checked")).map(
        (checkbox) => checkbox.value
    );

    if (selectedImages.length === 0) {
        alert("No images selected!");
        return;
    }

    try {
        const response = await fetch("/download-selected", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ images: selectedImages })
        });

        if (response.status === 200) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "selected_images.zip";
            document.body.appendChild(a);
            a.click();
            a.remove();
        } else {
            alert("Failed to download selected images.");
        }
    } catch (error) {
        console.error("Error:", error);
    }
});
