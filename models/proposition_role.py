##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.db import models

from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin
from .enums import dissertation_role_status


class PropositionRoleAdmin(SerializableModelAdmin):
    list_display = ('adviser', 'status', 'proposition_dissertation')
    raw_id_fields = ('adviser', 'proposition_dissertation')
    search_fields = ('uuid', 'proposition_dissertation__author__person__last_name',
                     'proposition_dissertation__author__person__first_name',
                     'proposition_dissertation__title',
                     'adviser__person__last_name',
                     'adviser__person__first_name')


class PropositionRole(SerializableModel):
    status = models.CharField(max_length=12,
                              choices=dissertation_role_status.STATUS_CHOICES,
                              default=dissertation_role_status.PROMOTEUR
                              )
    adviser = models.ForeignKey('Adviser', on_delete=models.PROTECT)
    proposition_dissertation = models.ForeignKey('PropositionDissertation', on_delete=models.CASCADE)

    def __str__(self):
        return u"%s %s" % (self.status if self.status else "",
                           self.adviser if self.adviser else "")


def add(status, adviser, proposition_dissertation):
    count_by_status_adviser_proposition = PropositionRole.objects.filter(
        proposition_dissertation=proposition_dissertation,
        status=status,
        adviser=adviser
    ).exists()
    if not count_by_status_adviser_proposition:
        role = PropositionRole(status=status, adviser=adviser, proposition_dissertation=proposition_dissertation)
        role.save()
