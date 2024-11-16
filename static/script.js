document.getElementById("scrape-form").addEventListener("submit", async function (event) {
    event.preventDefault();

    const query = document.getElementById("query").value.trim();
    const num_images = parseInt(document.getElementById("num_images").value);
    const style = document.getElementById("style").value;
    const use_case = document.getElementById("use_case").value;

    const categories = Array.from(
        document.querySelectorAll("input[name='categories']:checked")
    ).map(checkbox => checkbox.value);

    const min_width = parseInt(document.getElementById("min_width").value) || 0;
    const min_height = parseInt(document.getElementById("min_height").value) || 0;
    const max_width = parseInt(document.getElementById("max_width").value) || 5000;
    const max_height = parseInt(document.getElementById("max_height").value) || 5000;

    const data = {
        query,
        num_images,
        style,
        use_case,
        categories,
        min_width,
        min_height,
        max_width,
        max_height
    };

    try {
        const response = await fetch("/scrape-images", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });

        if (response.ok) {
            const result = await response.json();
            const imageList = document.getElementById("image-list");
            imageList.innerHTML = "";

            // Add checkboxes and images
            result.images.forEach(image => {
                const container = document.createElement("div");
                container.classList.add("image-container");

                const imgElement = document.createElement("img");
                imgElement.src = image;
                imgElement.alt = "Scraped Image";
                imgElement.classList.add("scraped-image");

                const checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.value = image;
                checkbox.classList.add("image-checkbox");

                container.appendChild(imgElement);
                container.appendChild(checkbox);
                imageList.appendChild(container);
            });

            document.getElementById("download-selected").style.display = "block";
        } else {
            console.error("Error:", response.statusText);
        }
    } catch (error) {
        console.error("Error:", error);
    }
});

document.getElementById("download-selected").addEventListener("click", async function () {
    const selectedImages = Array.from(
        document.querySelectorAll(".image-checkbox:checked")
    ).map(checkbox => checkbox.value);

    if (selectedImages.length === 0) {
        alert("No images selected for download!");
        return;
    }

    try {
        const response = await fetch("/download-selected", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ images: selectedImages }),
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);

            const a = document.createElement("a");
            a.href = url;
            a.download = "selected_images.zip";
            a.click();

            window.URL.revokeObjectURL(url);
        } else {
            console.error("Error:", response.statusText);
        }
    } catch (error) {
        console.error("Error:", error);
    }
});
