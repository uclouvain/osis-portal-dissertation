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

from base.tests.factories.academic_year import AcademicYearFactory, create_current_academic_year
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.offer import OfferFactory
from base.tests.factories.offer_enrollment import OfferEnrollmentFactory
from base.tests.factories.offer_year import OfferYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory
from dissertation.models import dissertation
from dissertation.tests.factories.adviser import AdviserManagerFactory, AdviserTeacherFactory
from dissertation.tests.factories.dissertation import DissertationFactory
from dissertation.tests.factories.proposition_dissertation import PropositionDissertationFactory


class DissertationModelTestCase(TestCase):
    def setUp(self):
        self.manager = AdviserManagerFactory()
        a_person_teacher = PersonFactory(first_name='Pierre',
                                                last_name='Dupont')
        self.teacher = AdviserTeacherFactory(person=a_person_teacher)
        a_person_student1 = PersonFactory(last_name="Durant",
                                                user=None)
        self.student1 = StudentFactory(person=a_person_student1)
        a_person_student2 = PersonFactory(last_name="Robert",
                                                user=None)
        self.student2 = StudentFactory(person=a_person_student2)
        self.offer1 = OfferFactory(title="test_offer1")
        self.current_academic_year = create_current_academic_year()
        self.current_offer_year = OfferYearFactory(
            acronym="test_offer1", offer=self.offer1,
            academic_year=self.current_academic_year
        )
        self.education_group = EducationGroupFactory()
        self.current_education_group_year = EducationGroupYearFactory(
            acronym="test_offer1",
            education_group =self.education_group,
            academic_year=self.current_academic_year
        )
        self.academic_year2015 = AcademicYearFactory(year=2015)
        self.offer_year_start2015 = OfferYearFactory(acronym="test_offer1", offer=self.offer1,
                                                  academic_year=self.academic_year2015)

        self.offer_enrollment2017 = OfferEnrollmentFactory(offer_year= self.current_offer_year,
                                                           student= self.student1)
        self.offer_enrollment2015 = OfferEnrollmentFactory(offer_year=self.offer_year_start2015,
                                                           student=self.student2)
        self.proposition_dissertation = PropositionDissertationFactory(author=self.teacher,
                                                                       creator=a_person_teacher,
                                                                       title='Proposition de memoire'
                                                                       )
        self.dissertation_to_put_back_to_draft = DissertationFactory(
            author=self.student1,
            offer_year_start=self.current_offer_year,
            proposition_dissertation=self.proposition_dissertation,
            status='DIR_SUBMIT',
            active=True,
            dissertation_role__adviser=self.teacher,
            dissertation_role__status='PROMOTEUR'
        )
        self.dissertation_test_count2015 = DissertationFactory(
            author=self.student1,
            offer_year_start=self.offer_year_start2015,
            proposition_dissertation=self.proposition_dissertation,
            status='COM_SUBMIT',
            active=True,
            dissertation_role__adviser=self.teacher,
            dissertation_role__status='PROMOTEUR'
        )

        self.dissertation_test_count2017 = DissertationFactory(
            author=self.student2,
            offer_year_start=self.current_offer_year,
            proposition_dissertation=self.proposition_dissertation,
            status='COM_SUBMIT',
            active=True,
            dissertation_role__adviser=self.teacher,
            dissertation_role__status='PROMOTEUR'
        )


    def test_count_by_proposition(self):
        self.client.force_login(self.manager.person.user)
        self.assertEqual(dissertation.count_by_proposition(self.proposition_dissertation), 2)

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