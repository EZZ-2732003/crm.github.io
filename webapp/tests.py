# webapp/tests.py
from django.test import TestCase
from django.utils import timezone
from .models import Reserve
from .forms import ReserveForm
import json

class ReservationTests(TestCase):
    def setUp(self):
        self.valid_data = {
            'patient_name': 'John Doe',
            'phone': '01234567890',
            'type': 'old',
            'date': timezone.now().date(),
            'time': '10:00 AM',
            'Branch': 'EL_Mohandsen',
            'services': json.dumps(['BOTOX', 'FILLER']),
            'notes': 'Test notes'
        }

    # Model Tests
    def test_create_reservation_with_services(self):
        reservation = Reserve.objects.create(**self.valid_data)
        self.assertEqual(reservation.services, ['BOTOX', 'FILLER'])
        self.assertEqual(reservation.status, 'pending')

    def test_service_validation_in_model(self):
        with self.assertRaises(Exception):
            Reserve.objects.create(
                **{**self.valid_data, 'services': ['INVALID_SERVICE']}
            )

    # Form Tests
    def test_valid_form_submission(self):
        form = ReserveForm(data={
            **self.valid_data,
            'services': ['BOTOX', 'FILLER']
        })
        self.assertTrue(form.is_valid())

    def test_form_with_invalid_service(self):
        form = ReserveForm(data={
            **self.valid_data,
            'services': ['INVALID_SERVICE']
        })
        self.assertFalse(form.is_valid())
        self.assertIn('services', form.errors)

    def test_form_with_empty_services(self):
        form = ReserveForm(data={
            **self.valid_data,
            'services': []
        })
        self.assertFalse(form.is_valid())
        self.assertIn('services', form.errors)

    def test_form_with_string_services(self):
        form = ReserveForm(data={
            **self.valid_data,
            'services': 'BOTOX,FILLER'
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['services'], ['BOTOX', 'FILLER'])

    # View Tests
    def test_successful_reservation_flow(self):
        response = self.client.post('/Schedule_Appointment', data={
            **self.valid_data,
            'services': ['BOTOX']
        })
        self.assertEqual(response.status_code, 302)  # Check redirect
        self.assertEqual(Reserve.objects.count(), 1)

    def test_invalid_reservation_flow(self):
        response = self.client.post('/Schedule_Appointment', data={
            **self.valid_data,
            'services': []
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required")

    # Edge Cases
    def test_duplicate_services(self):
        form = ReserveForm(data={
            **self.valid_data,
            'services': ['BOTOX', 'BOTOX']
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['services'], ['BOTOX'])

    def test_max_services(self):
        all_services = [choice[0] for choice in Reserve.SERVICE_CHOICES]
        form = ReserveForm(data={
            **self.valid_data,
            'services': all_services
        })
        self.assertTrue(form.is_valid())