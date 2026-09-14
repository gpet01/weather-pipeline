const COLOR_WARM = "#f2994a";
const COLOR_COOL = "#4fa8d8";
const COLOR_MUTED = "#7f92a3";
const COLOR_GRID = "#24323e";

function formatTime(bigQueryDatetimeString) {
    const isoUtc = bigQueryDatetimeString.replace(" ", "T") + "Z";
    const date = new Date(isoUtc);
    return date.toLocaleTimeString("el-GR", {
        hour: "2-digit",
        minute: "2-digit",
        timeZone: "Europe/Athens",
    });
}

function formatDateTime(bigQueryDatetimeString) {
    const isoUtc = bigQueryDatetimeString.replace(" ", "T") + "Z";
    const date = new Date(isoUtc);
    return date.toLocaleString("el-GR", {
        day: "2-digit",
        month: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        timeZone: "Europe/Athens",
    });
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
    .then((res) => {
        if (!res.ok) throw new Error(`Server responded with ${res.status}`);
        return res.json();
    })
    .then((data) => {
        const labels = data.labels.map(formatTime);

        if (data.current) {
            document.getElementById("currentTemp").textContent = Math.round(data.current.temp);
            document.getElementById("currentDescription").textContent = data.current.description;
            document.getElementById("currentHumidity").textContent = `${data.current.humidity}%`;
            document.getElementById("currentWind").textContent = `${data.current.wind_speed} m/s`;
            document.getElementById("updatedLabel").textContent = `Πρόβλεψη για ${formatDateTime(data.current.forecast_time)}`;
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
    })
    .catch((error) =>{
        document.getElementById("currentDescription").textContent = 
            "Δεν ήταν δυνατή η φόρτωση δεδομένων καιρού.";
        console.error("Weather data fetch failed:", error);
    });
