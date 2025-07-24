from django.core.management.base import BaseCommand
from django.conf import settings
import os
import json
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Clean up old result files'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Delete files older than this many days (default: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
    
    def handle(self, *args, **options):
        output_dir = os.path.join(settings.BASE_DIR, 'output')
        
        if not os.path.exists(output_dir):
            self.stdout.write(self.style.WARNING('Output directory does not exist'))
            return
        
        cutoff_date = datetime.now() - timedelta(days=options['days'])
        deleted_count = 0
        
        for filename in os.listdir(output_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(output_dir, filename)
                
                try:
                    # Check file modification time
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_mtime < cutoff_date:
                        if options['dry_run']:
                            self.stdout.write(f'Would delete: {filename}')
                        else:
                            os.remove(file_path)
                            self.stdout.write(f'Deleted: {filename}')
                        deleted_count += 1
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing {filename}: {e}')
                    )
        
        if options['dry_run']:
            self.stdout.write(f'Would delete {deleted_count} files')
        else:
            self.stdout.write(f'Deleted {deleted_count} files older than {options["days"]} days')
