const COLOR_WARM = "#f2994a";
const COLOR_COOL = "#4fa8d8";
const COLOR_MUTED = "#7f92a3";
const COLOR_GRID = "#24323e";

function formatTime(isoLikeString) {
    // BigQuery returns "YYYY-MM-DD HH:MM:SS" — show just the hour for chart labels.
    const parts = isoLikeString.split(" ");
    return parts.length > 1 ? parts[1].slice(0, 5) : isoLikeString;
}

function baseChartOptions(unitSuffix) {
    return {
        responsive: true,
        plugins: {
            legend: { display: false },
        },
        scales: {
            x: {
                ticks: { color: COLOR_MUTED },
                grid: { color: COLOR_GRID },
            },
            y: {
                ticks: {
                    color: COLOR_MUTED,
                    callback: (value) => `${value}${unitSuffix}`,
                },
                grid: { color: COLOR_GRID },
            },
        },
    };
}

fetch("/api/weather-data")
    .then((res) => res.json())
    .then((data) => {
        const labels = data.labels.map(formatTime);

        if (data.current) {
            document.getElementById("currentTemp").textContent = Math.round(data.current.temp);
            document.getElementById("currentDescription").textContent = data.current.description;
            document.getElementById("currentHumidity").textContent = `${data.current.humidity}%`;
            document.getElementById("currentWind").textContent = `${data.current.wind_speed} m/s`;
            document.getElementById("updatedLabel").textContent = `Πρόβλεψη για ${data.current.forecast_time}`;
        }

        new Chart(document.getElementById("tempChart"), {
            type: "line",
            data: {
                labels,
                datasets: [{
                    data: data.temp,
                    borderColor: COLOR_WARM,
                    backgroundColor: COLOR_WARM,
                    tension: 0.35,
                    pointRadius: 3,
                }],
            },
            options: baseChartOptions("°"),
        });

        new Chart(document.getElementById("humidityChart"), {
            type: "line",
            data: {
                labels,
                datasets: [{
                    data: data.humidity,
                    borderColor: COLOR_COOL,
                    backgroundColor: COLOR_COOL,
                    tension: 0.35,
                    pointRadius: 3,
                }],
            },
            options: baseChartOptions("%"),
        });
    });