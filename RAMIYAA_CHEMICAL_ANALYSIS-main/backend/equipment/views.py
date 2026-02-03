import pandas as pd
import os
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import EquipmentDataset, Equipment
from .serializers import EquipmentDatasetSerializer, EquipmentSerializer
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from django.utils import timezone
from django.conf import settings


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_csv(request):
    """Upload and parse CSV file"""
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    
    # Validate file extension
    if not file.name.endswith('.csv'):
        return Response({'error': 'File must be a CSV'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Read CSV with pandas
        df = pd.read_csv(file)
        
        # Validate required columns
        required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return Response({
                'error': f'Missing required columns: {", ".join(missing_columns)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Clean column names (remove extra spaces)
        df.columns = df.columns.str.strip()
        
        # Create dataset record
        dataset = EquipmentDataset.objects.create(
            name=request.data.get('name', f'Dataset {timezone.now().strftime("%Y-%m-%d %H:%M")}'),
            total_count=len(df),
            file_name=file.name
        )
        
        # Create equipment records
        equipment_list = []
        for _, row in df.iterrows():
            equipment = Equipment(
                dataset=dataset,
                equipment_name=str(row['Equipment Name']).strip(),
                equipment_type=str(row['Type']).strip(),
                flowrate=pd.to_numeric(row['Flowrate'], errors='coerce'),
                pressure=pd.to_numeric(row['Pressure'], errors='coerce'),
                temperature=pd.to_numeric(row['Temperature'], errors='coerce'),
            )
            equipment_list.append(equipment)
        
        Equipment.objects.bulk_create(equipment_list)
        
        # Keep only last 5 datasets
        datasets = EquipmentDataset.objects.all().order_by('-uploaded_at')
        if datasets.count() > 5:
            for dataset_to_delete in datasets[5:]:
                dataset_to_delete.delete()
        
        serializer = EquipmentDatasetSerializer(dataset)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dataset_summary(request, dataset_id):
    """Get summary statistics for a dataset"""
    try:
        dataset = EquipmentDataset.objects.get(id=dataset_id)
        equipment = Equipment.objects.filter(dataset=dataset)
        
        # Calculate statistics
        flowrates = [e.flowrate for e in equipment if e.flowrate is not None]
        pressures = [e.pressure for e in equipment if e.pressure is not None]
        temperatures = [e.temperature for e in equipment if e.temperature is not None]
        
        # Equipment type distribution
        type_distribution = {}
        for e in equipment:
            type_distribution[e.equipment_type] = type_distribution.get(e.equipment_type, 0) + 1
        
        summary = {
            'dataset_id': dataset.id,
            'dataset_name': dataset.name,
            'total_count': dataset.total_count,
            'uploaded_at': dataset.uploaded_at,
            'averages': {
                'flowrate': sum(flowrates) / len(flowrates) if flowrates else 0,
                'pressure': sum(pressures) / len(pressures) if pressures else 0,
                'temperature': sum(temperatures) / len(temperatures) if temperatures else 0,
            },
            'type_distribution': type_distribution,
        }
        
        return Response(summary)
    
    except EquipmentDataset.DoesNotExist:
        return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dataset_list(request):
    """List all datasets (last 5)"""
    datasets = EquipmentDataset.objects.all().order_by('-uploaded_at')[:5]
    serializer = EquipmentDatasetSerializer(datasets, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def equipment_list(request, dataset_id):
    """List all equipment for a dataset"""
    try:
        dataset = EquipmentDataset.objects.get(id=dataset_id)
        equipment = Equipment.objects.filter(dataset=dataset)
        serializer = EquipmentSerializer(equipment, many=True)
        return Response(serializer.data)
    except EquipmentDataset.DoesNotExist:
        return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_pdf(request, dataset_id):
    """Generate PDF report for a dataset"""
    try:
        dataset = EquipmentDataset.objects.get(id=dataset_id)
        equipment = Equipment.objects.filter(dataset=dataset)
        
        # Calculate statistics
        flowrates = [e.flowrate for e in equipment if e.flowrate is not None]
        pressures = [e.pressure for e in equipment if e.pressure is not None]
        temperatures = [e.temperature for e in equipment if e.temperature is not None]
        
        # Equipment type distribution
        type_distribution = {}
        for e in equipment:
            type_distribution[e.equipment_type] = type_distribution.get(e.equipment_type, 0) + 1
        
        # Create PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="equipment_report_{dataset_id}.pdf"'
        
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(f"Equipment Dataset Report: {dataset.name}", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Summary
        summary_text = f"""
        <b>Dataset Information:</b><br/>
        Total Equipment: {dataset.total_count}<br/>
        Uploaded: {dataset.uploaded_at.strftime('%Y-%m-%d %H:%M')}<br/>
        File: {dataset.file_name}<br/>
        <br/>
        <b>Average Values:</b><br/>
        Flowrate: {sum(flowrates) / len(flowrates) if flowrates else 0:.2f}<br/>
        Pressure: {sum(pressures) / len(pressures) if pressures else 0:.2f}<br/>
        Temperature: {sum(temperatures) / len(temperatures) if temperatures else 0:.2f}<br/>
        <br/>
        <b>Equipment Type Distribution:</b><br/>
        """
        for eq_type, count in type_distribution.items():
            summary_text += f"{eq_type}: {count}<br/>"
        
        summary = Paragraph(summary_text, styles['Normal'])
        elements.append(summary)
        elements.append(Spacer(1, 12))
        
        # Equipment table
        table_data = [['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']]
        for e in equipment[:50]:  # Limit to first 50 for PDF
            table_data.append([
                e.equipment_name,
                e.equipment_type,
                f"{e.flowrate:.2f}" if e.flowrate else "N/A",
                f"{e.pressure:.2f}" if e.pressure else "N/A",
                f"{e.temperature:.2f}" if e.temperature else "N/A",
            ])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        return response
    
    except EquipmentDataset.DoesNotExist:
        return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)
