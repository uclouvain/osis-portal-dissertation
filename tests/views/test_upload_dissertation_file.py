# ##################################################################################################
#   OSIS stands for Open Student Information System. It's an application                           #
#   designed to manage the core business of higher education institutions,                         #
#   such as universities, faculties, institutes and professional schools.                          #
#   The core business involves the administration of students, teachers,                           #
#   courses, programs and so on.                                                                   #
#   Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)             #
#   This program is free software: you can redistribute it and/or modify                           #
#   it under the terms of the GNU General Public License as published by                           #
#   the Free Software Foundation, either version 3 of the License, or                              #
#   (at your option) any later version.                                                            #
#   This program is distributed in the hope that it will be useful,                                #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of                                 #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                                  #
#   GNU General Public License for more details.                                                   #
#   A copy of this license - GNU General Public License - is available                             #
#   at the root of the source code of this program.  If not,                                       #
#   see http://www.gnu.org/licenses/.                                                              #
# ##################################################################################################
from django.http import HttpResponseRedirect
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory
from base.tests.factories.user import UserFactory
from dissertation.tests.factories.dissertation import DissertationFactory
from dissertation.tests.factories.dissertation_document_file import DissertationDocumentFileFactory


class TestDeleteDissertationFileView(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.person = PersonFactory(user=self.user)
        self.student = StudentFactory(person=self.person)
        self.dissertation = DissertationFactory(author=self.student)
        self.dissertation_document = DissertationDocumentFileFactory(dissertation=self.dissertation)
        self.dissertation2 = DissertationFactory()
        self.dissertation_document2 = DissertationDocumentFileFactory(dissertation=self.dissertation2)
        self.client.force_login(self.student.person.user)

    def test_delete_file(self):
        response = self.client.post(
            reverse('dissertation_file_delete', args=[self.dissertation.pk])
        )
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)


