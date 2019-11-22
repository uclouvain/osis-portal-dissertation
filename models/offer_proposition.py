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
from django.utils import timezone

from base.models import offer
from dissertation.models.offer_proposition_group import OfferPropositionGroup
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class OfferPropositionAdmin(SerializableModelAdmin):
    list_display = ('acronym', 'offer',
                    'recent_acronym_education_group')
    raw_id_fields = ('offer', 'education_group')
    search_fields = ('uuid', 'acronym', 'offer_id', 'education_group_id',)


class OfferProposition(SerializableModel):
    acronym = models.CharField(max_length=200)
    offer = models.ForeignKey(offer.Offer, on_delete=models.CASCADE)
    education_group = models.OneToOneField('base.EducationGroup',
                                           null=True,
                                           blank=True,
                                           on_delete=models.PROTECT,
                                           related_name='offer_proposition')
    student_can_manage_readers = models.BooleanField(default=True)
    adviser_can_suggest_reader = models.BooleanField(default=False)
    evaluation_first_year = models.BooleanField(default=False)
    validation_commission_exists = models.BooleanField(default=False)
    start_visibility_proposition = models.DateField(default=timezone.now)
    end_visibility_proposition = models.DateField(default=timezone.now)
    start_visibility_dissertation = models.DateField(default=timezone.now)
    end_visibility_dissertation = models.DateField(default=timezone.now)
    start_jury_visibility = models.DateField(default=timezone.now)
    end_jury_visibility = models.DateField(default=timezone.now)
    start_edit_title = models.DateField(default=timezone.now)
    end_edit_title = models.DateField(default=timezone.now)
    offer_proposition_group = models.ForeignKey(OfferPropositionGroup, null=True, blank=True, on_delete=models.CASCADE)
    global_email_to_commission = models.BooleanField(default=False)

    @property
    def recent_acronym_education_group(self):
        if self.education_group:
            return self.education_group.most_recent_acronym
        return None

    def __str__(self):
        return str(self.recent_acronym_education_group)


def get_by_education_group(educ_group):
    return OfferProposition.objects.get(education_group=educ_group)


def search_by_education_groups(education_groups):
    return OfferProposition.objects.filter(education_group__in=education_groups)
