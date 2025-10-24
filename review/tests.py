from django.test import TestCase
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
import uuid
import json

from main.models import Lapangan
from coach.models import Coach
from review.models import Review, ReviewCoach
from main.forms import ReviewForm, ReviewCoachForm


class ReviewLapanganTestCase(TestCase):
    def setUp(self):
        """Setup data untuk testing review lapangan"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Buat lapangan untuk testing
        self.lapangan = Lapangan.objects.create(
            id=uuid.uuid4(),
            nama="Lapangan Test",
            alamat="Alamat Test",
            kecamatan="Test Kecamatan",
            olahraga="Sepak Bola",
            rating=4.5,
            original_rating=4.0,
            tarif_per_sesi=100000,
            refund=True,
            kontak="08123456789",
            deskripsi="Deskripsi test",
            fasilitas="Fasilitas test",
            peraturan="Peraturan test"
        )
        
        # Buat review untuk testing
        self.review = Review.objects.create(
            lapangan=self.lapangan,
            reviewer_name="Test Reviewer",
            rating=4.5,
            review_text="Review text test",
            gambar="https://example.com/image.jpg"
        )

    def test_show_review_lapangan_success(self):
        """Test menampilkan halaman review lapangan"""
        response = self.client.get(
            reverse('review:show_review_lapangan', args=[self.lapangan.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lapangan Test")
        self.assertTemplateUsed(response, 'review/lapangan/review_lapangan.html')

    def test_show_review_lapangan_not_found(self):
        """Test menampilkan review lapangan yang tidak ada"""
        fake_id = uuid.uuid4()
        response = self.client.get(
            reverse('review:show_review_lapangan', args=[fake_id])
        )
        self.assertEqual(response.status_code, 404)

    def test_show_feeds_review_lapangan(self):
        """Test menampilkan feeds review lapangan"""
        response = self.client.get(
            reverse('review:show_feeds_review_lapangan', args=[self.lapangan.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lapangan Test")
        self.assertTemplateUsed(response, 'review/lapangan/feeds_review_lapangan.html')

    def test_show_form_review_lapangan_get(self):
        """Test menampilkan form review lapangan (GET)"""
        response = self.client.get(
            reverse('review:show_form_review_lapangan', args=[self.lapangan.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review/lapangan/form_review_lapangan.html')
        self.assertIsInstance(response.context['review_form'], ReviewForm)

    def test_show_form_review_lapangan_post_valid(self):
        """Test submit form review lapangan (POST valid)"""
        data = {
            'reviewer_name': 'New Reviewer',
            'rating': 5.0,
            'review_text': 'Excellent field!',
            'gambar': ''
        }
        response = self.client.post(
            reverse('review:show_form_review_lapangan', args=[self.lapangan.id]),
            data
        )
        # Cek apakah redirect ke feeds review
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Review.objects.filter(reviewer_name='New Reviewer').exists())

    def test_get_single_review_json(self):
        """Test mendapatkan single review dalam format JSON"""
        response = self.client.get(
            reverse('review:get_single_review_json', args=[self.review.id])
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['reviewer_name'], 'Test Reviewer')
        self.assertEqual(float(data['rating']), 4.5)

    def test_get_single_review_json_not_found(self):
        """Test mendapatkan review yang tidak ada"""
        response = self.client.get(
            reverse('review:get_single_review_json', args=[999])
        )
        self.assertEqual(response.status_code, 404)

    def test_show_edit_review_lapangan_get(self):
        """Test menampilkan form edit review (GET)"""
        response = self.client.get(
            reverse('review:show_edit_review_lapangan', args=[self.review.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review/lapangan/edit_review_lapangan.html')

    def test_show_edit_review_lapangan_post(self):
        """Test submit form edit review (POST)"""
        data = {
            'reviewer_name': 'Updated Reviewer',
            'rating': 3.0,
            'review_text': 'Updated review text',
            'gambar': ''
        }
        response = self.client.post(
            reverse('review:show_edit_review_lapangan', args=[self.review.id]),
            data
        )
        # Cek apakah redirect ke feeds review
        self.assertEqual(response.status_code, 302)
        
        # Refresh dari database
        self.review.refresh_from_db()
        self.assertEqual(self.review.reviewer_name, 'Updated Reviewer')
        self.assertEqual(float(self.review.rating), 3.0)

    def test_add_review_lapangan_ajax_valid(self):
        """Test menambah review via AJAX (valid)"""
        data = {
            'reviewer_name': 'AJAX Reviewer',
            'rating': 4.0,
            'review_text': 'AJAX review text',
            'gambar': ''
        }
        response = self.client.post(
            reverse('review:add_review_lapangan', args=[self.lapangan.id]),
            data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertTrue(Review.objects.filter(reviewer_name='AJAX Reviewer').exists())

    def test_add_review_lapangan_ajax_invalid(self):
        """Test menambah review via AJAX (invalid data)"""
        data = {
            'reviewer_name': '',  # Nama kosong
            'rating': 6.0,  # Rating di luar range
            'review_text': '',
            'gambar': ''
        }
        response = self.client.post(
            reverse('review:add_review_lapangan', args=[self.lapangan.id]),
            data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')

    def test_update_lapangan_rating_function(self):
        """Test fungsi update rating lapangan"""
        from review.views import update_lapangan_rating
        
        # Test dengan review baru
        initial_rating = self.lapangan.rating
        new_rating = update_lapangan_rating(self.lapangan)
        
        # Refresh dari database
        self.lapangan.refresh_from_db()
        self.assertNotEqual(initial_rating, new_rating)
        self.assertEqual(self.lapangan.rating, new_rating)

    def test_get_reviews_json_lapangan(self):
        """Test mendapatkan semua review lapangan dalam JSON"""
        response = self.client.get(
            reverse('review:get_reviews_json_lapangan', args=[self.lapangan.id])
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)

    def test_update_review_ajax(self):
        """Test update review via AJAX"""
        data = {
            'reviewer_name': 'Updated AJAX',
            'rating': 2.5,
            'review_text': 'Updated via AJAX',
            'gambar': ''
        }
        response = self.client.post(
            reverse('review:update_review', args=[self.review.id]),
            data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Refresh dari database
        self.review.refresh_from_db()
        self.assertEqual(self.review.reviewer_name, 'Updated AJAX')

    def test_delete_review_ajax(self):
        """Test delete review via AJAX"""
        review_id = self.review.id
        response = self.client.post(
            reverse('review:delete_review', args=[review_id])
        )
        self.assertEqual(response.status_code, 200)
        
        # Cek apakah review sudah dihapus
        with self.assertRaises(Review.DoesNotExist):
            Review.objects.get(pk=review_id)


class ReviewCoachTestCase(TestCase):
    def setUp(self):
        """Setup data untuk testing review coach"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='coachuser',
            password='coachpass123'
        )
        
        # Buat coach untuk testing
        self.coach = Coach.objects.create(
            name="Coach Test",
            sport_branch="Basketball",
            location="Jakarta",
            contact="08123456789",
            experience="5 years experience",
            certifications="Certified Coach"
        )
        
        # Buat review coach untuk testing
        self.review_coach = ReviewCoach.objects.create(
            coach=self.coach,
            reviewer_name="Coach Reviewer",
            rating=5,
            review_text="Great coach!",
            user=self.user
        )

    def test_show_feeds_review_coach(self):
        """Test menampilkan feeds review coach"""
        response = self.client.get(
            reverse('review:show_feeds_review_coach', args=[self.coach.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Coach Test")
        self.assertTemplateUsed(response, 'review/coach/feeds_review_coach.html')

    def test_show_form_review_coach_authenticated(self):
        """Test menampilkan form review coach (authenticated)"""
        self.client.login(username='coachuser', password='coachpass123')
        response = self.client.get(
            reverse('review:show_form_review_coach', args=[self.coach.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review/coach/form_review_coach.html')

    def test_show_form_review_coach_post(self):
        """Test submit form review coach"""
        self.client.login(username='coachuser', password='coachpass123')
        data = {
            'reviewer_name': 'New Coach Reviewer',
            'rating': 4,
            'review_text': 'Good coaching!'
        }
        response = self.client.post(
            reverse('review:show_form_review_coach', args=[self.coach.id]),
            data
        )
        # Cek apakah redirect ke feeds review
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ReviewCoach.objects.filter(reviewer_name='New Coach Reviewer').exists())

    def test_edit_review_coach_authenticated(self):
        """Test edit review coach (authenticated user)"""
        self.client.login(username='coachuser', password='coachpass123')
        response = self.client.get(
            reverse('review:edit_review_coach', args=[self.review_coach.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review/coach/edit_review_coach.html')

    def test_edit_review_coach_unauthorized(self):
        """Test edit review coach (unauthorized user)"""
        # Buat user lain
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        self.client.login(username='otheruser', password='otherpass123')
        
        response = self.client.get(
            reverse('review:edit_review_coach', args=[self.review_coach.id])
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_review_coach_authorized(self):
        """Test delete review coach (authorized user)"""
        self.client.login(username='coachuser', password='coachpass123')
        review_id = self.review_coach.id
        
        response = self.client.post(
            reverse('review:delete_review_coach', args=[review_id])
        )
        self.assertEqual(response.status_code, 200)
        
        # Cek apakah review sudah dihapus
        with self.assertRaises(ReviewCoach.DoesNotExist):
            ReviewCoach.objects.get(pk=review_id)

    def test_delete_review_coach_unauthorized(self):
        """Test delete review coach (unauthorized user)"""
        # Buat user lain
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        self.client.login(username='otheruser', password='otherpass123')
        
        response = self.client.post(
            reverse('review:delete_review_coach', args=[self.review_coach.id])
        )
        self.assertEqual(response.status_code, 403)

    def test_get_reviews_json_coach(self):
        """Test mendapatkan review coach dalam JSON"""
        response = self.client.get(
            reverse('review:get_reviews_json_coach', args=[self.coach.id])
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)


class ReviewModelsTestCase(TestCase):
    def setUp(self):
        """Setup untuk testing models"""
        self.user = User.objects.create_user(
            username='modeluser',
            password='modelpass123'
        )
        
        self.lapangan = Lapangan.objects.create(
            id=uuid.uuid4(),
            nama="Model Test Field",
            alamat="Test Address"
        )
        
        self.coach = Coach.objects.create(
            name="Model Test Coach",
            sport_branch="Tennis"
        )

    def test_review_creation(self):
        """Test pembuatan model Review"""
        review = Review.objects.create(
            lapangan=self.lapangan,
            reviewer_name="Model Reviewer",
            rating=4.5,
            review_text="Test review text"
        )
        self.assertEqual(str(review), f'Review oleh Model Reviewer untuk Model Test Field - Rating: 4.5')
        self.assertEqual(review.lapangan, self.lapangan)

    def test_review_coach_creation(self):
        """Test pembuatan model ReviewCoach"""
        review_coach = ReviewCoach.objects.create(
            coach=self.coach,
            reviewer_name="Coach Model Reviewer",
            rating=5,
            review_text="Excellent coach",
            user=self.user
        )
        self.assertEqual(str(review_coach), f"Review for Model Test Coach by Coach Model Reviewer")
        self.assertEqual(review_coach.coach, self.coach)

    def test_review_coach_permissions(self):
        """Test permissions pada ReviewCoach"""
        review_coach = ReviewCoach.objects.create(
            coach=self.coach,
            reviewer_name="Permission Reviewer",
            rating=4,
            review_text="Test permissions",
            user=self.user
        )
        
        # Test can_edit dengan user yang benar
        self.assertTrue(review_coach.can_edit(self.user))
        
        # Test can_edit dengan user yang salah
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        self.assertFalse(review_coach.can_edit(other_user))
        
        # Test can_delete
        self.assertTrue(review_coach.can_delete(self.user))
        self.assertFalse(review_coach.can_delete(other_user))


class ReviewFormsTestCase(TestCase):
    def test_review_form_valid(self):
        """Test ReviewForm dengan data valid"""
        form_data = {
            'reviewer_name': 'Form Tester',
            'rating': 4.5,
            'review_text': 'This is a test review',
            'gambar': ''
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_review_form_invalid_rating(self):
        """Test ReviewForm dengan rating invalid"""
        form_data = {
            'reviewer_name': 'Form Tester',
            'rating': 6.0,  # Rating di atas 5.0
            'review_text': 'This is a test review',
            'gambar': ''
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)

    def test_review_coach_form_valid(self):
        """Test ReviewCoachForm dengan data valid"""
        form_data = {
            'reviewer_name': 'Coach Form Tester',
            'rating': 5,
            'review_text': 'Great coach!'
        }
        form = ReviewCoachForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_review_coach_form_invalid_rating(self):
        """Test ReviewCoachForm dengan rating invalid"""
        form_data = {
            'reviewer_name': 'Coach Form Tester',
            'rating': 6,  # Rating di atas 5
            'review_text': 'Great coach!'
        }
        form = ReviewCoachForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)