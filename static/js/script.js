
let map;
let mapMarkers = [];
let riskChart;
let budgetChart;
let currentData = null;


document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    loadAreas();
    setupEventListeners();
});


function initializeMap() {
    map = L.map('map').setView([40.7128, -74.0060], 10); // Default to NYC
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
}


function loadAreas() {
    fetch('/api/areas')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('areaSelect');
            data.areas.forEach(area => {
                const option = document.createElement('option');
                option.value = area;
                option.textContent = area;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading areas:', error);
        });
}


function setupEventListeners() {
    
    document.querySelectorAll('input[name="dataSource"]').forEach(radio => {
        radio.addEventListener('change', function() {
            const uploadSection = document.getElementById('uploadSection');
            uploadSection.style.display = this.id === 'uploadData' ? 'block' : 'none';
        });
    });

    
    document.getElementById('analyzeBtn').addEventListener('click', runAnalysis);

   
    document.getElementById('generateSampleBtn').addEventListener('click', generateSampleData);

   
    document.getElementById('csvFile').addEventListener('change', handleFileUpload);
}


function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    showProgress(true);

    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`File uploaded successfully! Loaded ${data.count} roads.`);
            document.getElementById('defaultData').checked = false;
            document.getElementById('uploadData').checked = true;
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        alert('Upload failed: ' + error.message);
    })
    .finally(() => {
        showProgress(false);
    });
}


function runAnalysis() {
    const area = document.getElementById('areaSelect').value;
    const zone = document.getElementById('zoneSelect').value;
    const budget = parseFloat(document.getElementById('budgetInput').value);
    const useDefault = document.getElementById('defaultData').checked;

    if (isNaN(budget) || budget <= 0) {
        alert('Please enter a valid budget amount');
        return;
    }

    showProgress(true);

    fetch('/api/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            area: area,
            zone: zone,
            budget: budget,
            use_default: useDefault
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentData = data.analysis;
            updateDashboard(data.analysis);
        } else {
            alert('Analysis failed: ' + data.error);
        }
    })
    .catch(error => {
        alert('Analysis error: ' + error.message);
    })
    .finally(() => {
        showProgress(false);
    });
}


function generateSampleData() {
    showProgress(true);
    
    fetch('/api/generate-sample', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('New sample data generated successfully!');
            loadAreas();
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        alert('Error: ' + error.message);
    })
    .finally(() => {
        showProgress(false);
    });
}


function updateDashboard(analysis) {
    // Update summary cards
    document.getElementById('budgetUsed').textContent = 
        formatCurrency(analysis.budget_used);
    document.getElementById('utilizationRate').textContent = 
        analysis.budget_utilization.toFixed(1) + '% utilized';
    document.getElementById('roadsSelected').textContent = 
        analysis.roads_selected;
    document.getElementById('totalRoads').textContent = 
        'of ' + analysis.roads_total + ' total';
    document.getElementById('avgRiskScore').textContent = 
        analysis.statistics.avg_risk_score.toFixed(1);
    document.getElementById('highRiskCount').textContent = 
        analysis.risk_distribution.High;

    
    updateCharts(analysis);

    
    updateMap(analysis.selected_roads);

    
    updateRoadTable(analysis.selected_roads);
}


