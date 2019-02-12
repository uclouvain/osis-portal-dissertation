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
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from base import models as mdl
from base.models import student, offer_year, academic_year
from dissertation.models import dissertation_location, proposition_dissertation
from dissertation.models.enums.dissertation_status import DISSERTATION_STATUS
from dissertation.utils import emails_dissert
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class DissertationAdmin(SerializableModelAdmin):
    list_display = ('uuid', 'title', 'author', 'status', 'active', 'proposition_dissertation', 'modification_date',
                    'education_group_year_start')
    raw_id_fields = ('author', 'offer_year_start', 'proposition_dissertation', 'location', 'education_group_year_start')
    search_fields = ('uuid', 'title', 'author__person__last_name', 'author__person__first_name',
                     'proposition_dissertation__title', 'proposition_dissertation__author__person__last_name',
                     'proposition_dissertation__author__person__first_name', 'education_group_year_start__id')


DEFEND_PERIODE_CHOICES = (
    ('UNDEFINED', _('undefined')),
    ('JANUARY', _('January')),
    ('JUNE', _('June')),
    ('SEPTEMBER', _('September')),
)


class Dissertation(SerializableModel):
    title = models.CharField(_('Dissertation'), max_length=500)
    author = models.ForeignKey(student.Student)
    status = models.CharField(max_length=12, choices=DISSERTATION_STATUS, default='DRAFT')
    defend_periode = models.CharField(_('Defend period'), max_length=12, choices=DEFEND_PERIODE_CHOICES,
                                      default='UNDEFINED', null=True)
    defend_year = models.IntegerField(_('Defend year'), blank=True, null=True)
    offer_year_start = models.ForeignKey(offer_year.OfferYear, null=True, blank=True)
    education_group_year_start = models.ForeignKey('base.EducationGroupYear',
                                                   null=True,
                                                   blank=True,
                                                   on_delete=models.PROTECT,
                                                   related_name='dissertations', verbose_name=_('Offers'))
    proposition_dissertation = models.ForeignKey(proposition_dissertation.PropositionDissertation,
                                                 verbose_name=_('Dissertation subject'))
    description = models.TextField(_('Description'), blank=True, null=True)
    active = models.BooleanField(default=True)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False)
    modification_date = models.DateTimeField(auto_now=True)
    location = models.ForeignKey(dissertation_location.DissertationLocation, blank=True, null=True,
                                 verbose_name=_('Dissertation location'))

    def __str__(self):
        return self.title

    def deactivate(self):
        self.active = False
        self.save()

    def set_status(self, status):
        self.status = status
        self.save()

    def go_forward(self):
        next_status = get_next_status(self, "go_forward")
        if self.status == 'DRAFT' and next_status == 'DIR_SUBMIT':
            emails_dissert.send_email_to_all_promotors(self, 'dissertation_adviser_new_project_dissertation')
        self.set_status(next_status)

    def go_back(self):
        next_status = get_next_status(self, "go_back")
        if self.status == 'DIR_SUBMIT' and next_status == 'DRAFT':
            emails_dissert.send_email_to_all_promotors(self, 'dissertation_back_to_draft')
            self.set_status(next_status)

    def accept(self):
        next_status = get_next_status(self, "accept")
        self.set_status(next_status)

    def refuse(self):
        next_status = get_next_status(self, "refuse")
        self.set_status(next_status)

    def author_is_logged_student(self, request):
        logged_person = mdl.person.find_by_user(request.user)
        logged_student = mdl.student.find_by_person(logged_person)
        return logged_student == self.author


def count_disser_submit_by_student_in_educ_group(student, educ_group):
    return Dissertation.objects.filter(author=student) \
        .filter(education_group_year_start__education_group=educ_group) \
        .exclude(status='DIR_KO') \
        .exclude(status='DRAFT') \
        .filter(active=True) \
        .count()


def get_next_status(memory, operation):
    if operation == "go_forward":
        if memory.status == 'DRAFT' or memory.status == 'DIR_KO':
            return 'DIR_SUBMIT'
        else:
            return memory.status
    elif operation == "go_back":
        if memory.status == 'DIR_SUBMIT':
            return 'DRAFT'
        else:
            return memory.status
    else:
        return memory.status


def search(terms, author=None):
    queryset = Dissertation.objects.all()
    if terms:
        queryset = queryset.filter(
            Q(title__icontains=terms) |
            Q(description__icontains=terms)
        )
    queryset = queryset.filter(author=author)
    queryset = queryset.distinct()
    return queryset


def find_by_user(user):
    return Dissertation.objects.filter(author=user).exclude(active=False)


def find_by_id(dissertation_id):
    return Dissertation.objects.get(pk=dissertation_id)


def count_by_proposition(proposition):
    current_academic_year = academic_year.starting_academic_year()
    return Dissertation.objects.filter(proposition_dissertation=proposition) \
        .filter(active=True) \
        .filter(education_group_year_start__academic_year=current_academic_year) \
        .exclude(status='DRAFT') \
        .exclude(status='DIR_KO') \
        .count()
