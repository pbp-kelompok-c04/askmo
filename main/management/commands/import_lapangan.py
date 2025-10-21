import csv
import io
import re
from decimal import Decimal
from django.core.management.base import BaseCommand
from main.models import Lapangan
import urllib.request 

class Command(BaseCommand):
    help = 'Imports or updates Lapangan data from a live Google Sheet CSV URL'

    def handle(self, *args, **options):
        
        google_sheet_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQbSY08jMXwk_6tygh3715T0WtXkbONAKySVsTTu67CQAeTc_6IWZax7YqpgMUvzmoVf0m7STaNq0Bt/pub?gid=0&single=true&output=csv'

        # Clear existing data. This makes it an "update" script.
        self.stdout.write(self.style.WARNING('Clearing existing Lapangan data...'))
        Lapangan.objects.all().delete()

        self.stdout.write(f'Importing Lapangan data from Google Sheet...')
        
        try:
            # Download the data
            response = urllib.request.urlopen(google_sheet_url)
            # Read and decode the data as text
            csv_data = response.read().decode('utf-8')
            # Use io.StringIO to treat the text as a file
            csv_file = io.StringIO(csv_data)

            # Read the CSV data
            reader = csv.DictReader(csv_file)
            
            count = 0
            for row in reader:
                # Skip empty rows
                if not row.get('LAPANGAN'):
                    continue

                try:
                    # --- Parse data from your specific columns ---
                    
                    # Parse rating: "4.5/5 (293 ratings)" -> 4.5
                    rating_val = 0.0
                    if row.get('RATING'):
                        rating_match = re.match(r'([\d\.]+)', row['RATING'])
                        if rating_match:
                            rating_val = float(rating_match.group(1))

                    # Parse refund: "Bisa" -> True
                    is_refund = row.get('REFUND', '').strip().lower() == 'bisa'
                    
                    # Parse olahraga: "Sepak Bola" -> "sepakbola"
                    olahraga_val = row.get('BIDANG OLAHRAGA', 'lainnya').strip().lower().replace(' ', '')
                    
                    # Parse harga, use 0 if empty
                    price_str = row.get('HARGA PER SESI (MULAI DARI)', '0').strip()
                    
                    # Remove all non-numeric characters (like "Rp", ".", and spaces)
                    cleaned_price_str = re.sub(r'[^\d]', '', price_str)
                    
                    # If the string was "Gratis" or "-" it will be empty. Default to 0.
                    if not cleaned_price_str:
                        cleaned_price_str = '0'
                        
                    # Now, it's safe to convert
                    tarif_val = Decimal(cleaned_price_str)

                    # Map CSV columns to model fields
                    Lapangan.objects.create(
                        nama=row['LAPANGAN'],
                        kecamatan=row.get('KECAMATAN') or None,
                        alamat=row['DESKRIPSI LAPANGAN'], # ini yang alamat ya
                        deskripsi=row.get('DESKRIPSI') or None, 
                        thumbnail=row.get('GAMBAR LAPANGAN (URL)') or None,
                        kontak=row.get('CP LAPANGAN') or None,
                        olahraga=olahraga_val,
                        tarif_per_sesi=tarif_val,
                        rating=rating_val,
                        refund=is_refund,
                        review=row.get('REVIEW') or None,
                        fasilitas=row.get('FASILITAS') or None,
                        peraturan=row.get('ATURAN') or None
                    )
                    count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error importing row: {row.get('LAPANGAN')}. Error: {e}"))
            
            self.stdout.write(self.style.SUCCESS(f'Successfully imported/updated {count} lapangan.'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An unexpected error occurred: {e}'))