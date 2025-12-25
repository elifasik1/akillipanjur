const API_URL = "http://127.0.0.1:5000";
let sensorChart;

function initChart() {
  const ctx = document.getElementById('sensorChart').getContext('2d');

  sensorChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        { label: 'Işık', data: [], borderColor: '#4a90e2', yAxisID: 'L', tension: 0.3 },
        { label: 'Sıcaklık', data: [], borderColor: '#f48c8c', yAxisID: 'T', tension: 0.3 }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        L: {   // ✅ dataset yAxisID: 'L' ile aynı
          type: 'linear',
          position: 'left',
          title: { display: true, text: 'Işık' },
          min: 0,
          max: 1000
        },
        T: {   // ✅ dataset yAxisID: 'T' ile aynı
          type: 'linear',
          position: 'right',
          title: { display: true, text: 'Sıcaklık (°C)' },
          min: 0,
          max: 50,
          grid: { drawOnChartArea: false }
        }
      },
      plugins: {
        legend: { position: 'top' }
      }
    }
  });
}


function showToast(msg, type='info') {
    const container = document.getElementById("toast-container");
    const t = document.createElement("div");
    t.className = `toast ${type}`;
    t.innerText = msg;
    container.appendChild(t);
    setTimeout(() => t.remove(), 3000);
}

function refreshData() {
    fetch(`${API_URL}/sensor-data`).then(r => r.json()).then(data => {
        document.getElementById("mode").innerText = data.state.mode;
        document.getElementById("shutter").innerText = data.state.shutter;
        
        // Eğer grafik boşsa ve geçmiş veri varsa, önce geçmişi yükle
        if (sensorChart.data.labels.length === 0 && data.history && data.history.length > 0) {
            data.history.forEach(item => {
                const time = item.ts.split('T')[1].substring(0, 8);
                sensorChart.data.labels.push(time);
                sensorChart.data.datasets[0].data.push(item.isik);
                sensorChart.data.datasets[1].data.push(item.sicaklik);
            });
            sensorChart.update();
        }

        if (data.latest) {
            document.getElementById("isik").innerText = data.latest.isik;
            document.getElementById("sicaklik").innerText = data.latest.sicaklik;
            document.getElementById("nem").innerText = data.latest.nem;
            
            // Sadece yeni bir veri geldiyse grafiğe ekle (zaman kontrolü)
            const lastLabel = sensorChart.data.labels[sensorChart.data.labels.length - 1];
            const currentTs = data.latest.ts.split('T')[1].substring(0, 8);
            
            if (lastLabel !== currentTs) {
                updateChart(data.latest);
            }
        }
    });
}

function updateChart(latest) {
    if (!sensorChart || !latest) return;

    // Verilerin sayısal olduğundan emin oluyoruz (Kritik adım)
    const isikDeğeri = Number(latest.isik);
    const sicaklikDeğeri = Number(latest.sicaklik);

    if (sensorChart.data.labels.length > 15) { 
        sensorChart.data.labels.shift(); 
        sensorChart.data.datasets[0].data.shift(); 
        sensorChart.data.datasets[1].data.shift(); 
    }

    const time = new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    sensorChart.data.labels.push(time);
    
    // Işık ve Sıcaklığı ayrı ayrı ekliyoruz
    sensorChart.data.datasets[0].data.push(isikDeğeri);
    sensorChart.data.datasets[1].data.push(sicaklikDeğeri);
    
    sensorChart.update();
}
function setMode(mode) {
    fetch(`${API_URL}/control`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ mode }) })
    .then(() => { showToast(`Mod değiştirildi: ${mode}`); refreshData(); });
}

function setShutter(shutter) {
    if (document.getElementById("mode").innerText === "AUTO") {
        showToast("Otomatik modda manuel kontrol yapılamaz!", "danger"); return;
    }
    fetch(`${API_URL}/control`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ shutter }) })
    .then(() => { showToast(`Panjur: ${shutter}`); refreshData(); });
}

document.addEventListener('DOMContentLoaded', () => {
    initChart();
    refreshData();
    setInterval(refreshData, 2000); // 2 saniyede bir güncelleme [cite: 36, 78]
});