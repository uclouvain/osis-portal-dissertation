##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import json
from unittest.mock import patch

from django.http import HttpResponse, HttpResponseRedirect
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory
from dissertation.forms import DissertationUpdateForm
from dissertation.models.enums import dissertation_role_status
from dissertation.tests.factories.adviser import AdviserManagerFactory, AdviserTeacherFactory
from dissertation.tests.factories.dissertation import DissertationFactory
from dissertation.tests.factories.offer_proposition import OfferPropositionFactory
from dissertation.tests.factories.proposition_dissertation import PropositionDissertationFactory
from osis_common.models import message_history
from osis_common.models import message_template


class DissertationViewTestCase(TestCase):
    fixtures = ['dissertation/fixtures/message_templates_dissertation.json', ]

    @classmethod
    def setUpTestData(cls):
        cls.maxDiff = None
        cls.manager = AdviserManagerFactory()
        a_person_teacher = PersonFactory(first_name='Pierre',
                                         last_name='Dupont')
        cls.teacher = AdviserTeacherFactory(person=a_person_teacher)
        a_person_student = PersonFactory(last_name="Durant")
        another_person_student = PersonFactory(last_name="Paul")
        cls.student = StudentFactory.create(person=a_person_student)
        cls.student_with_1_dissertation = StudentFactory(person=another_person_student)
        cls.education_group1 = EducationGroupFactory()
        cls.academic_year1 = AcademicYearFactory()
        cls.education_group_year1 = EducationGroupYearFactory(
            acronym="test_offer1",
            education_group=cls.education_group1,
            academic_year=cls.academic_year1
        )
        cls.offer_proposition1 = OfferPropositionFactory(education_group=cls.education_group1)
        cls.proposition_dissertation = PropositionDissertationFactory(
            author=cls.teacher,
            creator=a_person_teacher,
            title='Proposition 1212121'
        )
        cls.proposition_dissertation2 = PropositionDissertationFactory(
            author=cls.teacher,
            creator=a_person_teacher,
            title='Proposition 1212121'
        )

    def setUp(self):
        self.client.force_login(self.student.person.user)
        self.dissertation = DissertationFactory(
            author=self.student,
            title='Dissertation test',
            education_group_year=self.education_group_year1,
            proposition_dissertation=self.proposition_dissertation2,
            status='DIR_SUBMIT',
            active=True,
            dissertation_role__adviser=self.teacher,
            dissertation_role__status=dissertation_role_status.PROMOTEUR
        )
        self.dissertation_to_dir_submit = DissertationFactory(
            author=self.student_with_1_dissertation,
            status='DRAFT',
            active=True,
            dissertation_role__adviser=self.teacher,
            dissertation_role__status=dissertation_role_status.PROMOTEUR
        )

    def test_email_new_dissert(self):
        self.dissertation_test_email = DissertationFactory(
            author=self.student,
            title='Dissertation_test_email',
            education_group_year=self.education_group_year1,
            proposition_dissertation=self.proposition_dissertation,
            status='DRAFT',
            active=True,
            dissertation_role__adviser=self.teacher,
            dissertation_role__status=dissertation_role_status.PROMOTEUR
        )
        self.client.force_login(self.manager.person.user)
        count_messages_before_status_change = len(message_history.find_my_messages(self.teacher.person.id))
        self.dissertation_test_email.go_forward()
        message_history_result = message_history.find_my_messages(self.teacher.person.id)
        self.assertEqual(count_messages_before_status_change + 1, len(message_history_result))
        self.assertNotEqual(message_template.find_by_reference('dissertation_adviser_new_project_dissertation_txt'),
                            None)
        self.assertNotEqual(
            message_template.find_by_reference('dissertation_adviser_new_project_dissertation_html'),
            None)
        self.assertIn('Vous avez reçu une demande d\'encadrement de mémoire',
                      message_history_result.last().subject)

    def test_dissertation_to_dir_submit(self):
        self.client.force_login(self.student_with_1_dissertation.person.user)
        form = DissertationUpdateForm(
            dissertation=self.dissertation_to_dir_submit,
            person=self.student_with_1_dissertation.person,
            action="go_forward",
        )
        response = self.client.post(
            reverse('dissertation_to_dir_submit', args=[self.dissertation_to_dir_submit.pk]),
            {"form": form, }
        )
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)

    def test_dissertation_to_dir_submit_with_another_student(self):
        form = DissertationUpdateForm(
            dissertation=self.dissertation_to_dir_submit,
            person=self.student_with_1_dissertation.person,
            action="go_forward",
        )
        response = self.client.post(
            reverse('dissertation_to_dir_submit', args=[self.dissertation_to_dir_submit.pk]),
            {"form": form, }
        )
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)

    @patch("dissertation.forms.DissertationUpdateForm.is_valid", return_value=False)
    def test_dissertation_to_dir_submit_with_invalid_form(self, *args):
        self.client.force_login(self.student_with_1_dissertation.person.user)
        form = DissertationUpdateForm(
            dissertation=self.dissertation_to_dir_submit,
            person=self.student_with_1_dissertation.person,
            action="go_forward",
        )
        response = self.client.post(
            reverse('dissertation_to_dir_submit', args=[self.dissertation_to_dir_submit.pk]),
            {"form": form, }
        )
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_dissertation_back_to_draft(self):
        form = DissertationUpdateForm(
            dissertation=self.dissertation,
            person=self.student.person,
            action="go_back",
        )
        response = self.client.post(
            reverse('dissertation_back_to_draft', args=[self.dissertation.pk]),
            {"form": form, }
        )
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)
        self.dissertation.refresh_from_db()
        self.assertEqual(self.dissertation.status, 'DRAFT')

    @patch("dissertation.forms.DissertationUpdateForm.is_valid", return_value=False)
    def test_dissertation_back_to_draft_with_invalid_form(self, mock_form):
        form = DissertationUpdateForm(
            dissertation=self.dissertation,
            person=self.student.person,
            action="go_back",
        )
        response = self.client.post(
            reverse('dissertation_back_to_draft', args=[self.dissertation.pk]),
            {"form": form}
        )
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_dissertation_jury_new_view(self):
        response = self.client.post(
            reverse('add_reader', args=[self.dissertation.pk]), {
                "status": "READER",
                'adviser': self.teacher.pk,
                "dissertation": self.dissertation.pk
            }
        )
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)

    def test_dissertation_jury_new_view_without_student_logged(self):
        self.client.force_login(self.manager.person.user)
        response = self.client.post(
            reverse('add_reader', args=[self.dissertation.pk]), {
                "status": "READER",
                'adviser': self.teacher.pk,
                "dissertation": self.dissertation.pk
            }
        )
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)


class TestAdviserAutocomplete(TestCase):
    @classmethod
    def setUpTestData(cls):
        a_person_student = PersonFactory(last_name="Durant")
        cls.student = StudentFactory.create(person=a_person_student)
        cls.url = reverse('adviser-autocomplete')
        cls.person = PersonFactory(first_name="pierre")
        cls.adviser = AdviserTeacherFactory(person=cls.person)

    def test_when_filter(self):
        self.client.force_login(user=self.student.person.user)
        response = self.client.get(self.url, data={"q": 'pie'})
        self.assertEqual(response.status_code, HttpResponse.status_code)
        results = _get_results_from_autocomplete_response(response)
        expected_results = [{'text': self.adviser.person.first_name, 'id': str(self.adviser.pk)}]
        self.assertEqual(results[0].get('id'), expected_results[0].get('id'))


def _get_results_from_autocomplete_response(response):
    json_response = str(response.content, encoding='utf8')
    return json.loads(json_response)['results']
