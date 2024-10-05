// Fetch blink data and draw chart
async function drawBlinkChart() {
    try {
        // Fetch blink data from backend
        const response = await fetch('/get_blink_data');
        const blinkData = await response.json();

        // Extract timestamps and blink counts from data
        const labels = blinkData.map(entry => new Date(entry.timestamp).toLocaleString());
        const blinkCounts = blinkData.map(entry => entry.blink_count);

        // Use Chart.js to draw the line chart
        const ctx = document.getElementById('blinkChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Blink Count Over Time',
                    data: blinkCounts,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderWidth: 1,
                    tension: 0.2  // Add smoothness to the line
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Blink Count'
                        },
                        beginAtZero: true
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error fetching blink data:', error);
    }
}

// Call function to draw the chart
drawBlinkChart();
