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

from base.tests.factories.education_group import EducationGroupFactory
from dissertation.models import proposition_dissertation
from dissertation.tests.factories.offer_proposition import OfferPropositionFactory
from dissertation.tests.factories.proposition_dissertation import PropositionDissertationFactory
from dissertation.tests.factories.proposition_offer import PropositionOfferFactory


class PropositionDissertationModelTestCase(TestCase):
    def setUp(self):
        self.education_group2 = EducationGroupFactory()
        self.offer_prop2 = OfferPropositionFactory(education_group=self.education_group2)
        self.proposition_dissert_2 = PropositionDissertationFactory()
        self.prop_offer2 = PropositionOfferFactory(
            proposition_dissertation=self.proposition_dissert_2,
            offer_proposition=self.offer_prop2
        )
        self.prop_offer3 = PropositionOfferFactory(
            proposition_dissertation=self.proposition_dissert_2,
            offer_proposition=self.offer_prop2
        )

    def test_find_by_education_groups(self):
        query_set_proposition_dissertation = proposition_dissertation.find_by_education_groups(
            [self.education_group2, ])
        self.assertEqual(self.proposition_dissert_2, query_set_proposition_dissertation[0])
