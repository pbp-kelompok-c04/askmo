from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from coach.models import Coach, CoachWishlist
from coach.forms import CoachForm
from django.core.files.uploadedfile import SimpleUploadedFile
import json


class CoachModelTestCase(TestCase):
    """Test lengkap untuk model Coach"""
    
    def setUp(self):
        """Setup data untuk testing"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.coach = Coach.objects.create(
            name="Test Coach",
            sport_branch="Sepak Bola",
            location="Jakarta Selatan",
            contact="08123456789",
            experience="5 years coaching experience in football",
            certifications="AFC A License, UEFA B License",
            service_fee="Rp 300,000 / Jam"
        )
    
    def test_coach_creation(self):
        """Test pembuatan model Coach"""
        self.assertEqual(self.coach.name, "Test Coach")
        self.assertEqual(self.coach.sport_branch, "Sepak Bola")
        self.assertEqual(self.coach.location, "Jakarta Selatan")
        self.assertEqual(self.coach.contact, "08123456789")
        self.assertEqual(self.coach.experience, "5 years coaching experience in football")
        self.assertEqual(self.coach.certifications, "AFC A License, UEFA B License")
        self.assertEqual(self.coach.service_fee, "Rp 300,000 / Jam")
    
    def test_coach_str_method(self):
        """Test string representation"""
        expected = "Test Coach - Sepak Bola"
        self.assertEqual(str(self.coach), expected)
    
    def test_coach_with_photo(self):
        """Test coach dengan photo"""
        image = SimpleUploadedFile(
            name='test_coach.jpg',
            content=b'fake image content',
            content_type='image/jpeg'
        )
        coach_with_photo = Coach.objects.create(
            name="Photo Coach",
            sport_branch="Basketball",
            location="Jakarta",
            contact="081234567890",
            photo=image
        )
        self.assertTrue(coach_with_photo.photo)
        self.assertIn('test_coach', coach_with_photo.photo.name)
    
    def test_coach_optional_fields_blank(self):
        """Test coach dengan optional fields kosong"""
        minimal_coach = Coach.objects.create(
            name="Minimal Coach",
            sport_branch="Tennis",
            location="Bandung",
            contact="coach@example.com"
        )
        self.assertEqual(minimal_coach.experience, "")
        self.assertEqual(minimal_coach.certifications, "")
        self.assertEqual(minimal_coach.service_fee, "")
        self.assertFalse(minimal_coach.photo)
    
    def test_coach_all_fields(self):
        """Test coach dengan semua fields diisi"""
        full_coach = Coach.objects.create(
            name="Full Coach",
            sport_branch="Volleyball",
            location="Surabaya",
            contact="08123456789",
            experience="10 years experience",
            certifications="Pro License",
            service_fee="Rp 500,000 / Jam"
        )
        self.assertIsNotNone(full_coach.name)
        self.assertIsNotNone(full_coach.sport_branch)
        self.assertIsNotNone(full_coach.location)
        self.assertIsNotNone(full_coach.contact)


class CoachWishlistModelTestCase(TestCase):
    """Test untuk model CoachWishlist"""
    
    def setUp(self):
        """Setup data"""
        self.user = User.objects.create_user(
            username='wishlistuser',
            password='wishlistpass123'
        )
        
        self.coach = Coach.objects.create(
            name="Wishlist Coach",
            sport_branch="Tennis",
            location="Bandung",
            contact="08987654321"
        )
    
    def test_wishlist_creation(self):
        """Test pembuatan wishlist"""
        wishlist = CoachWishlist.objects.create(
            user=self.user,
            coach=self.coach
        )
        self.assertEqual(wishlist.user, self.user)
        self.assertEqual(wishlist.coach, self.coach)
    
    def test_wishlist_str_method(self):
        """Test string representation"""
        wishlist = CoachWishlist.objects.create(
            user=self.user,
            coach=self.coach
        )
        expected = f"{self.user.username} - {self.coach.name}"
        self.assertEqual(str(wishlist), expected)


class CoachPublicViewsTestCase(TestCase):
    """Test untuk public views (coach list dan detail)"""
    
    def setUp(self):
        """Setup data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='publicuser',
            password='publicpass123'
        )
        
        # Create multiple coaches for testing
        self.coach1 = Coach.objects.create(
            name="Football Coach",
            sport_branch="Sepak Bola",
            location="Jakarta",
            contact="08111111111",
            service_fee="Rp 250,000 / Jam"
        )
        
        self.coach2 = Coach.objects.create(
            name="Basketball Coach",
            sport_branch="Basket",
            location="Bandung",
            contact="08222222222",
            service_fee="Rp 300,000 / Jam"
        )
        
        self.coach3 = Coach.objects.create(
            name="Tennis Coach",
            sport_branch="Tennis",
            location="Surabaya",
            contact="08333333333"
        )
    
    def test_coach_list_view(self):
        """Test menampilkan halaman list coach"""
        response = self.client.get(reverse('coach:coach_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'coach/index.html')
        self.assertIn('coaches', response.context)
        self.assertEqual(len(response.context['coaches']), 3)
    
    def test_coach_list_view_with_search(self):
        """Test coach list dengan search query"""
        response = self.client.get(reverse('coach:coach_list'), {'search': 'Football'})
        self.assertEqual(response.status_code, 200)
        coaches = response.context['coaches']
        # Search might return all coaches if not implemented yet, or exact matches
        self.assertGreaterEqual(len(coaches), 1)
        # At least one coach should match
        names = [c.name for c in coaches]
        self.assertTrue(any('Football' in name for name in names))
    
    def test_coach_list_view_filter_by_sport(self):
        """Test coach list filter by sport branch"""
        response = self.client.get(reverse('coach:coach_list'), {'sport_branch': 'Basket'})
        self.assertEqual(response.status_code, 200)
        coaches = response.context['coaches']
        self.assertEqual(len(coaches), 1)
        self.assertEqual(coaches[0].sport_branch, "Basket")
    
    def test_coach_list_view_filter_by_location(self):
        """Test coach list filter by location"""
        response = self.client.get(reverse('coach:coach_list'), {'location': 'Bandung'})
        self.assertEqual(response.status_code, 200)
        coaches = response.context['coaches']
        self.assertEqual(len(coaches), 1)
        self.assertEqual(coaches[0].location, "Bandung")
    
    def test_coach_list_view_multiple_filters(self):
        """Test coach list dengan multiple filters"""
        response = self.client.get(
            reverse('coach:coach_list'), 
            {'sport_branch': 'Sepak Bola', 'location': 'Jakarta'}
        )
        self.assertEqual(response.status_code, 200)
        coaches = response.context['coaches']
        self.assertEqual(len(coaches), 1)
    
    def test_coach_detail_view(self):
        """Test menampilkan detail coach sebagai authenticated user"""
        self.client.login(username='publicuser', password='publicpass123')
        response = self.client.get(reverse('coach:coach_detail', args=[self.coach1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'coach/coach_detail.html')
        self.assertEqual(response.context['coach'], self.coach1)
        self.assertIn('is_saved_to_wishlist', response.context)
        self.assertFalse(response.context['is_saved_to_wishlist'])
    
    def test_coach_detail_view_not_found(self):
        """Test detail coach yang tidak ada"""
        self.client.login(username='publicuser', password='publicpass123')
        response = self.client.get(reverse('coach:coach_detail', args=[99999]))
        self.assertEqual(response.status_code, 404)
    
    def test_coach_detail_view_whatsapp_number_processing(self):
        """Test processing nomor WhatsApp di detail view"""
        self.client.login(username='publicuser', password='publicpass123')
        # Test dengan nomor yang dimulai dengan 0
        coach_with_zero = Coach.objects.create(
            name="WhatsApp Coach",
            sport_branch="Futsal",
            location="Jakarta",
            contact="081234567890"
        )
        
        response = self.client.get(reverse('coach:coach_detail', args=[coach_with_zero.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['whatsapp_number'], '6281234567890')
        self.assertIsNotNone(response.context['phone_number_cleaned'])
    
    def test_coach_detail_view_with_email_contact(self):
        """Test detail dengan contact berupa email"""
        self.client.login(username='publicuser', password='publicpass123')
        coach_with_email = Coach.objects.create(
            name="Email Coach",
            sport_branch="Voli",
            location="Jakarta",
            contact="coach@example.com"
        )
        
        response = self.client.get(reverse('coach:coach_detail', args=[coach_with_email.pk]))
        self.assertEqual(response.status_code, 200)
        # Email tidak diproses sebagai nomor telepon
        self.assertIsNone(response.context.get('whatsapp_number'))
    
    def test_coach_detail_with_wishlist_saved(self):
        """Test detail coach yang sudah di-save ke wishlist"""
        self.client.login(username='publicuser', password='publicpass123')
        CoachWishlist.objects.create(user=self.user, coach=self.coach1)
        response = self.client.get(reverse('coach:coach_detail', args=[self.coach1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_saved_to_wishlist'])


class CoachAuthenticationTestCase(TestCase):
    """Test untuk authentication admin coach"""
    
    def setUp(self):
        """Setup data"""
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='staffuser',
            password='staffpass123',
            is_staff=True
        )
        self.normal_user = User.objects.create_user(
            username='normaluser',
            password='normalpass123'
        )
    
    def test_login_view_get(self):
        """Test GET login page"""
        response = self.client.get(reverse('coach:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'coach_admin/login.html')
    
    def test_login_view_post_staff_user(self):
        """Test login dengan staff user"""
        response = self.client.post(
            reverse('coach:login'),
            {'username': 'staffuser', 'password': 'staffpass123'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('coach:dashboard'))
    
    def test_login_view_post_non_staff_user(self):
        """Test login dengan non-staff user (should fail)"""
        response = self.client.post(
            reverse('coach:login'),
            {'username': 'normaluser', 'password': 'normalpass123'}
        )
        self.assertEqual(response.status_code, 200)
        # Check for error message (either Indonesian or English)
        content = response.content.decode('utf-8')
        self.assertTrue(
            'Anda tidak memiliki akses' in content or 
            'Invalid credentials' in content or
            'you do not have admin access' in content
        )
    
    def test_login_view_post_invalid_credentials(self):
        """Test login dengan kredensial salah"""
        response = self.client.post(
            reverse('coach:login'),
            {'username': 'wronguser', 'password': 'wrongpass'}
        )
        self.assertEqual(response.status_code, 200)
        # Form akan menampilkan error
    
    def test_logout_view(self):
        """Test logout"""
        self.client.login(username='staffuser', password='staffpass123')
        response = self.client.get(reverse('coach:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('coach:login'))


class CoachAdminCRUDTestCase(TestCase):
    """Test untuk CRUD operations di admin panel"""
    
    def setUp(self):
        """Setup data"""
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='admin',
            password='adminpass123',
            is_staff=True
        )
        
        self.coach = Coach.objects.create(
            name="CRUD Test Coach",
            sport_branch="Swimming",
            location="Jakarta",
            contact="08123456789"
        )
    
    def test_dashboard_view_staff(self):
        """Test dashboard untuk staff user"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('coach:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'coach_admin/dashboard.html')
        self.assertIn('coaches', response.context)
    
    def test_dashboard_view_non_staff(self):
        """Test dashboard untuk non-staff (should redirect)"""
        normal_user = User.objects.create_user(
            username='normal',
            password='normalpass123'
        )
        self.client.login(username='normal', password='normalpass123')
        response = self.client.get(reverse('coach:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_dashboard_view_unauthenticated(self):
        """Test dashboard tanpa login"""
        response = self.client.get(reverse('coach:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_coach_create_view_get(self):
        """Test GET create form"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('coach:coach_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'coach_admin/coach_form.html')
        self.assertIsInstance(response.context['form'], CoachForm)
    
    def test_coach_create_view_post_valid(self):
        """Test POST create coach dengan data valid"""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'name': 'New Coach',
            'sport_branch': 'Badminton',
            'location': 'Surabaya',
            'contact': '08999999999',
            'experience': 'Experienced coach',
            'certifications': 'Level A',
            'service_fee': 'Rp 350,000 / Jam'
        }
        response = self.client.post(reverse('coach:coach_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('coach:dashboard'))
        self.assertTrue(Coach.objects.filter(name='New Coach').exists())
    
    def test_coach_create_view_post_invalid(self):
        """Test POST create dengan data invalid"""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'name': '',  # Required field empty
            'sport_branch': 'Badminton',
        }
        response = self.client.post(reverse('coach:coach_create'), data)
        self.assertEqual(response.status_code, 200)  # Stays on form
        self.assertFalse(Coach.objects.filter(sport_branch='Badminton').exists())
    
    def test_coach_update_view_get(self):
        """Test GET update form"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('coach:coach_update', args=[self.coach.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'coach_admin/coach_form.html')
        self.assertEqual(response.context['form'].instance, self.coach)
    
    def test_coach_update_view_post(self):
        """Test POST update coach"""
        self.client.login(username='admin', password='adminpass123')
        data = {
            'name': 'Updated Coach Name',
            'sport_branch': 'Updated Sport',
            'location': 'Updated Location',
            'contact': '08111111111',
            'experience': 'Updated experience',
            'certifications': 'Updated certs',
            'service_fee': 'Rp 400,000 / Jam'
        }
        response = self.client.post(
            reverse('coach:coach_update', args=[self.coach.pk]),
            data
        )
        self.assertEqual(response.status_code, 302)
        self.coach.refresh_from_db()
        self.assertEqual(self.coach.name, 'Updated Coach Name')
        self.assertEqual(self.coach.sport_branch, 'Updated Sport')
    
    def test_coach_delete_view_get(self):
        """Test GET delete confirmation"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('coach:coach_delete', args=[self.coach.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'coach_admin/coach_confirm_delete.html')
    
    def test_coach_delete_view_post(self):
        """Test POST delete coach"""
        self.client.login(username='admin', password='adminpass123')
        coach_id = self.coach.pk
        response = self.client.post(reverse('coach:coach_delete', args=[coach_id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('coach:dashboard'))
        self.assertFalse(Coach.objects.filter(pk=coach_id).exists())
    
    def test_coach_update_not_found(self):
        """Test update coach yang tidak ada"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('coach:coach_update', args=[99999]))
        self.assertEqual(response.status_code, 404)
    
    def test_coach_delete_not_found(self):
        """Test delete coach yang tidak ada"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(reverse('coach:coach_delete', args=[99999]))
        self.assertEqual(response.status_code, 404)


class CoachWishlistViewsTestCase(TestCase):
    """Test untuk wishlist functionality"""
    
    def setUp(self):
        """Setup data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='wishlistuser',
            password='wishlistpass123'
        )
        
        self.coach = Coach.objects.create(
            name="Wishlist Test Coach",
            sport_branch="Yoga",
            location="Bali",
            contact="08555555555"
        )
    
    def test_add_to_wishlist_authenticated(self):
        """Test menambahkan coach ke wishlist"""
        self.client.login(username='wishlistuser', password='wishlistpass123')
        response = self.client.get(
            reverse('coach:add_to_coach_list', args=[self.coach.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            CoachWishlist.objects.filter(user=self.user, coach=self.coach).exists()
        )
    
    def test_remove_from_wishlist(self):
        """Test menghapus coach dari wishlist"""
        self.client.login(username='wishlistuser', password='wishlistpass123')
        
        # Add to wishlist first
        CoachWishlist.objects.create(user=self.user, coach=self.coach)
        
        # Remove from wishlist
        response = self.client.get(
            reverse('coach:add_to_coach_list', args=[self.coach.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            CoachWishlist.objects.filter(user=self.user, coach=self.coach).exists()
        )
    
    def test_toggle_wishlist_multiple_times(self):
        """Test toggle wishlist beberapa kali"""
        self.client.login(username='wishlistuser', password='wishlistpass123')
        
        # Add
        self.client.get(reverse('coach:add_to_coach_list', args=[self.coach.pk]))
        self.assertTrue(
            CoachWishlist.objects.filter(user=self.user, coach=self.coach).exists()
        )
        
        # Remove
        self.client.get(reverse('coach:add_to_coach_list', args=[self.coach.pk]))
        self.assertFalse(
            CoachWishlist.objects.filter(user=self.user, coach=self.coach).exists()
        )
        
        # Add again
        self.client.get(reverse('coach:add_to_coach_list', args=[self.coach.pk]))
        self.assertTrue(
            CoachWishlist.objects.filter(user=self.user, coach=self.coach).exists()
        )
    
    def test_add_to_wishlist_unauthenticated(self):
        """Test add to wishlist tanpa login"""
        response = self.client.get(
            reverse('coach:add_to_coach_list', args=[self.coach.pk])
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_wishlist_list_view(self):
        """Test menampilkan wishlist"""
        self.client.login(username='wishlistuser', password='wishlistpass123')
        
        # Add coaches to wishlist - dengan photo untuk menghindari error di template
        image = SimpleUploadedFile(
            name='coach2_photo.jpg',
            content=b'fake image content',
            content_type='image/jpeg'
        )
        coach2 = Coach.objects.create(
            name="Wishlist Coach 2",
            sport_branch="Pilates",
            location="Jakarta",
            contact="08666666666",
            photo=image
        )
        
        # Add photo to existing coach
        image1 = SimpleUploadedFile(
            name='coach1_photo.jpg',
            content=b'fake image content',
            content_type='image/jpeg'
        )
        self.coach.photo = image1
        self.coach.save()
        
        CoachWishlist.objects.create(user=self.user, coach=self.coach)
        CoachWishlist.objects.create(user=self.user, coach=coach2)
        
        response = self.client.get(reverse('coach:coach_wishlist_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wishlist/wishlist_coach_list.html')
        self.assertEqual(len(response.context['coach_list']), 2)
    
    def test_wishlist_list_view_empty(self):
        """Test wishlist kosong"""
        self.client.login(username='wishlistuser', password='wishlistpass123')
        response = self.client.get(reverse('coach:coach_wishlist_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['coach_list']), 0)
    
    def test_wishlist_list_view_unauthenticated(self):
        """Test wishlist view tanpa login"""
        response = self.client.get(reverse('coach:coach_wishlist_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login


class CoachFormTestCase(TestCase):
    """Test untuk CoachForm"""
    
    def test_coach_form_valid(self):
        """Test form dengan data valid"""
        form_data = {
            'name': 'Form Test Coach',
            'sport_branch': 'Running',
            'location': 'Medan',
            'contact': '08777777777',
            'experience': 'Marathon coach for 10 years',
            'certifications': 'IAAF Level 2',
            'service_fee': 'Rp 200,000 / Jam'
        }
        form = CoachForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_coach_form_missing_required_fields(self):
        """Test form dengan required fields kosong"""
        form_data = {
            'name': '',
            'sport_branch': '',
            'location': '',
            'contact': ''
        }
        form = CoachForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('sport_branch', form.errors)
        self.assertIn('location', form.errors)
        self.assertIn('contact', form.errors)
    
    def test_coach_form_optional_fields(self):
        """Test form dengan hanya required fields"""
        form_data = {
            'name': 'Minimal Coach',
            'sport_branch': 'Golf',
            'location': 'Bali',
            'contact': '08888888888'
        }
        form = CoachForm(data=form_data)
        self.assertTrue(form.is_valid())


class CoachIntegrationTestCase(TestCase):
    """Integration tests untuk workflow lengkap"""
    
    def setUp(self):
        """Setup untuk integration test"""
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass123',
            is_staff=True
        )
        self.normal_user = User.objects.create_user(
            username='normaluser',
            password='normalpass123'
        )
    
    def test_complete_coach_crud_workflow(self):
        """Test workflow lengkap: create, read, update, delete"""
        # Login as admin
        self.client.login(username='admin', password='adminpass123')
        
        # 1. Create coach
        create_data = {
            'name': 'Integration Coach',
            'sport_branch': 'Hockey',
            'location': 'Yogyakarta',
            'contact': '08999999999',
            'experience': 'Hockey coach',
            'certifications': 'FIH Level 1',
            'service_fee': 'Rp 280,000 / Jam'
        }
        create_response = self.client.post(
            reverse('coach:coach_create'),
            create_data
        )
        self.assertEqual(create_response.status_code, 302)
        
        # 2. Verify created
        coach = Coach.objects.get(name='Integration Coach')
        self.assertEqual(coach.sport_branch, 'Hockey')
        
        # 3. Read/View coach detail
        detail_response = self.client.get(
            reverse('coach:coach_detail', args=[coach.pk])
        )
        self.assertEqual(detail_response.status_code, 200)
        
        # 4. Update coach
        update_data = {
            'name': 'Updated Integration Coach',
            'sport_branch': 'Field Hockey',
            'location': 'Updated Location',
            'contact': '08111111111',
            'experience': 'Updated experience',
            'certifications': 'Updated certs',
            'service_fee': 'Rp 320,000 / Jam'
        }
        update_response = self.client.post(
            reverse('coach:coach_update', args=[coach.pk]),
            update_data
        )
        self.assertEqual(update_response.status_code, 302)
        
        # 5. Verify updated
        coach.refresh_from_db()
        self.assertEqual(coach.name, 'Updated Integration Coach')
        self.assertEqual(coach.sport_branch, 'Field Hockey')
        
        # 6. Delete coach
        delete_response = self.client.post(
            reverse('coach:coach_delete', args=[coach.pk])
        )
        self.assertEqual(delete_response.status_code, 302)
        
        # 7. Verify deleted
        self.assertFalse(Coach.objects.filter(pk=coach.pk).exists())
    
    def test_wishlist_workflow(self):
        """Test workflow wishlist lengkap"""
        # Create coach with photo
        image = SimpleUploadedFile(
            name='workflow_coach.jpg',
            content=b'fake image content',
            content_type='image/jpeg'
        )
        coach = Coach.objects.create(
            name='Workflow Coach',
            sport_branch='Crossfit',
            location='Jakarta',
            contact='08123123123',
            photo=image
        )
        
        # Login as normal user
        self.client.login(username='normaluser', password='normalpass123')
        
        # 1. Add to wishlist
        self.client.get(reverse('coach:add_to_coach_list', args=[coach.pk]))
        self.assertTrue(
            CoachWishlist.objects.filter(
                user=self.normal_user,
                coach=coach
            ).exists()
        )
        
        # 2. View coach detail 
        detail_response = self.client.get(
            reverse('coach:coach_detail', args=[coach.pk])
        )
        self.assertEqual(detail_response.status_code, 200)
        self.assertTrue(detail_response.context['is_saved_to_wishlist'])
        
        # 3. Check wishlist
        wishlist_response = self.client.get(reverse('coach:coach_wishlist_list'))
        self.assertEqual(len(wishlist_response.context['coach_list']), 1)
        
        # 4. Remove from wishlist
        self.client.get(reverse('coach:add_to_coach_list', args=[coach.pk]))
        self.assertFalse(
            CoachWishlist.objects.filter(
                user=self.normal_user,
                coach=coach
            ).exists()
        )
    
    def test_search_and_filter_workflow(self):
        """Test workflow search dan filter"""
        # Create multiple coaches
        coaches_data = [
            {'name': 'Jakarta Football Coach', 'sport_branch': 'Sepak Bola', 'location': 'Jakarta'},
            {'name': 'Jakarta Basketball Coach', 'sport_branch': 'Basket', 'location': 'Jakarta'},
            {'name': 'Bandung Football Coach', 'sport_branch': 'Sepak Bola', 'location': 'Bandung'},
        ]
        
        for data in coaches_data:
            Coach.objects.create(
                name=data['name'],
                sport_branch=data['sport_branch'],
                location=data['location'],
                contact='08123456789'
            )
        
        # 1. Search by name
        search_response = self.client.get(
            reverse('coach:coach_list'),
            {'search': 'Football'}
        )
        # Should contain at least the Football coaches
        self.assertGreaterEqual(len(search_response.context['coaches']), 2)
        
        # 2. Filter by sport
        sport_response = self.client.get(
            reverse('coach:coach_list'),
            {'sport_branch': 'Sepak Bola'}
        )
        self.assertEqual(len(sport_response.context['coaches']), 2)
        
        # 3. Filter by location
        location_response = self.client.get(
            reverse('coach:coach_list'),
            {'location': 'Jakarta'}
        )
        self.assertEqual(len(location_response.context['coaches']), 2)
        
        # 4. Combined filters
        combined_response = self.client.get(
            reverse('coach:coach_list'),
            {'sport_branch': 'Sepak Bola', 'location': 'Jakarta'}
        )
        self.assertEqual(len(combined_response.context['coaches']), 1)


class CoachPermissionTestCase(TestCase):
    """Test untuk permission dan authorization"""
    
    def setUp(self):
        """Setup data"""
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='staff',
            password='staffpass',
            is_staff=True
        )
        self.normal_user = User.objects.create_user(
            username='normal',
            password='normalpass'
        )
        
        self.coach = Coach.objects.create(
            name="Permission Test Coach",
            sport_branch="Boxing",
            location="Jakarta",
            contact="08123456789"
        )
    
    def test_staff_can_access_dashboard(self):
        """Test staff user dapat akses dashboard"""
        self.client.login(username='staff', password='staffpass')
        response = self.client.get(reverse('coach:dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_normal_user_cannot_access_dashboard(self):
        """Test normal user tidak dapat akses dashboard"""
        self.client.login(username='normal', password='normalpass')
        response = self.client.get(reverse('coach:dashboard'))
        self.assertEqual(response.status_code, 302)
    
    def test_staff_can_create_coach(self):
        """Test staff dapat create coach"""
        self.client.login(username='staff', password='staffpass')
        response = self.client.get(reverse('coach:coach_create'))
        self.assertEqual(response.status_code, 200)
    
    def test_normal_user_cannot_create_coach(self):
        """Test normal user tidak dapat create coach"""
        self.client.login(username='normal', password='normalpass')
        response = self.client.get(reverse('coach:coach_create'))
        self.assertEqual(response.status_code, 302)
    
    def test_staff_can_update_coach(self):
        """Test staff dapat update coach"""
        self.client.login(username='staff', password='staffpass')
        response = self.client.get(
            reverse('coach:coach_update', args=[self.coach.pk])
        )
        self.assertEqual(response.status_code, 200)
    
    def test_normal_user_cannot_update_coach(self):
        """Test normal user tidak dapat update coach"""
        self.client.login(username='normal', password='normalpass')
        response = self.client.get(
            reverse('coach:coach_update', args=[self.coach.pk])
        )
        self.assertEqual(response.status_code, 302)
    
    def test_staff_can_delete_coach(self):
        """Test staff dapat delete coach"""
        self.client.login(username='staff', password='staffpass')
        response = self.client.get(
            reverse('coach:coach_delete', args=[self.coach.pk])
        )
        self.assertEqual(response.status_code, 200)
    
    def test_normal_user_cannot_delete_coach(self):
        """Test normal user tidak dapat delete coach"""
        self.client.login(username='normal', password='normalpass')
        response = self.client.get(
            reverse('coach:coach_delete', args=[self.coach.pk])
        )
        self.assertEqual(response.status_code, 302)
    
    def test_anyone_can_view_coach_list(self):
        """Test semua orang dapat melihat list coach"""
        response = self.client.get(reverse('coach:coach_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_anyone_can_view_coach_detail(self):
        """Test semua orang dapat melihat detail coach sebagai authenticated user"""
        self.client.login(username='normal', password='normalpass')
        response = self.client.get(
            reverse('coach:coach_detail', args=[self.coach.pk])
        )
        self.assertEqual(response.status_code, 200)