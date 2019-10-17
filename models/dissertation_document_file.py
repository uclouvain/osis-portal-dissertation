##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
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


class DissertationDocumentFileAdmin(SerializableModelAdmin):
    list_display = ('dissertation', 'document_file')
    raw_id_fields = ('dissertation', 'document_file')
    search_fields = ('uuid',)


class DissertationDocumentFile(SerializableModel):
    dissertation = models.ForeignKey('Dissertation', on_delete=models.CASCADE)
    document_file = models.ForeignKey('osis_common.documentFile', on_delete=models.CASCADE)

    def __str__(self):
        return u"%s %s" % (self.dissertation if self.dissertation else "",
                           self.document_file if self.document_file else "")


def search(dissertation=None, description=None):
    out = None
    queryset = DissertationDocumentFile.objects.order_by('document_file__creation_date')
    if dissertation:
        queryset = queryset.filter(dissertation=dissertation)
    if description:
        queryset = queryset.filter(document_file__description=description)
    if dissertation or description:
        out = queryset
    return out