function updateCharts(analysis) {
    
    const riskCtx = document.getElementById('riskChart').getContext('2d');
    
    if (riskChart) {
        riskChart.destroy();
    }
    
    riskChart = new Chart(riskCtx, {
        type: 'doughnut',
        data: {
            labels: ['High Risk', 'Medium Risk', 'Low Risk'],
            datasets: [{
                data: [
                    analysis.risk_distribution.High,
                    analysis.risk_distribution.Medium,
                    analysis.risk_distribution.Low
                ],
                backgroundColor: [
                    '#dc3545', // Red
                    '#ffc107', // Yellow
                    '#28a745'  // Green
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });

   
    const budgetCtx = document.getElementById('budgetChart').getContext('2d');
    const totalBudget = analysis.budget_used + analysis.budget_remaining;
    
    if (budgetChart) {
        budgetChart.destroy();
    }
    
    budgetChart = new Chart(budgetCtx, {
        type: 'bar',
        data: {
            labels: ['Budget Used', 'Budget Remaining'],
            datasets: [{
                label: 'Amount ($)',
                data: [analysis.budget_used, analysis.budget_remaining],
                backgroundColor: [
                    'rgba(40, 167, 69, 0.7)',
                    'rgba(108, 117, 125, 0.7)'
                ],
                borderColor: [
                    'rgb(40, 167, 69)',
                    'rgb(108, 117, 125)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + (value / 1000).toFixed(0) + 'k';
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return '$' + context.raw.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}


function updateMap(roads) {
    // Clear existing markers
    mapMarkers.forEach(marker => map.removeLayer(marker));
    mapMarkers = [];

    if (roads.length === 0) return;

    
    roads.forEach((road, index) => {
        let markerColor;
        if (road.risk_category === 'High') markerColor = 'red';
        else if (road.risk_category === 'Medium') markerColor = 'orange';
        else markerColor = 'green';

        const marker = L.marker([road.latitude, road.longitude], {
            icon: L.divIcon({
                html: `<div style="
                    background-color: ${markerColor};
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    border: 2px solid white;
                    box-shadow: 0 0 5px rgba(0,0,0,0.5);
                "></div>`,
                className: 'road-marker',
                iconSize: [12, 12]
            })
        });

        marker.bindPopup(`
            <strong>${road.road_name}</strong><br>
            Risk Score: ${road.risk_score} (${road.risk_category})<br>
            Accidents: ${road.accidents}<br>
            Traffic: ${road.traffic.toLocaleString()}<br>
            Repair Cost: $${road.repair_cost.toLocaleString()}<br>
            Priority: ${index + 1}
        `);

        marker.addTo(map);
        mapMarkers.push(marker);
    });

    
    if (mapMarkers.length > 0) {
        const group = new L.featureGroup(mapMarkers);
        map.fitBounds(group.getBounds().pad(0.1));
    }
}


function updateRoadTable(roads) {
    const tbody = document.getElementById('roadTableBody');
    tbody.innerHTML = '';

    if (roads.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-muted">
                    No roads selected within budget
                </td>
            </tr>
        `;
        return;
    }

    roads.forEach((road, index) => {
        const riskBadge = getRiskBadge(road.risk_score, road.risk_category);
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><span class="badge bg-primary">${index + 1}</span></td>
            <td><strong>${road.road_name}</strong><br>
                <small class="text-muted">${road.area} - ${road.zone}</small></td>
            <td>${riskBadge}</td>
            <td><span class="badge bg-danger">${road.accidents}</span></td>
            <td>${road.traffic.toLocaleString()}</td>
            <td>$${road.repair_cost.toLocaleString()}</td>
            <td><span class="badge bg-success">Selected</span></td>
        `;
        tbody.appendChild(row);
    });
}


function getRiskBadge(score, category) {
    let color, text;
    
    if (category === 'High') {
        color = 'danger';
        text = `${score} (High)`;
    } else if (category === 'Medium') {
        color = 'warning';
        text = `${score} (Medium)`;
    } else {
        color = 'success';
        text = `${score} (Low)`;
    }
    
    return `<span class="badge bg-${color}">${text}</span>`;
}


function exportData() {
    if (!currentData) {
        alert('No data to export');
        return;
    }

    const dataStr = JSON.stringify(currentData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = 'road-analysis-' + new Date().toISOString().split('T')[0] + '.json';
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
}


function formatCurrency(amount) {
    if (amount >= 1000000) {
        return '$' + (amount / 1000000).toFixed(1) + 'M';
    } else if (amount >= 1000) {
        return '$' + (amount / 1000).toFixed(0) + 'k';
    } else {
        return '$' + amount.toFixed(0);
    }
}


function showProgress(show) {
    document.getElementById('progressIndicator').style.display = show ? 'block' : 'none';
    document.getElementById('analyzeBtn').disabled = show;
}
