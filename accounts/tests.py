from django.test import TestCase

from accounts.models import ClinicianProfile, PatientProfile, User


class UserRBACTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin_user", password="pass123", role="admin"
        )
        self.clinician_assigned = User.objects.create_user(
            username="clinician_assigned", password="pass123", role="clinician"
        )
        ClinicianProfile.objects.create(user=self.clinician_assigned, can_view_all_patients=False)

        self.clinician_all = User.objects.create_user(
            username="clinician_all", password="pass123", role="clinician"
        )
        ClinicianProfile.objects.create(user=self.clinician_all, can_view_all_patients=True)

        self.patient_a = User.objects.create_user(
            username="patient_a", password="pass123", role="patient"
        )
        PatientProfile.objects.create(user=self.patient_a, clinician=self.clinician_assigned)

        self.patient_b = User.objects.create_user(
            username="patient_b", password="pass123", role="patient"
        )
        PatientProfile.objects.create(user=self.patient_b, clinician=self.clinician_all)

    def test_patient_can_only_access_own_data(self):
        self.assertTrue(self.patient_a.can_access_patient_data(self.patient_a))
        self.assertFalse(self.patient_a.can_access_patient_data(self.patient_b))

    def test_assigned_clinician_access_is_scoped_to_their_patients(self):
        self.assertTrue(self.clinician_assigned.can_access_patient_data(self.patient_a))
        self.assertFalse(self.clinician_assigned.can_access_patient_data(self.patient_b))

    def test_all_patients_clinician_can_access_any_patient(self):
        self.assertTrue(self.clinician_all.can_access_patient_data(self.patient_a))
        self.assertTrue(self.clinician_all.can_access_patient_data(self.patient_b))

    def test_admin_can_access_any_patient(self):
        self.assertTrue(self.admin.can_access_patient_data(self.patient_a))
        self.assertTrue(self.admin.can_access_patient_data(self.patient_b))

    def test_non_patient_target_is_denied(self):
        self.assertFalse(self.clinician_all.can_access_patient_data(self.admin))
        self.assertFalse(self.admin.can_access_patient_data(None))
