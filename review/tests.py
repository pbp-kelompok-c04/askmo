# review/test_tests.py
from django.test import TestCase
from decimal import Decimal

from .views import update_lapangan_rating
from review.models import Review
from main.models import Lapangan


class UpdateLapanganRatingTests(TestCase):
    def setUp(self):
        # Create a Lapangan with a known original_rating
        self.lapangan = Lapangan.objects.create(
            id='z72074e5-4f36-4074-9549-b3a985d85207',
            nama='Unit Test Field',
            original_rating=Decimal('3.5')
        )

    def test_returns_original_when_no_reviews(self):
        # Ensure there are no reviews for this lapangan
        Review.objects.filter(lapangan=self.lapangan).delete()
        new_rating = update_lapangan_rating(self.lapangan)
        # Should return the original rating as a float
        self.assertIsInstance(new_rating, float)
        self.assertEqual(new_rating, float(self.lapangan.original_rating))

    def test_calculates_correct_average_single_review(self):
        Review.objects.create(lapangan=self.lapangan, rating=Decimal('5.0'), review_text='single review')
        expected = (float(self.lapangan.original_rating) + 5.0) / (1 + 1)
        new_rating = update_lapangan_rating(self.lapangan)
        self.assertIsInstance(new_rating, float)
        self.assertAlmostEqual(new_rating, expected, places=6)

    def test_calculates_correct_average_multiple_reviews(self):
        # Add multiple reviews and verify the weighted average formula
        Review.objects.create(lapangan=self.lapangan, rating=Decimal('5.0'), review_text='r1')
        Review.objects.create(lapangan=self.lapangan, rating=Decimal('3.0'), review_text='r2')
        Review.objects.create(lapangan=self.lapangan, rating=Decimal('4.0'), review_text='r3')
        ratings_sum = 5.0 + 3.0 + 4.0
        count = 3
        expected = (float(self.lapangan.original_rating) + ratings_sum) / (1 + count)
        new_rating = update_lapangan_rating(self.lapangan)
        self.assertAlmostEqual(new_rating, expected, places=6)

    def test_precision_and_type(self):
        # Add reviews with decimal fractions to ensure precision handling
        Review.objects.create(lapangan=self.lapangan, rating=Decimal('4.25'), review_text='precise1')
        Review.objects.create(lapangan=self.lapangan, rating=Decimal('3.75'), review_text='precise2')
        ratings_sum = 4.25 + 3.75
        count = 2
        expected = (float(self.lapangan.original_rating) + ratings_sum) / (1 + count)
        new_rating = update_lapangan_rating(self.lapangan)
        self.assertIsInstance(new_rating, float)
        self.assertAlmostEqual(new_rating, expected, places=6)