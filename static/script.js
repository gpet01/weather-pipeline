fetch("/api/weather-data")
    .then(res => res.json())
    .then(data => {
        new Chart(document.getElementById("tempChart"), {
            type: "line",
            data: {
                labels: data.labels,
                datasets: [{
                    label: "Temperature (°C)",
                    data: data.temp,
                    borderColor: "#ff6384",
                    tension: 0.3,
                }]
            }
        });

        new Chart(document.getElementById("humidityChart"), {
            type: "line",
            data: {
                labels: data.labels,
                datasets: [{
                    label: "Humidity (%)",
                    data: data.humidity,
                    borderColor: "#36a2eb",
                    tension: 0.3,
                }]
            }
        });
    });