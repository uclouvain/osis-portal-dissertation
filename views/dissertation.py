##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2018-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.utils.functional import cached_property
from django.views import View
from django.views.generic import TemplateView, FormView

import dissertation.models.enums.defend_periodes
import dissertation.models.enums.dissertation_status
from base.views.mixin import AjaxTemplateMixin
from dissertation.forms import CreateDissertationForm, UpdateDissertationForm, \
    UpdateDissertationTitleForm, DissertationJuryAddForm, DissertationJustificationForm
from dissertation.models import dissertation, proposition_dissertation
from dissertation.models.adviser import Adviser
from dissertation.models.enums import dissertation_status, dissertation_role_status
from dissertation.services.dissertation import DissertationService
from dissertation.services.proposition_dissertation import PropositionDissertationService


class DissertationListView(LoginRequiredMixin, TemplateView):
    # TemplateView
    template_name = "dissertations_list.html"

    @cached_property
    def person(self):
        return self.request.user.person

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(),
            'dissertations': self.get_dissertations(),
        }

    def get_dissertations(self):
        search_term = self.request.GET.get('search', '')
        return DissertationService.search(search_term, self.person)


class DissertationDetailView(LoginRequiredMixin, TemplateView):
    # TemplateView
    template_name = "dissertation_detail.html"

    @cached_property
    def person(self):
        return self.request.user.person

    @cached_property
    def dissertation(self):
        return DissertationService.get(self.kwargs['uuid'], self.person)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(),
            'dissertation': self.dissertation,
            'proposition_dissertation': self.get_proposition_dissertation(),
            'can_delete_dissertation': self.can_delete_dissertation(),
            'can_edit_dissertation': self.can_edit_dissertation(),
            'can_delete_jury_readers': self.can_delete_jury_readers(),
            'can_add_jury_readers': self.can_add_jury_readers(),
            'have_already_submitted_a_dissertation': False
        }

    def get_proposition_dissertation(self):
        proposition_dissertation_uuid = self.dissertation['proposition_uuid']
        return PropositionDissertationService.get(proposition_dissertation_uuid, self.person)

    def can_delete_dissertation(self) -> bool:
        return str(self.dissertation.status) in [
            dissertation.DissertationStatus.DRAFT.name,
            dissertation.DissertationStatus.DIR_KO.name,
        ]

    def can_edit_dissertation(self) -> bool:
        return str(self.dissertation.status) in [
            dissertation.DissertationStatus.DRAFT.name,
            dissertation.DissertationStatus.DIR_KO.name,
        ] and DissertationService.can_edit_dissertation(self.kwargs['uuid'], self.person)

    def can_delete_jury_readers(self) -> bool:
        return DissertationService.can_manage_jury_member(self.kwargs['uuid'], self.person)

    def can_add_jury_readers(self) -> bool:
        all_jury_readers_members = [
            jury_member for jury_member in self.dissertation.jury
            if jury_member.status.value == dissertation_role_status.READER
        ]
        return len(self.dissertation.jury) < 4 and len(all_jury_readers_members) < 2 \
            and DissertationService.can_manage_jury_member(self.kwargs['uuid'], self.person)


class DissertationCreateView(LoginRequiredMixin, FormView):
    # FormView
    form_class = CreateDissertationForm
    template_name = "dissertation_form.html"

    @cached_property
    def person(self):
        return self.request.user.person

    @cached_property
    def student(self):
        return self.person.student_set.first()

    @cached_property
    def proposition_dissertation(self):
        return PropositionDissertationService.get(self.kwargs['uuid'], self.person)

    def form_valid(self, form):
        uuid_dissertation = DissertationService.create(
            proposition_dissertation_uuid=self.kwargs['uuid'],
            title=form.cleaned_data['title'],
            description=form.cleaned_data['description'],
            defend_year=form.cleaned_data['defend_year'],
            defend_period=form.cleaned_data['defend_period'],
            location_uuid=form.cleaned_data['location'],
            education_group_year_uuid=form.cleaned_data['education_group_year'],
            person=self.person
        )
        return redirect("dissertation_detail", uuid=uuid_dissertation)

    def get_form_kwargs(self):
        return {
            **super().get_form_kwargs(),
            'student': self.student,
            'proposition_dissertation': self.proposition_dissertation
        }

    def get_initial(self):
        proposition_dissertation_str = "%s %s %s - %s" % (
            self.proposition_dissertation.author.last_name.upper(),
            self.proposition_dissertation.author.first_name,
            self.proposition_dissertation.author.middle_name,
            self.proposition_dissertation.title
        )

        return {
            'proposition_dissertation': proposition_dissertation_str
        }

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'proposition_dissertation': proposition_dissertation
        }


class DissertationHistoryView(LoginRequiredMixin, TemplateView):
    # TemplateView
    template_name = "dissertation_history.html"

    @cached_property
    def person(self):
        return self.request.user.person

    @cached_property
    def dissertation(self):
        return DissertationService.get(self.kwargs['uuid'], self.person)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(),
            'dissertation': self.dissertation,
            'dissertation_history': self.get_dissertation_history()
        }

    def get_dissertation_history(self):
        return DissertationService.history(self.kwargs['uuid'], self.person)


