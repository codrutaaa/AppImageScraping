document.addEventListener("DOMContentLoaded", async () => {
    try {
        const response = await fetch("/api/statistics");
        const stats = await response.json();

        // Update Statistics Cards
        document.getElementById("total-images").textContent = stats.total_images;
        document.getElementById("unique-searches").textContent = stats.unique_searches;
        document.getElementById("popular-search").textContent = stats.popular_search;

        // Bar Chart for Search Term Frequency
        const barCtx = document.getElementById("barChart").getContext("2d");
        new Chart(barCtx, {
            type: "bar",
            data: {
                labels: stats.bar_labels, // Unique terms
                datasets: [{
                    label: "Number of Searches",
                    data: stats.bar_data,   // Frequency of each term
                    backgroundColor: "rgba(52, 152, 219, 0.7)",
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        title: { display: true, text: "Search Terms" }
                    },
                    y: {
                        title: { display: true, text: "Search Frequency" },
                        beginAtZero: true
                    }
                }
            }
        });

        // Pie Chart for Search Term Distribution
        const pieCtx = document.getElementById("pieChart").getContext("2d");
        new Chart(pieCtx, {
            type: "pie",
            data: {
                labels: stats.pie_labels, // Unique terms
                datasets: [{
                    data: stats.pie_data,   // Frequency of each term
                    backgroundColor: ["#3498db", "#2ecc71", "#e74c3c", "#f1c40f", "#9b59b6"]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: "bottom" }
                }
            }
        });
    } catch (error) {
        console.error("Error fetching statistics:", error);
    }
});
