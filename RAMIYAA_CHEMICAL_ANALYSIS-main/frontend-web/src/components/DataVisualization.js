import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Line, Pie } from 'react-chartjs-2';
import './DataVisualization.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

function DataVisualization({ summary, equipment }) {
  // Prepare type distribution chart data
  const typeDistributionData = {
    labels: Object.keys(summary.type_distribution),
    datasets: [
      {
        label: 'Equipment Count',
        data: Object.values(summary.type_distribution),
        backgroundColor: [
          'rgba(102, 126, 234, 0.8)',
          'rgba(118, 75, 162, 0.8)',
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 206, 86, 0.8)',
        ],
        borderColor: [
          'rgba(102, 126, 234, 1)',
          'rgba(118, 75, 162, 1)',
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  // Prepare parameter averages chart
  const averagesData = {
    labels: ['Flowrate', 'Pressure', 'Temperature'],
    datasets: [
      {
        label: 'Average Values',
        data: [
          summary.averages.flowrate,
          summary.averages.pressure,
          summary.averages.temperature,
        ],
        backgroundColor: 'rgba(102, 126, 234, 0.8)',
        borderColor: 'rgba(102, 126, 234, 1)',
        borderWidth: 1,
      },
    ],
  };

  // Prepare equipment parameters line chart (sample of first 10)
  const sampleEquipment = equipment.slice(0, 10);
  const equipmentNames = sampleEquipment.map((e) => e.equipment_name);
  const flowrates = sampleEquipment.map((e) => e.flowrate || 0);
  const pressures = sampleEquipment.map((e) => e.pressure || 0);
  const temperatures = sampleEquipment.map((e) => e.temperature || 0);

  const parametersData = {
    labels: equipmentNames,
    datasets: [
      {
        label: 'Flowrate',
        data: flowrates,
        borderColor: 'rgba(102, 126, 234, 1)',
        backgroundColor: 'rgba(102, 126, 234, 0.2)',
        tension: 0.4,
      },
      {
        label: 'Pressure',
        data: pressures,
        borderColor: 'rgba(118, 75, 162, 1)',
        backgroundColor: 'rgba(118, 75, 162, 0.2)',
        tension: 0.4,
      },
      {
        label: 'Temperature',
        data: temperatures,
        borderColor: 'rgba(255, 99, 132, 1)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        tension: 0.4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Equipment Parameters',
      },
    },
  };

  return (
    <div className="data-visualization">
      <div className="summary-section">
        <h2>📈 Dataset Summary</h2>
        <div className="summary-grid">
          <div className="summary-card">
            <h3>🔧 Total Equipment</h3>
            <p className="summary-value">{summary.total_count}</p>
          </div>
          <div className="summary-card">
            <h3>💧 Avg Flowrate</h3>
            <p className="summary-value">{summary.averages.flowrate.toFixed(2)}</p>
          </div>
          <div className="summary-card">
            <h3>⚡ Avg Pressure</h3>
            <p className="summary-value">{summary.averages.pressure.toFixed(2)}</p>
          </div>
          <div className="summary-card">
            <h3>🌡️ Avg Temperature</h3>
            <p className="summary-value">{summary.averages.temperature.toFixed(2)}</p>
          </div>
        </div>
      </div>

      <div className="charts-section">
        <div className="chart-container">
          <h3>📊 Equipment Type Distribution</h3>
          <div className="chart-wrapper">
            <Pie data={typeDistributionData} options={chartOptions} />
          </div>
        </div>

        <div className="chart-container">
          <h3>📈 Average Parameters</h3>
          <div className="chart-wrapper">
            <Bar data={averagesData} options={chartOptions} />
          </div>
        </div>

        <div className="chart-container full-width">
          <h3>📉 Equipment Parameters (Sample)</h3>
          <div className="chart-wrapper">
            <Line data={parametersData} options={chartOptions} />
          </div>
        </div>
      </div>

      <div className="table-section">
        <h3>📋 Equipment Data Table</h3>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Equipment Name</th>
                <th>Type</th>
                <th>Flowrate</th>
                <th>Pressure</th>
                <th>Temperature</th>
              </tr>
            </thead>
            <tbody>
              {equipment.map((item) => (
                <tr key={item.id}>
                  <td>{item.equipment_name}</td>
                  <td>{item.equipment_type}</td>
                  <td>{item.flowrate?.toFixed(2) || 'N/A'}</td>
                  <td>{item.pressure?.toFixed(2) || 'N/A'}</td>
                  <td>{item.temperature?.toFixed(2) || 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default DataVisualization;
