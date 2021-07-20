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

from django.conf import settings
from osis_dissertation_sdk.model.defend_period_enum import DefendPeriodEnum
from osis_dissertation_sdk.model.dissertation_create_command import DissertationCreateCommand

from frontoffice.settings.osis_sdk import dissertation as dissertation_sdk

from base.models.person import Person

import osis_dissertation_sdk
from osis_dissertation_sdk.api import dissertation_api


logger = logging.getLogger(settings.DEFAULT_LOGGER)


class DissertationService:
    @staticmethod
    def create(
            proposition_dissertation_uuid: str,
            title: str,
            description: str,
            defend_year: int,
            defend_period: str,
            location_uuid: str,
            education_group_year_uuid: str,
            person: Person
    ) -> str:
        configuration = dissertation_sdk.build_configuration(person)
        with osis_dissertation_sdk.ApiClient(configuration) as api_client:
            api_instance = dissertation_api.DissertationApi(api_client)
            cmd = DissertationCreateCommand(
                proposition_dissertation_uuid=proposition_dissertation_uuid,
                title=title,
                description=description,
                defend_year=defend_year,
                defend_period=DefendPeriodEnum(defend_period),
                location_uuid=location_uuid,
                education_group_year_uuid=education_group_year_uuid,
            )
            response = api_instance.dissertation_create(
                dissertation_create_command=cmd,
                accept_language=person.language,
            )
            return response.dissertation_uuid

    @staticmethod
    def update(
            uuid: str,
            title: str,
            description: str,
            defend_year: int,
            defend_period: str,
            location_uuid: str,
            person: Person
    ) -> str:
        configuration = dissertation_sdk.build_configuration(person)
        with osis_dissertation_sdk.ApiClient(configuration) as api_client:
            api_instance = dissertation_api.DissertationApi(api_client)


    @staticmethod
    def search(term: str, person: Person) -> str:
        # TODO Implement pagination if usefull
        configuration = dissertation_sdk.build_configuration(person)
        with osis_dissertation_sdk.ApiClient(configuration) as api_client:
            api_instance = dissertation_api.DissertationApi(api_client)
            response = api_instance.dissertation_list(
                limit=100,
                offset=0,
                search=term,
                accept_language=person.language
            )
            return getattr(response, 'results', [])

    @staticmethod
    def get(uuid: str, person: Person):
        configuration = dissertation_sdk.build_configuration(person)
        with osis_dissertation_sdk.ApiClient(configuration) as api_client:
            api_instance = dissertation_api.DissertationApi(api_client)
            return api_instance.dissertation_detail(
                uuid=uuid,
                accept_language=person.language
            )

    @staticmethod
    def deactivate(uuid: str, person: Person):
        configuration = dissertation_sdk.build_configuration(person)
        with osis_dissertation_sdk.ApiClient(configuration) as api_client:
            api_instance = dissertation_api.DissertationApi(api_client)
            api_instance.dissertation_deactivate(
                uuid=uuid,
                accept_language=person.language
            )

    @staticmethod
    def history(uuid: str, person: Person):
        # TODO Implement pagination if usefull
        configuration = dissertation_sdk.build_configuration(person)
        with osis_dissertation_sdk.ApiClient(configuration) as api_client:
            api_instance = dissertation_api.DissertationApi(api_client)
            response = api_instance.dissertation_history(
                uuid=uuid,
                accept_language=person.language
            )
            return getattr(response, 'results', [])
