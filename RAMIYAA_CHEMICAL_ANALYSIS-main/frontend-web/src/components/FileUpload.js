import React, { useState } from 'react';
import axios from 'axios';
import './FileUpload.css';

const API_BASE_URL = 'http://localhost:8000/api';

function FileUpload({ onUpload }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setMessage('');
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage('Please select a file');
      return;
    }

    setUploading(true);
    setMessage('');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', file.name);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setMessage('File uploaded successfully!');
      setFile(null);
      document.getElementById('file-input').value = '';
      if (onUpload) {
        onUpload();
      }
    } catch (error) {
      setMessage(
        error.response?.data?.error || 'Error uploading file. Make sure the backend is running and file format is correct.'
      );
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="file-upload">
      <h2>📤 Upload CSV File</h2>
      <div className="upload-controls">
        <input
          id="file-input"
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          disabled={uploading}
        />
        <button
          onClick={handleUpload}
          disabled={uploading || !file}
          className="upload-button"
        >
          {uploading ? '⏳ Uploading...' : '🚀 Upload'}
        </button>
      </div>
      {message && (
        <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
          {message.includes('Error') ? '❌' : '✅'} {message}
        </div>
      )}
      <p className="help-text">
        💡 <strong>CSV Format:</strong> Equipment Name, Type, Flowrate, Pressure, Temperature
      </p>
    </div>
  );
}

export default FileUpload;
