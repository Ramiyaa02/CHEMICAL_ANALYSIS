import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import FileUpload from './components/FileUpload';
import DatasetList from './components/DatasetList';
import DataVisualization from './components/DataVisualization';

// Configure axios with basic auth
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';
const username = 'admin';
const password = 'admin123';

axios.defaults.auth = {
  username: username,
  password: password
};

function App() {
  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [summary, setSummary] = useState(null);
  const [equipment, setEquipment] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/datasets/`);
      setDatasets(response.data);
      if (response.data.length > 0 && !selectedDataset) {
        handleDatasetSelect(response.data[0].id);
      }
    } catch (error) {
      console.error('Error fetching datasets:', error);
      alert('Error fetching datasets. Make sure the backend is running.');
    }
  };

  const handleDatasetSelect = async (datasetId) => {
    setSelectedDataset(datasetId);
    setLoading(true);
    try {
      const [summaryResponse, equipmentResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/datasets/${datasetId}/summary/`),
        axios.get(`${API_BASE_URL}/datasets/${datasetId}/equipment/`)
      ]);
      setSummary(summaryResponse.data);
      setEquipment(equipmentResponse.data);
    } catch (error) {
      console.error('Error fetching dataset data:', error);
      alert('Error fetching dataset data');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async () => {
    await fetchDatasets();
  };

  const handleDownloadPDF = async () => {
    if (!selectedDataset) return;
    try {
      const response = await axios.get(
        `${API_BASE_URL}/datasets/${selectedDataset}/pdf/`,
        { responseType: 'blob' }
      );
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `equipment_report_${selectedDataset}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert('Error downloading PDF');
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Chemical Equipment Parameter Visualizer</h1>
        <p>Hybrid Web + Desktop Application</p>
      </header>
      
      <main className="App-main">
        <div className="upload-section">
          <FileUpload onUpload={handleFileUpload} />
        </div>

        <div className="content-section">
          <div className="datasets-panel">
            <h2>📁 Datasets (Last 5)</h2>
            <DatasetList
              datasets={datasets}
              selectedDataset={selectedDataset}
              onSelect={handleDatasetSelect}
            />
            {selectedDataset && (
              <button
                className="pdf-button"
                onClick={handleDownloadPDF}
                disabled={loading}
              >
                📄 Download PDF Report
              </button>
            )}
          </div>

          <div className="visualization-panel">
            {loading ? (
              <div className="loading">⏳ Loading data...</div>
            ) : summary && equipment.length > 0 ? (
              <DataVisualization summary={summary} equipment={equipment} />
            ) : (
              <div className="no-data">
                <p>📊 No data available. Please upload a CSV file to visualize equipment data.</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