# TODO: Implement access view if offer_pro.start_edit_title <= timezone.now().date() <= offer_pro.end_edit_title
class DissertationUpdateView(LoginRequiredMixin, FormView):
    @cached_property
    def person(self):
        return self.request.user.person

    @cached_property
    def dissertation(self):
        return DissertationService.get(self.kwargs['uuid'], self.person)

    def get_form_class(self):
        return UpdateDissertationForm if self._can_edit_all_form() else UpdateDissertationTitleForm

    def get_template_names(self):
        return ["dissertation_edit_form.html"] if self._can_edit_all_form() else ["dissertation_title_form.html"]

    def get_initial(self):
        return {
            'title': self.dissertation.title,
            'description': self.dissertation.description,
            'defend_year': self.dissertation.defend_year,
            'defend_period': self.dissertation.defend_period,
            'location': self.dissertation.location.uuid,
        }

    def form_valid(self, form):
        update_kwargs = {
            'uuid': self.kwargs['uuid'],
            'title': form.cleaned_data['title'],
        }
        if self._can_edit_all_form():
            update_kwargs.update(
                description=form.cleaned_data['description'],
                defend_year=form.cleaned_data['defend_year'],
                defend_period=form.cleaned_data['defend_period'],
                location_uuid=form.cleaned_data['location'],
            )
        else:
            update_kwargs.update(
                description=self.dissertation.description,
                defend_year=self.dissertation.defend_year,
                defend_period=self.dissertation.defend_period,
                location_uuid=self.dissertation.location.uuid,
            )

        DissertationService.update(**update_kwargs, person=self.person)
        return redirect("dissertation_detail", uuid=self.kwargs['uuid'])

    def _can_edit_all_form(self) -> bool:
        return self.dissertation.status.value in [
            dissertation.DissertationStatus.DRAFT.name,
            dissertation.DissertationStatus.DIR_KO.name,
        ]


class DissertationDeleteView(LoginRequiredMixin, View):
    @cached_property
    def person(self):
        return self.request.user.person

    def get(self, *args, **kwargs):
        # TODO Move to POST
        DissertationService.deactivate(self.kwargs['uuid'], self.person)
        return redirect('dissertations')


class DissertationJuryAddView(AjaxTemplateMixin, FormView):
    # FormView
    template_name = 'dissertation_reader_edit_inner.html'
    form_class = DissertationJuryAddForm

    @cached_property
    def person(self):
        return self.request.user.person

    def form_valid(self, form):
        DissertationService.add_jury_member(
            uuid=self.kwargs['uuid'],
            adviser_uuid=form.cleaned_data['adviser'],
            person=self.person
        )
        return redirect("dissertation_detail", uuid=self.kwargs['uuid'])


class AdviserAutocomplete(autocomplete.Select2QuerySetView):
    def get_result_label(self, adviser: Adviser):
        return "{} {}, {}".format(adviser.person.last_name, adviser.person.first_name, adviser.person.email)

    def get_result_value(self, adviser: Adviser):
        return adviser.uuid

    def get_queryset(self):
        qs = Adviser.objects.all().select_related("person").order_by("person")
        if self.q:
            qs = qs.filter(Q(person__last_name__icontains=self.q) | Q(person__first_name__icontains=self.q))
        return qs


class DissertationJuryDeleteView(LoginRequiredMixin, View):
    @cached_property
    def person(self):
        return self.request.user.person

    def get(self, *args, **kwargs):
        # TODO Move to POST
        DissertationService.delete_jury_member(
            uuid=self.kwargs['uuid'],
            uuid_jury_member=self.kwargs['uuid_jury_member'],
            person=self.person,
        )
        return redirect('dissertation_detail', uuid=self.kwargs['uuid'])


class DissertationSubmitView(LoginRequiredMixin, FormView):
    # FormView
    template_name = 'dissertation_add_justification.html'
    form_class = DissertationJustificationForm

    @cached_property
    def person(self):
        return self.request.user.person

    @cached_property
    def dissertation(self):
        return DissertationService.get(self.kwargs['uuid'], self.person)

    def form_valid(self, form):
        DissertationService.submit(
            uuid=self.kwargs['uuid'],
            justification=form.cleaned_data['justification'],
            person=self.person
        )
        return redirect("dissertation_detail", uuid=self.kwargs['uuid'])

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'new_status_display': dict(dissertation_status.DISSERTATION_STATUS).get(dissertation_status.DIR_SUBMIT),
            'dissertation': self.dissertation
        }


class DissertationBackToDraftView(LoginRequiredMixin, FormView):
    # FormView
    template_name = 'dissertation_add_justification.html'
    form_class = DissertationJustificationForm

    @cached_property
    def person(self):
        return self.request.user.person

    @cached_property
    def dissertation(self):
        return DissertationService.get(self.kwargs['uuid'], self.person)

    def form_valid(self, form):
        DissertationService.back_to_draft(
            uuid=self.kwargs['uuid'],
            justification=form.cleaned_data['justification'],
            person=self.person
        )
        return redirect("dissertation_detail", uuid=self.kwargs['uuid'])

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'new_status_display': dict(dissertation_status.DISSERTATION_STATUS).get(dissertation_status.DRAFT),
            'dissertation': self.dissertation
        }
