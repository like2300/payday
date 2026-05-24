from django.test import TestCase
from django.urls import reverse
from django.http import JsonResponse
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import Fundraiser

class TemplateLoadingTest(TestCase):
    def test_fundraiser_detail_renders(self):
        dummy_image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        fundraiser = Fundraiser.objects.create(
            title="Test Fundraiser",
            slug="test-fundraiser",
            description="A test description",
            beneficiary_name="Beneficiary",
            beneficiary_phone="123456789",
            background_media=dummy_image
        )
        url = reverse('fundraiser_detail', kwargs={'slug': fundraiser.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, fundraiser.title)
        self.assertContains(response, "Donateurs")

    def test_donor_ajax_loading(self):
        dummy_image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        fundraiser = Fundraiser.objects.create(
            title="AJAX Test",
            slug="ajax-test",
            description="A test description",
            beneficiary_name="Beneficiary",
            beneficiary_phone="123456789",
            background_media=dummy_image
        )
        url = reverse('fundraiser_detail', kwargs={'slug': fundraiser.slug})
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, JsonResponse)
        data = response.json()
        self.assertIn('html', data)
        self.assertIn('total_pages', data)
