##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2018-2019 Université catholique de Louvain (http://www.uclouvain.be)
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

from base.tests.factories.education_group import EducationGroupFactory
from dissertation.models.offer_proposition import get_by_education_group, search_by_education_groups
from dissertation.tests.factories.offer_proposition import OfferPropositionFactory


class OfferPropositionModelTestCase(TestCase):
    def setUp(self):
        self.education_group1 = EducationGroupFactory()
        self.education_group2 = EducationGroupFactory()
        self.offer_prop1 = OfferPropositionFactory(education_group=self.education_group1)
        self.offer_prop2 = OfferPropositionFactory(education_group=self.education_group2)

    def test_get_by_education_group(self):
        self.assertEqual(get_by_education_group(self.education_group1), self.offer_prop1)
        self.assertEqual(get_by_education_group(self.education_group2), self.offer_prop2)

    def search_by_education_groups(self):
        self.assertCountEqual(
            search_by_education_groups([self.education_group1, self.education_group2]),
            [self.offer_prop1, self.offer_prop2])
