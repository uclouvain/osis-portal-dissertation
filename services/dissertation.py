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
from osis_dissertation_sdk.api import dissertation_api
from osis_dissertation_sdk.model.defend_period_enum import DefendPeriodEnum
from osis_dissertation_sdk.model.dissertation_back_to_draft_command import DissertationBackToDraftCommand
from osis_dissertation_sdk.model.dissertation_create_command import DissertationCreateCommand
from osis_dissertation_sdk.model.dissertation_jury_add_command import DissertationJuryAddCommand
from osis_dissertation_sdk.model.dissertation_submit_command import DissertationSubmitCommand
from osis_dissertation_sdk.model.dissertation_update_command import DissertationUpdateCommand

from base.models.person import Person
from frontoffice.settings.osis_sdk import dissertation as dissertation_sdk
from frontoffice.settings.osis_sdk.utils import build_mandatory_auth_headers

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class DissertationService:
    CONFIGURATION = dissertation_sdk.build_configuration()

    @classmethod
    def create(
            cls,
            proposition_dissertation_uuid: str,
            title: str,
            description: str,
            defend_year: int,
            defend_period: str,
            location_uuid: str,
            acronym: str,
            year: int,
            person: Person
    ) -> str:
        with osis_dissertation_sdk.ApiClient(cls.CONFIGURATION) as api_client:
            api_instance = dissertation_api.DissertationApi(api_client)
            cmd = DissertationCreateCommand(
                proposition_dissertation_uuid=proposition_dissertation_uuid,
                title=title,
                description=description,
                defend_year=defend_year,
                defend_period=DefendPeriodEnum(defend_period),
                location_uuid=location_uuid,
                acronym=acronym,
                year=year,
            )
            response = api_instance.dissertation_create(
                dissertation_create_command=cmd,
                **build_mandatory_auth_headers(person),
            )
            return response.dissertation_uuid

    @classmethod
    def update(
            cls,
            uuid: str,
            title: str,
            description: str,
            defend_year: int,
            defend_period: str,
            location_uuid: str,
            person: Person
    ) -> None:
        with osis_dissertation_sdk.ApiClient(cls.CONFIGURATION) as api_client:
            api_instance = dissertation_api.DissertationApi(api_client)
            cmd = DissertationUpdateCommand(
                title=title,
                description=description,
                defend_year=defend_year,
                defend_period=DefendPeriodEnum(str(defend_period)),
                location_uuid=location_uuid,
            )
            api_instance.dissertation_update(
                uuid=uuid,
                dissertation_update_command=cmd,
                **build_mandatory_auth_headers(person),
            )

    @classmethod
    def search(cls, term: str, person: Person) -> str:
        with osis_dissertation_sdk.ApiClient(cls.CONFIGURATION) as api_client:
            api_instance = dissertation_api.DissertationApi(api_client)
            response = api_instance.dissertation_list(
                limit=100,
                offset=0,
                search=term,
                **build_mandatory_auth_headers(person),
            )
            return getattr(response, 'results', [])

    @classmethod
    def get(cls, uuid: str, person: Person):
        with osis_dissertation_sdk.ApiClient(cls.CONFIGURATION) as api_client:
            api_instance = dissertation_api.DissertationApi(api_client)
            return api_instance.dissertation_detail(
                uuid=uuid,
                **build_mandatory_auth_headers(person),
            )

    @classmethod
    def deactivate(cls, uuid: str, person: Person):
        with osis_dissertation_sdk.ApiClient(cls.CONFIGURATION) as api_client:
            api_instance = dissertation_api.DissertationApi(api_client)
            api_instance.dissertation_deactivate(
                uuid=uuid,
                **build_mandatory_auth_headers(person),
            )

    @classmethod
    def submit(cls, uuid: str, justification: str, person: Person):
        with osis_dissertation_sdk.ApiClient(cls.CONFIGURATION) as api_client:
            api_instance = dissertation_api.DissertationApi(api_client)
            cmd = DissertationSubmitCommand(
                justification=justification,
            )
            api_instance.dissertation_submit(
                uuid=uuid,
                dissertation_submit_command=cmd,
                **build_mandatory_auth_headers(person),
            )

    @classmethod
    def back_to_draft(cls, uuid: str, justification: str, person: Person):
        with osis_dissertation_sdk.ApiClient(cls.CONFIGURATION) as api_client:
            api_instance = dissertation_api.DissertationApi(api_client)
            cmd = DissertationBackToDraftCommand(
                justification=justification,
            )
            api_instance.dissertation_back_to_draft(
                uuid=uuid,
                dissertation_back_to_draft_command=cmd,
                **build_mandatory_auth_headers(person),
            )

    @classmethod
    def history(cls, uuid: str, person: Person):
        with osis_dissertation_sdk.ApiClient(cls.CONFIGURATION) as api_client:
            api_instance = dissertation_api.DissertationApi(api_client)
            response = api_instance.dissertation_history(
                uuid=uuid,
                **build_mandatory_auth_headers(person),
            )
            return getattr(response, 'results', [])

    @classmethod
    def delete_jury_member(cls, uuid: str, uuid_jury_member: str, person: Person):
        with osis_dissertation_sdk.ApiClient(cls.CONFIGURATION) as api_client:
            api_instance = dissertation_api.DissertationApi(api_client)
            api_instance.dissertation_deletejurymember(
                uuid=uuid,
                uuid_jury_member=uuid_jury_member,
                **build_mandatory_auth_headers(person),
            )

    @classmethod
    def add_jury_member(cls, uuid: str, adviser_uuid: str, person: Person):
        with osis_dissertation_sdk.ApiClient(cls.CONFIGURATION) as api_client:
            api_instance = dissertation_api.DissertationApi(api_client)
            cmd = DissertationJuryAddCommand(adviser_uuid=adviser_uuid)
            api_instance.dissertation_addjurymember(
                uuid=uuid,
                dissertation_jury_add_command=cmd,
                **build_mandatory_auth_headers(person),
            )

    @classmethod
    def can_manage_jury_member(cls, uuid: str, person: Person):
        with osis_dissertation_sdk.ApiClient(cls.CONFIGURATION) as api_client:
            api_instance = dissertation_api.DissertationApi(api_client)
            response = api_instance.dissertation_can_manage_jury_member(
                uuid=uuid,
                **build_mandatory_auth_headers(person),
            )
            return getattr(response, 'can_manage_jury_members', False)

    @classmethod
    def can_edit_dissertation(cls, uuid: str, person: Person):
        with osis_dissertation_sdk.ApiClient(cls.CONFIGURATION) as api_client:
            api_instance = dissertation_api.DissertationApi(api_client)
            response = api_instance.dissertation_can_edit_dissertation(
                uuid=uuid,
                **build_mandatory_auth_headers(person),
            )
            return getattr(response, 'can_edit_dissertation', False)

    @classmethod
    def update_dissertation_file(cls, person, data, uuid=None):
        with osis_dissertation_sdk.ApiClient(cls.CONFIGURATION) as api_client:
            api_instance = dissertation_api.DissertationApi(api_client)
            return api_instance.update_dissertation_file(
                uuid=str(uuid),
                dissertation_file=data,
                **build_mandatory_auth_headers(person),
            )

    @classmethod
    def retrieve_dissertation_file(cls, person, uuid=None):
        with osis_dissertation_sdk.ApiClient(cls.CONFIGURATION) as api_client:
            api_instance = dissertation_api.DissertationApi(api_client)
            return api_instance.retrieve_dissertation_file(
                uuid=str(uuid),
                **build_mandatory_auth_headers(person),
            )
