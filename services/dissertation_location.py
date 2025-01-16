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

import osis_dissertation_sdk
from django.conf import settings
from osis_dissertation_sdk.api import dissertation_location_api

from base.models.person import Person
from frontoffice.settings.osis_sdk import dissertation as dissertation_sdk
from frontoffice.settings.osis_sdk.utils import build_mandatory_auth_headers

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class DissertationLocationService:

    @staticmethod
    def get_dissertation_locations_list(person: Person):
        configuration = dissertation_sdk.build_configuration()
        with osis_dissertation_sdk.ApiClient(configuration) as api_client:
            api_instance = dissertation_location_api.DissertationLocationApi(api_client)
            return api_instance.dissertation_locations_list(
                **build_mandatory_auth_headers(person),
            )
