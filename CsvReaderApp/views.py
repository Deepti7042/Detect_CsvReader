import csv
import os
import matplotlib.pyplot as plt
from collections import Counter
from django.shortcuts import render
from django.conf import settings
import matplotlib
matplotlib.use('Agg')

def generate_charts(request):
    if request.method == 'POST' and request.FILES['csv_file']:
        uploaded_file = request.FILES['csv_file']
        file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        defect_counts = read_csv_and_process(file_path)
        bar_chart_url = generate_bar_chart(defect_counts, 'bar_chart.png')

        context = {'bar_chart_url': bar_chart_url}
        return render(request, 'CsvReaderApp/csv_data.html', context)
    else:
        return render(request, 'CsvReaderApp/csv_upload.html')

def read_csv_and_process(file_path):
    defect_counts = Counter()
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            severity = row['severity'].strip().upper()  # Assuming 'severity' is the correct column name
            if severity in ['LOW', 'MEDIUM', 'HIGH']:  # Filter unwanted values
                defect_counts[severity] += 1
    return defect_counts

def generate_bar_chart(defect_counts, file_name):
    severity_levels = ['LOW', 'MEDIUM', 'HIGH']
    severity_counts = {level: defect_counts.get(level, 0) for level in severity_levels}
    
    fig, ax = plt.subplots()
    ax.bar(severity_levels, [severity_counts[level] for level in severity_levels], color='skyblue')
    ax.set_xlabel('Severity')
    ax.set_ylabel('Count')
    ax.set_title('Defect Severity Distribution')
    ax.tick_params(axis='x', rotation=45)
    
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    plt.savefig(file_path, format='png')
    plt.close()

    return os.path.join(settings.MEDIA_URL, file_name)

# Note: Ensure that MEDIA_ROOT and MEDIA_URL are properly configured in your settings.py
