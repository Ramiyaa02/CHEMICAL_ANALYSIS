import React from 'react';
import './DatasetList.css';

function DatasetList({ datasets, selectedDataset, onSelect }) {
  if (datasets.length === 0) {
    return <p className="no-datasets">📭 No datasets available. Upload a CSV file to get started!</p>;
  }

  return (
    <div className="dataset-list">
      {datasets.map((dataset) => (
        <div
          key={dataset.id}
          className={`dataset-item ${selectedDataset === dataset.id ? 'selected' : ''}`}
          onClick={() => onSelect(dataset.id)}
        >
          <div className="dataset-name">📊 {dataset.name}</div>
          <div className="dataset-meta">
            <span>📦 {dataset.total_count} items</span>
            <span className="dataset-date">
              📅 {new Date(dataset.uploaded_at).toLocaleDateString()}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}

export default DatasetList;
