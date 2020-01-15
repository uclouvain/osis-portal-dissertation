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

from django.test import TestCase

from base.models.enums import offer_enrollment_state
from base.tests.factories.academic_year import AcademicYearFactory, create_current_academic_year
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.offer import OfferFactory
from base.tests.factories.offer_enrollment import OfferEnrollmentFactory
from base.tests.factories.offer_year import OfferYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory
from dissertation.models import dissertation
from dissertation.models.enums import dissertation_role_status
from dissertation.tests.factories.adviser import AdviserManagerFactory, AdviserTeacherFactory
from dissertation.tests.factories.dissertation import DissertationFactory
from dissertation.tests.factories.proposition_dissertation import PropositionDissertationFactory


class DissertationModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager = AdviserManagerFactory()
        a_person_teacher = PersonFactory(first_name='Pierre',
                                         last_name='Dupont')
        cls.teacher = AdviserTeacherFactory(person=a_person_teacher)
        a_person_student1 = PersonFactory(last_name="Durant",
                                          user=None)
        cls.student1 = StudentFactory(person=a_person_student1)
        a_person_student2 = PersonFactory(last_name="Robert",
                                          user=None)
        cls.student2 = StudentFactory(person=a_person_student2)
        cls.offer1 = OfferFactory()
        cls.education_group1 = EducationGroupFactory()
        cls.current_academic_year = create_current_academic_year()
        cls.current_offer_year = OfferYearFactory(
            acronym="test_offer1",
            offer=cls.offer1,
            academic_year=cls.current_academic_year
        )
        cls.current_education_group_year = EducationGroupYearFactory(
            education_group=cls.education_group1,
            acronym="test_offer1",
            academic_year=cls.current_academic_year
        )
        cls.education_group2 = EducationGroupFactory()
        cls.education_group_year = EducationGroupYearFactory(
            education_group=cls.education_group2,
            academic_year=cls.current_academic_year
        )
        cls.academic_year2015 = AcademicYearFactory(
            year=2015
        )
        cls.education_group_year_2015 = EducationGroupYearFactory(
            acronym="test_offer1",
            education_group=cls.education_group1,
            academic_year=cls.academic_year2015
        )
        cls.offer_enrollment_curent_year = OfferEnrollmentFactory(
            offer_year=cls.current_offer_year,
            student=cls.student1,
            education_group_year=cls.current_education_group_year,
            enrollment_state=offer_enrollment_state.SUBSCRIBED
        )
        cls.offer_enrollment2015 = OfferEnrollmentFactory(
            student=cls.student2,
            education_group_year=cls.education_group_year_2015,
            enrollment_state=offer_enrollment_state.SUBSCRIBED
        )
        cls.proposition_dissertation = PropositionDissertationFactory(author=cls.teacher,
                                                                      creator=a_person_teacher,
                                                                      title='Proposition de memoire'
                                                                      )
        cls.dissertation_to_put_back_to_draft = DissertationFactory(
            author=cls.student1,
            education_group_year=cls.current_education_group_year,
            proposition_dissertation=cls.proposition_dissertation,
            status='DIR_SUBMIT',
            active=True,
            dissertation_role__adviser=cls.teacher,
            dissertation_role__status=dissertation_role_status.PROMOTEUR
        )
        cls.dissertation_test_count2015 = DissertationFactory(
            author=cls.student1,
            education_group_year=cls.education_group_year_2015,
            proposition_dissertation=cls.proposition_dissertation,
            status='COM_SUBMIT',
            active=True,
            dissertation_role__adviser=cls.teacher,
            dissertation_role__status=dissertation_role_status.PROMOTEUR
        )
        cls.dissertation_test_count2017 = DissertationFactory(
            author=cls.student2,
            education_group_year=cls.current_education_group_year,
            proposition_dissertation=cls.proposition_dissertation,
            status='COM_SUBMIT',
            active=True,
            dissertation_role__adviser=cls.teacher,
            dissertation_role__status=dissertation_role_status.PROMOTEUR
        )

    def test_count_by_proposition(self):
        self.assertEqual(dissertation.count_by_proposition(self.proposition_dissertation), 2)

    def test_count_disser_submit_by_student_in_educ_group(self):
        self.assertEqual(dissertation.count_disser_submit_by_student_in_educ_group(
            self.student1,
            self.education_group_year_2015.education_group), 2
        )

    def test_go_back(self):
        self.client.force_login(self.manager.person.user)
        self.dissertation_to_put_back_to_draft.go_back()
        self.dissertation_to_put_back_to_draft.refresh_from_db()
        self.assertEqual(self.dissertation_to_put_back_to_draft.status, 'DRAFT')
        self.dissertation_test_count2017.go_back()
        self.assertNotEqual(self.dissertation_test_count2017.status, 'DRAFT')

    def test_get_next_status(self):
        next_status = dissertation.get_next_status(self.dissertation_test_count2017, "go_forward")
        self.assertEqual(next_status, self.dissertation_test_count2017.status)
        next_status = dissertation.get_next_status(self.dissertation_test_count2017, "")
        self.assertEqual(next_status, self.dissertation_test_count2017.status)

    def test_find_by_id(self):
        self.assertEqual(dissertation.find_by_id(self.dissertation_to_put_back_to_draft.id),
                         self.dissertation_to_put_back_to_draft)

    def test_by_user(self):
        dissertation_list = dissertation.find_by_user(self.student2)
        self.assertEqual(dissertation_list[0], self.dissertation_test_count2017)
