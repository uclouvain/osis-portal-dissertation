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

import osis_dissertation_sdk
from django.conf import settings
from osis_dissertation_sdk.api import proposition_dissertation_api
from osis_dissertation_sdk.model.proposition_dissertation_detail import PropositionDissertationDetail
from osis_dissertation_sdk.model.proposition_dissertation_row import PropositionDissertationRow

from base.models.person import Person
from base.utils.api_utils import gather_all_api_paginated_results
from frontoffice.settings.osis_sdk import dissertation as dissertation_sdk
from frontoffice.settings.osis_sdk.utils import build_mandatory_auth_headers

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class PropositionDissertationService:
    CONFIGURATION = dissertation_sdk.build_configuration()

    @classmethod
    @gather_all_api_paginated_results
    def search(cls, term: str, person: Person, **kwargs) -> List[PropositionDissertationRow]:
        with osis_dissertation_sdk.ApiClient(cls.CONFIGURATION) as api_client:
            api_instance = proposition_dissertation_api.PropositionDissertationApi(api_client)
            kwargs['limit'] = 100
            api_response = api_instance.propositions_list(
                search=term,
                **build_mandatory_auth_headers(person),
                **kwargs
            )
            return api_response

    @classmethod
    def get(cls, uuid: str, person: Person) -> PropositionDissertationDetail:
        with osis_dissertation_sdk.ApiClient(cls.CONFIGURATION) as api_client:
            api_instance = proposition_dissertation_api.PropositionDissertationApi(api_client)
            return api_instance.proposition_infos(
                uuid=uuid,
                **build_mandatory_auth_headers(person),
            )

    @classmethod
    def update_proposition_dissertation_file(cls, person, data, uuid=None):
        with osis_dissertation_sdk.ApiClient(cls.CONFIGURATION) as api_client:
            api_instance = proposition_dissertation_api.PropositionDissertationApi(api_client)
            return api_instance.update_proposition_dissertation_file(
                uuid=str(uuid),
                dissertation_file=data,
                **build_mandatory_auth_headers(person),
            )

    @classmethod
    def retrieve_proposition_dissertation_file(cls, person, uuid=None):
        with osis_dissertation_sdk.ApiClient(cls.CONFIGURATION) as api_client:
            api_instance = proposition_dissertation_api.PropositionDissertationApi(api_client)
            return api_instance.retrieve_proposition_dissertation_file(
                uuid=str(uuid),
                **build_mandatory_auth_headers(person),
            )
