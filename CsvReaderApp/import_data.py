import csv
from django.core.management.base import BaseCommand
from CsvReaderApp.models import Defect

class Command(BaseCommand):
    help = 'Import data from CSV file'

    def handle(self, *args, **kwargs):
        with open('structuredata.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                Defect.objects.create(
                    line_number=row[0],
                    structure_id=row[1],
                    inspection_status=row[2],
                    file=row[3],
                    feature=row[4],
                    defect=row[5], 
                    description=row[6],
                    severity=row[7],
                    position=row[8]
                )
