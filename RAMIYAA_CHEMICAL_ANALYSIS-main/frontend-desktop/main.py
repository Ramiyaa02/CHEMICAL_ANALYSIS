import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel, QListWidget, QTableWidget,
    QTableWidgetItem, QMessageBox, QTabWidget, QGroupBox, QGridLayout,
    QLineEdit, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import json
from datetime import datetime

API_BASE_URL = 'http://localhost:8000/api'
USERNAME = 'admin'
PASSWORD = 'admin123'


class LoginDialog(QDialog):
    """Simple login dialog for basic authentication"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Login')
        self.setModal(True)
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Username')
        self.username_input.setText(USERNAME)
        layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText(PASSWORD)
        layout.addWidget(self.password_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_credentials(self):
        return self.username_input.text(), self.password_input.text()


class DataFetchThread(QThread):
    """Thread for fetching data from API"""
    data_fetched = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, url, auth):
        super().__init__()
        self.url = url
        self.auth = auth
    
    def run(self):
        try:
            response = requests.get(self.url, auth=self.auth)
            response.raise_for_status()
            self.data_fetched.emit(response.json())
        except Exception as e:
            self.error_occurred.emit(str(e))


class MatplotlibWidget(QWidget):
    """Widget for displaying matplotlib charts"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def plot_pie_chart(self, labels, values, title):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.set_title(title)
        self.canvas.draw()
    
    def plot_bar_chart(self, labels, values, title, ylabel):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.bar(labels, values, color=['#667eea', '#764ba2', '#ff6384'])
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.tick_params(axis='x', rotation=45)
        self.canvas.draw()
    
    def plot_line_chart(self, x_data, y_data_list, labels, title):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        colors = ['#667eea', '#764ba2', '#ff6384']
        for i, (y_data, label) in enumerate(zip(y_data_list, labels)):
            ax.plot(x_data, y_data, marker='o', label=label, color=colors[i % len(colors)])
        ax.set_title(title)
        ax.set_xlabel('Equipment')
        ax.set_ylabel('Value')
        ax.legend()
        ax.tick_params(axis='x', rotation=45)
        self.canvas.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.auth = None
        self.datasets = []
        self.selected_dataset = None
        self.summary = None
        self.equipment = []
        
        self.init_ui()
        self.show_login()
    
    def init_ui(self):
        self.setWindowTitle('Chemical Equipment Parameter Visualizer - Desktop')
        self.setGeometry(100, 100, 1400, 900)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # Header
        header = QLabel('Chemical Equipment Parameter Visualizer')
        header.setFont(QFont('Arial', 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet('padding: 10px; background-color: #667eea; color: white;')
        main_layout.addWidget(header)
        
        # Upload section
        upload_group = QGroupBox('Upload CSV File')
        upload_layout = QHBoxLayout()
        self.upload_btn = QPushButton('Select CSV File')
        self.upload_btn.clicked.connect(self.upload_file)
        upload_layout.addWidget(self.upload_btn)
        upload_group.setLayout(upload_layout)
        main_layout.addWidget(upload_group)
        
        # Content section
        content_layout = QHBoxLayout()
        
        # Left panel - Datasets
        left_panel = QGroupBox('Datasets (Last 5)')
        left_layout = QVBoxLayout()
        self.dataset_list = QListWidget()
        self.dataset_list.itemClicked.connect(self.on_dataset_selected)
        left_layout.addWidget(self.dataset_list)
        
        self.pdf_btn = QPushButton('Download PDF Report')
        self.pdf_btn.clicked.connect(self.download_pdf)
        self.pdf_btn.setEnabled(False)
        left_layout.addWidget(self.pdf_btn)
        
        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(300)
        content_layout.addWidget(left_panel)
        
        # Right panel - Tabs
        tabs = QTabWidget()
        
        # Summary tab
        summary_tab = QWidget()
        summary_layout = QVBoxLayout()
        self.summary_label = QLabel('No data selected')
        self.summary_label.setAlignment(Qt.AlignCenter)
        summary_layout.addWidget(self.summary_label)
        summary_tab.setLayout(summary_layout)
        tabs.addTab(summary_tab, 'Summary')
        
        # Charts tab
        charts_tab = QWidget()
        charts_layout = QVBoxLayout()
        
        # Type distribution chart
        type_chart_group = QGroupBox('Equipment Type Distribution')
        type_chart_layout = QVBoxLayout()
        self.type_chart = MatplotlibWidget()
        type_chart_layout.addWidget(self.type_chart)
        type_chart_group.setLayout(type_chart_layout)
        charts_layout.addWidget(type_chart_group)
        
        # Averages chart
        avg_chart_group = QGroupBox('Average Parameters')
        avg_chart_layout = QVBoxLayout()
        self.avg_chart = MatplotlibWidget()
        avg_chart_layout.addWidget(self.avg_chart)
        avg_chart_group.setLayout(avg_chart_layout)
        charts_layout.addWidget(avg_chart_group)
        
        # Parameters line chart
        params_chart_group = QGroupBox('Equipment Parameters (Sample)')
        params_chart_layout = QVBoxLayout()
        self.params_chart = MatplotlibWidget()
        params_chart_layout.addWidget(self.params_chart)
        params_chart_group.setLayout(params_chart_layout)
        charts_layout.addWidget(params_chart_group)
        
        charts_tab.setLayout(charts_layout)
        tabs.addTab(charts_tab, 'Charts')
        
        # Table tab
        table_tab = QWidget()
        table_layout = QVBoxLayout()
        self.equipment_table = QTableWidget()
        self.equipment_table.setColumnCount(5)
        self.equipment_table.setHorizontalHeaderLabels([
            'Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'
        ])
        self.equipment_table.horizontalHeader().setStretchLastSection(True)
        table_layout.addWidget(self.equipment_table)
        table_tab.setLayout(table_layout)
        tabs.addTab(table_tab, 'Data Table')
        
        content_layout.addWidget(tabs)
        main_layout.addLayout(content_layout)
        
        central_widget.setLayout(main_layout)
    
    def show_login(self):
        login_dialog = LoginDialog(self)
        if login_dialog.exec_() == QDialog.Accepted:
            username, password = login_dialog.get_credentials()
            self.auth = (username, password)
            self.fetch_datasets()
        else:
            sys.exit()
    
    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Select CSV File', '', 'CSV Files (*.csv)'
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {'name': file_path.split('/')[-1]}
                response = requests.post(
                    f'{API_BASE_URL}/upload/',
                    files=files,
                    data=data,
                    auth=self.auth
                )
                response.raise_for_status()
                QMessageBox.information(self, 'Success', 'File uploaded successfully!')
                self.fetch_datasets()
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error uploading file: {str(e)}')
    
    def fetch_datasets(self):
        try:
            response = requests.get(f'{API_BASE_URL}/datasets/', auth=self.auth)
            response.raise_for_status()
            self.datasets = response.json()
            self.update_dataset_list()
            
            if self.datasets and not self.selected_dataset:
                self.on_dataset_selected_item(self.datasets[0]['id'])
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error fetching datasets: {str(e)}')
    
    def update_dataset_list(self):
        self.dataset_list.clear()
        for dataset in self.datasets:
            item_text = f"{dataset['name']}\n({dataset['total_count']} items, {dataset['uploaded_at'][:10]})"
            self.dataset_list.addItem(item_text)
    
    def on_dataset_selected(self, item):
        index = self.dataset_list.row(item)
        if index < len(self.datasets):
            self.on_dataset_selected_item(self.datasets[index]['id'])
    
    def on_dataset_selected_item(self, dataset_id):
        self.selected_dataset = dataset_id
        self.pdf_btn.setEnabled(True)
        
        # Fetch summary and equipment
        summary_thread = DataFetchThread(
            f'{API_BASE_URL}/datasets/{dataset_id}/summary/',
            self.auth
        )
        summary_thread.data_fetched.connect(self.on_summary_fetched)
        summary_thread.error_occurred.connect(self.on_error)
        summary_thread.start()
        
        equipment_thread = DataFetchThread(
            f'{API_BASE_URL}/datasets/{dataset_id}/equipment/',
            self.auth
        )
        equipment_thread.data_fetched.connect(self.on_equipment_fetched)
        equipment_thread.error_occurred.connect(self.on_error)
        equipment_thread.start()
    
    def on_summary_fetched(self, data):
        self.summary = data
        self.update_summary_display()
        self.update_charts()
    
    def on_equipment_fetched(self, data):
        self.equipment = data
        self.update_table()
        self.update_charts()
    
    def on_error(self, error_msg):
        QMessageBox.critical(self, 'Error', f'Error fetching data: {error_msg}')
    
    def update_summary_display(self):
        if not self.summary:
            return
        
        summary_text = f"""
        <h2>Dataset Summary</h2>
        <p><b>Dataset Name:</b> {self.summary['dataset_name']}</p>
        <p><b>Total Equipment:</b> {self.summary['total_count']}</p>
        <p><b>Uploaded:</b> {self.summary['uploaded_at']}</p>
        <hr>
        <h3>Average Values</h3>
        <p><b>Flowrate:</b> {self.summary['averages']['flowrate']:.2f}</p>
        <p><b>Pressure:</b> {self.summary['averages']['pressure']:.2f}</p>
        <p><b>Temperature:</b> {self.summary['averages']['temperature']:.2f}</p>
        <hr>
        <h3>Equipment Type Distribution</h3>
        """
        for eq_type, count in self.summary['type_distribution'].items():
            summary_text += f"<p><b>{eq_type}:</b> {count}</p>"
        
        self.summary_label.setText(summary_text)
    
    def update_charts(self):
        if not self.summary or not self.equipment:
            return
        
        # Type distribution pie chart
        type_labels = list(self.summary['type_distribution'].keys())
        type_values = list(self.summary['type_distribution'].values())
        self.type_chart.plot_pie_chart(type_labels, type_values, 'Equipment Type Distribution')
        
        # Averages bar chart
        avg_labels = ['Flowrate', 'Pressure', 'Temperature']
        avg_values = [
            self.summary['averages']['flowrate'],
            self.summary['averages']['pressure'],
            self.summary['averages']['temperature']
        ]
        self.avg_chart.plot_bar_chart(avg_labels, avg_values, 'Average Parameters', 'Value')
        
        # Parameters line chart (sample of first 10)
        sample_equipment = self.equipment[:10]
        equipment_names = [e['equipment_name'] for e in sample_equipment]
        flowrates = [e.get('flowrate', 0) or 0 for e in sample_equipment]
        pressures = [e.get('pressure', 0) or 0 for e in sample_equipment]
        temperatures = [e.get('temperature', 0) or 0 for e in sample_equipment]
        
        self.params_chart.plot_line_chart(
            equipment_names,
            [flowrates, pressures, temperatures],
            ['Flowrate', 'Pressure', 'Temperature'],
            'Equipment Parameters (Sample)'
        )
    
    def update_table(self):
        self.equipment_table.setRowCount(len(self.equipment))
        for row, item in enumerate(self.equipment):
            self.equipment_table.setItem(row, 0, QTableWidgetItem(item['equipment_name']))
            self.equipment_table.setItem(row, 1, QTableWidgetItem(item['equipment_type']))
            self.equipment_table.setItem(row, 2, QTableWidgetItem(
                f"{item['flowrate']:.2f}" if item.get('flowrate') else "N/A"
            ))
            self.equipment_table.setItem(row, 3, QTableWidgetItem(
                f"{item['pressure']:.2f}" if item.get('pressure') else "N/A"
            ))
            self.equipment_table.setItem(row, 4, QTableWidgetItem(
                f"{item['temperature']:.2f}" if item.get('temperature') else "N/A"
            ))
    
    def download_pdf(self):
        if not self.selected_dataset:
            return
        
        try:
            response = requests.get(
                f'{API_BASE_URL}/datasets/{self.selected_dataset}/pdf/',
                auth=self.auth,
                stream=True
            )
            response.raise_for_status()
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, 'Save PDF Report', f'equipment_report_{self.selected_dataset}.pdf',
                'PDF Files (*.pdf)'
            )
            
            if file_path:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                QMessageBox.information(self, 'Success', 'PDF report downloaded successfully!')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error downloading PDF: {str(e)}')


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
