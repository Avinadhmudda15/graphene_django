from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import ClinicianProfile, PatientProfile, User
from data_processing.models import Alert, Comment, PressureFrame, UploadSession


class DashboardAccessTests(TestCase):
    def setUp(self):
        self.clinician_limited = User.objects.create_user(
            username="clin_limited", password="pass123", role="clinician"
        )
        ClinicianProfile.objects.create(user=self.clinician_limited, can_view_all_patients=False)

        self.clinician_all = User.objects.create_user(
            username="clin_all", password="pass123", role="clinician"
        )
        ClinicianProfile.objects.create(user=self.clinician_all, can_view_all_patients=True)

        self.patient_assigned = User.objects.create_user(
            username="patient_assigned", password="pass123", role="patient"
        )
        PatientProfile.objects.create(user=self.patient_assigned, clinician=self.clinician_limited)

        self.patient_unassigned = User.objects.create_user(
            username="patient_unassigned", password="pass123", role="patient"
        )
        PatientProfile.objects.create(user=self.patient_unassigned, clinician=self.clinician_all)

        session_1 = UploadSession.objects.create(
            patient=self.patient_assigned,
            uploaded_by=self.clinician_limited,
            filename="test_20251011.csv",
            status="done",
        )
        session_2 = UploadSession.objects.create(
            patient=self.patient_unassigned,
            uploaded_by=self.clinician_all,
            filename="test_20251012.csv",
            status="done",
        )

        now = timezone.now()
        self.frame_assigned = PressureFrame.objects.create(
            patient=self.patient_assigned,
            session=session_1,
            frame_index=0,
            timestamp=now - timedelta(minutes=5),
            matrix_data=[1] * 1024,
            peak_pressure=650,
            contact_area_pct=42.0,
            avg_pressure=80.0,
            is_flagged=True,
        )
        self.frame_unassigned = PressureFrame.objects.create(
            patient=self.patient_unassigned,
            session=session_2,
            frame_index=0,
            timestamp=now - timedelta(minutes=2),
            matrix_data=[1] * 1024,
            peak_pressure=700,
            contact_area_pct=35.0,
            avg_pressure=75.0,
            is_flagged=True,
        )

        Alert.objects.create(
            patient=self.patient_assigned,
            frame=self.frame_assigned,
            timestamp=now - timedelta(minutes=5),
            severity="warning",
            message="Assigned patient alert",
        )
        Alert.objects.create(
            patient=self.patient_unassigned,
            frame=self.frame_unassigned,
            timestamp=now - timedelta(minutes=2),
            severity="warning",
            message="Unassigned patient alert",
        )

        self.comment_unassigned = Comment.objects.create(
            patient=self.patient_unassigned,
            frame=self.frame_unassigned,
            text="Need review",
        )

    def test_limited_clinician_cannot_read_unassigned_metrics(self):
        self.client.login(username="clin_limited", password="pass123")
        url = reverse("dashboard:api_metrics")
        response = self.client.get(url, {"hours": 6, "patient_id": self.patient_unassigned.pk})
        self.assertEqual(response.status_code, 403)

    def test_all_view_clinician_can_read_any_patient_metrics(self):
        self.client.login(username="clin_all", password="pass123")
        url = reverse("dashboard:api_metrics")
        response = self.client.get(url, {"hours": 6, "patient_id": self.patient_assigned.pk})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("labels", payload)
        self.assertIn("peak_pressure", payload)

    def test_patient_cannot_open_other_patient_frame(self):
        self.client.login(username="patient_assigned", password="pass123")
        url = reverse("dashboard:api_frame", kwargs={"pk": self.frame_unassigned.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_clinician_cannot_reply_to_unassigned_patient_comment(self):
        self.client.login(username="clin_limited", password="pass123")
        url = reverse("dashboard:clinician_reply", kwargs={"pk": self.comment_unassigned.pk})
        response = self.client.post(url, {"reply": "Please reposition regularly."})
        self.assertEqual(response.status_code, 302)

        self.comment_unassigned.refresh_from_db()
        self.assertEqual(self.comment_unassigned.clinician_reply, "")
        self.assertIsNone(self.comment_unassigned.reply_by)
