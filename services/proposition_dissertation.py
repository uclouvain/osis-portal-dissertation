##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
import logging
from typing import List

from django.conf import settings
from osis_dissertation_sdk.model.proposition_dissertation_detail import PropositionDissertationDetail
from osis_dissertation_sdk.model.proposition_dissertation_row import PropositionDissertationRow

from frontoffice.settings.osis_sdk import dissertation as dissertation_sdk

from base.models.person import Person

import osis_dissertation_sdk
from osis_dissertation_sdk.api import proposition_dissertation_api


logger = logging.getLogger(settings.DEFAULT_LOGGER)


class PropositionDissertationService:
    @staticmethod
    def search(term: str, person: Person) -> List[PropositionDissertationRow]:
        # TODO: Support pagination
        configuration = dissertation_sdk.build_configuration(person)
        with osis_dissertation_sdk.ApiClient(configuration) as api_client:
            api_instance = proposition_dissertation_api.PropositionDissertationApi(api_client)
            api_response = api_instance.propositions_list(
                search=term,
                accept_language=person.language
            )
            return getattr(api_response, 'results', [])

    @staticmethod
    def get(uuid: str, person: Person) -> PropositionDissertationDetail:
        configuration = dissertation_sdk.build_configuration(person)
        with osis_dissertation_sdk.ApiClient(configuration) as api_client:
            api_instance = proposition_dissertation_api.PropositionDissertationApi(api_client)
            return api_instance.proposition_detail(
                uuid=uuid,
                accept_language=person.language
            )
