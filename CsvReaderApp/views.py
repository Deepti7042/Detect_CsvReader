import csv
import os
import matplotlib.pyplot as plt
from collections import Counter
from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse
import matplotlib
matplotlib.use('Agg')
from django.http import HttpResponse

def upload_file(request):
    if request.method == 'POST' and 'csv_file' in request.FILES:
        uploaded_file = request.FILES['csv_file']
        file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
        try:
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # Check if the file was saved successfully by verifying its existence
            if os.path.exists(file_path):
                # Redirect to column selection with the filename as a parameter
                return redirect(reverse('select_column') + f'?file={uploaded_file.name}')
            else:
                return HttpResponse("Failed to save the file.", status=500)
        except IOError as e:
            return HttpResponse(f"Error saving file: {e}", status=500)
    else:
        return render(request, 'CsvReaderApp/csv_upload.html')

def select_column(request):
    file_name = request.GET.get('file')
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    columns = get_csv_columns(file_path)
    return render(request, 'CsvReaderApp/column_select.html', {'columns': columns, 'file_name': file_name})

def get_csv_columns(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        try:
            columns = next(reader)
        except StopIteration:
            columns = []  # Handle empty files
    return columns

def generate_charts(request):
    if request.method == 'POST' and 'selected_column' in request.POST:
        selected_column = request.POST['selected_column']
        file_name = request.POST['file_name']
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        defect_counts = read_csv_and_process(file_path, selected_column)
        bar_chart_url = generate_bar_chart(defect_counts, 'bar_chart.png', selected_column)

        return render(request, 'CsvReaderApp/csv_data.html', {'bar_chart_url': bar_chart_url})
    else:
        return redirect('upload_file')

def read_csv_and_process(file_path, selected_column):
    defect_counts = Counter()
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            value = row.get(selected_column, '').strip().upper()
            if value:  # Ensure value is not empty
                defect_counts[value] += 1
    return defect_counts

def generate_bar_chart(defect_counts, file_name, selected_column):
    values = list(defect_counts.keys())
    counts = [defect_counts[value] for value in values]

    fig, ax = plt.subplots()
    ax.bar(values, counts, color='skyblue')
    ax.set_xlabel('Values')
    ax.set_ylabel('Count')
    ax.set_title(f'Distribution of {selected_column}')
    ax.tick_params(axis='x', rotation=45)

    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    plt.savefig(file_path, format='png')
    plt.close()

    return os.path.join(settings.MEDIA_URL, file_name)
