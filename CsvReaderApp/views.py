import csv
import os
import ast
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
            if os.path.exists(file_path):
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
            columns = []
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
            item = row[selected_column]
            try:
                # Attempt to parse the item as a list
                parsed_items = ast.literal_eval(item)
                if isinstance(parsed_items, list):
                    for defect in parsed_items:
                        defect_counts[defect.strip()] += 1
                else:
                    # If not a list, treat it as a single defect
                    defect_counts[item.strip()] += 1
            except (ValueError, SyntaxError):
                # If parsing fails, treat it as a single defect string
                defect_counts[item.strip()] += 1
    return defect_counts

def generate_bar_chart(defect_counts, file_name, selected_column):
    total_counts = sum(defect_counts.values())
    threshold = total_counts * 0.05  # 5% of total

    # Aggregate small counts into 'Others'
    aggregated_counts = Counter()
    for defect, count in defect_counts.items():
        if count < threshold:
            aggregated_counts['Others'] += count
        else:
            aggregated_counts[defect] = count

    values = list(aggregated_counts.keys())
    counts = [aggregated_counts[value] for value in values]

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.bar(values, counts, color='skyblue')
    ax.set_xlabel('Values')
    ax.set_ylabel('Count')
    ax.set_title(f'Distribution of {selected_column}')
    ax.tick_params(axis='x', rotation=45)

    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    plt.savefig(file_path, format='png', bbox_inches='tight')
    plt.close()

    return os.path.join(settings.MEDIA_URL, file_name)
