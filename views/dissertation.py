##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2018-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.db.models import Q, Subquery, OuterRef
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView, TemplateView, FormView

import dissertation.models.enums.defend_periodes
import dissertation.models.enums.dissertation_status
from base import models as mdl
from base.models import academic_year, education_group, education_group_year
from base.models.education_group_year import EducationGroupYear
from base.models.enums import offer_enrollment_state
from base.models.offer_enrollment import OfferEnrollment
from base.views import layout
from base.views.mixin import AjaxTemplateMixin
from dissertation.forms import DissertationEditForm, DissertationRoleForm, \
    DissertationTitleForm, DissertationUpdateForm, CreateDissertationForm, UpdateDissertationForm
from dissertation.models import dissertation, dissertation_role, dissertation_update, \
    offer_proposition, proposition_dissertation
from dissertation.models.adviser import Adviser
from dissertation.models.dissertation import Dissertation
from dissertation.models.dissertation_document_file import DissertationDocumentFile
from dissertation.models.dissertation_role import DissertationRole
from dissertation.models.enums import dissertation_status, dissertation_role_status
from dissertation.models.proposition_role import PropositionRole
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
            'can_edit_jury_readers': self.can_edit_jury_readers()
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
        # TODO : periode d'edition offer_pro.start_edit_title <= timezone.now().date() <= offer_pro.end_edit_title
        return str(self.dissertation.status) in [
            dissertation.DissertationStatus.DRAFT.name,
            dissertation.DissertationStatus.DIR_KO.name,
        ]

    def can_edit_jury_readers(self) -> bool:
        # TODO: Implement can edit jury readers offer_pro.student_can_manage_readers,
        return True


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


class DissertationDeleteView(LoginRequiredMixin, View):
    @cached_property
    def person(self):
        return self.request.user.person

    def get(self, *args, **kwargs):
        # TODO Move to POST
        DissertationService.deactivate(self.kwargs['uuid'], self.person)
        return redirect('dissertations')


class DissertationUpdateView(LoginRequiredMixin, FormView):
    # FormView
    template_name = "dissertation_edit_form"

    @cached_property
    def person(self):
        return self.request.user.person

    @cached_property
    def dissertation(self):
        return DissertationService.get(self.kwargs['uuid'], self.person)

    def get_form_class(self):
        return UpdateDissertationForm

    def get_initial(self):
        return {
            'title': self.dissertation.title,
            'description': self.dissertation.description,
            'defend_year': self.dissertation.defend_year,
            'defend_period': self.dissertation.defend_period,
            'location': self.dissertation.location,
        }

    def form_valid(self, form):
        DissertationService.update(
            uuid=self.kwargs['uuid'],
            title=form.cleaned_data['title'],
            description=form.cleaned_data['description'],
            defend_year=form.cleaned_data['defend_year'],
            defend_period=form.cleaned_data['defend_period'],
            location_uuid=form.cleaned_data['location'],
            person=self.person
        )
        return redirect("dissertation_detail", uuid=self.kwargs['uuid'])


@login_required
def dissertation_edit(request, pk):
    dissert = get_object_or_404(Dissertation.objects, pk=pk)
    original_title = dissert.title
    person = mdl.person.find_by_user(request.user)
    student = mdl.student.find_by_person(person)
    if dissert.author_is_logged_student(request):
        education_groups = education_group.find_by_student_and_enrollment_states(
            student, [offer_enrollment_state.SUBSCRIBED, offer_enrollment_state.PROVISORY])
        offer_pro = offer_proposition.get_by_education_group(dissert.education_group_year.education_group)
        if dissert.status == 'DRAFT' or dissert.status == 'DIR_KO':
            return _manage_draft_or_ko_dissertation_form(dissert, education_groups, request)
        else:
            if offer_pro.start_edit_title <= timezone.now().date() <= offer_pro.end_edit_title:
                return _manage_dissertation_form(dissert, original_title, request)
            else:
                return redirect('dissertation_detail', pk=dissert.pk)
    else:
        return redirect('dissertations')


def _manage_dissertation_form(dissert, original_title, request):
    if request.method == "POST":
        form = DissertationTitleForm(request.POST, instance=dissert)
        if form.is_valid() and original_title != form.cleaned_data['title']:
            dissert = form.save()
            dissertation_update.add(request,
                                    dissert,
                                    dissert.status,
                                    justification=build_justification_with_title(dissert, original_title)
                                    )
        return redirect('dissertation_detail', pk=dissert.pk)
    else:
        form = DissertationTitleForm(instance=dissert)
    return layout.render(request, 'dissertation_title_form.html', {'form': form})


def _manage_draft_or_ko_dissertation_form(dissert, education_groups, request):
    if request.method == "POST":
        form = DissertationEditForm(request.POST, instance=dissert)
        if form.is_valid():
            dissert = form.save()
            dissertation_update.add(request, dissert, dissert.status,
                                    justification="student edited the dissertation")
            return redirect('dissertation_detail', pk=dissert.pk)
        else:
            form.fields["education_group_year"].queryset = education_group_year.find_by_education_groups(
                education_groups)
            form.fields[
                "proposition_dissertation"].queryset = proposition_dissertation.find_by_education_groups(
                education_groups)
    else:
        form = DissertationEditForm(instance=dissert)
        form.fields["education_group_year"].queryset = education_group_year.find_by_education_groups(
            education_groups)
        form.fields["proposition_dissertation"].queryset = proposition_dissertation.find_by_education_groups(
            education_groups)
    return layout.render(request, 'dissertation_edit_form.html',
                         {
                             'form': form,
                             'defend_periode_choices': dissertation.DEFEND_PERIODE
                         })


def build_justification_with_title(dissert, titre_original):
    return "student_edit_title: {} : {}, {} : {}".format(
        _("original title"),
        titre_original,
        _("new title"),
        dissert.title
    )


class DissertationJuryNewView(AjaxTemplateMixin, UserPassesTestMixin, CreateView):
    model = DissertationRole
    template_name = 'dissertation_reader_edit_inner.html'
    form_class = DissertationRoleForm
    _dissertation = None
    raise_exception = True

    def test_func(self):
        dissert = self.dissertation
        count_dissertation_role = dissertation_role.count_by_dissertation(dissert)
        count_reader = dissertation_role.count_reader_by_dissertation(dissert)
        offer_pro = offer_proposition.get_by_education_group(dissert.education_group_year.education_group)
        return offer_pro.student_can_manage_readers and count_dissertation_role < 5 and count_reader < 3

    def dispatch(self, request, *args, **kwargs):
        if self.dissertation.author_is_logged_student(request):
            return super().dispatch(request, *args, **kwargs)
        return redirect('dissertations')

    @property
    def dissertation(self):
        if not self._dissertation:
            self._dissertation = get_object_or_404(dissertation.Dissertation, pk=self.kwargs['pk'])
        return self._dissertation

    def get_initial(self):
        return {'status': dissertation_role_status.READER, 'dissertation': self.dissertation}

    def form_invalid(self, form):
        return super().form_invalid(form)

    def form_valid(self, form):
        result = super().form_valid(form)
        justification = "{} {}".format("Student added reader", form.cleaned_data['adviser'])
        dissert = self.dissertation
        dissertation_update.add(self.request, dissert, dissert.status, justification=justification)
        return result

    def get_success_url(self):
        return None


class AdviserAutocomplete(autocomplete.Select2QuerySetView):
    def get_result_label(self, item):
        return "{} {}, {}".format(item.person.last_name, item.person.first_name, item.person.email)

    def get_queryset(self):
        qs = Adviser.objects.all().select_related("person").order_by("person")
        if self.q:
            qs = qs.filter(Q(person__last_name__icontains=self.q) | Q(person__first_name__icontains=self.q))
        return qs


# TODO : Implement check on visibility date according to offerproposition
# offer_propositions = OfferProposition.objects.filter(
#         education_group__in=[
#             offer_enrollment.education_group_year.education_group for offer_enrollment in offer_enrollements
#         ]
#     )
#     date_now = timezone.now().date()
#     if any(o.start_visibility_dissertation <= date_now <= o.end_visibility_dissertation for o in offer_propositions):
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


@login_required
def dissertation_reader_delete(request, pk):
    role = get_object_or_404(dissertation_role.DissertationRole, pk=pk)
    dissert = role.dissertation
    if dissert.author_is_logged_student(request):
        offer_pro = offer_proposition.get_by_education_group(dissert.education_group_year.education_group)
        if offer_pro.student_can_manage_readers and dissert.status == 'DRAFT':
            justification = "Student deleted reader {}".format(role)
            dissertation_update.add(request, dissert, dissert.status, justification=justification)
            role.delete()
        return redirect('dissertation_detail', pk=dissert.pk)
    else:
        return redirect('dissertations')


@login_required
def dissertation_to_dir_submit(request, pk):
    dissert = get_object_or_404(dissertation.Dissertation, pk=pk)
    person = request.user.person
    student = person.student_set.first()
    submitted_memories_count = dissertation.count_disser_submit_by_student_in_educ_group(
        student,
        dissert.education_group_year.education_group)
    if dissert.author_is_logged_student(request) and submitted_memories_count == 0:
        new_status = dissertation.get_next_status(dissert, "go_forward")
        status_dict = dict(dissertation_status.DISSERTATION_STATUS)
        new_status_display = status_dict.get(new_status, dissertation_status.DIR_SUBMIT)

        form = DissertationUpdateForm(
            request.POST or None,
            dissertation=dissert,
            person=person,
            action="go_forward")
        if form.is_valid():
            form.save()
            return redirect('dissertation_detail', pk=pk)

        return layout.render(request, 'dissertation_add_justification.html',
                             {'form': form, 'dissertation': dissert, "new_status_display": new_status_display})
    else:
        return redirect('dissertations')


@login_required
def dissertation_back_to_draft(request, pk):
    dissert = get_object_or_404(dissertation.Dissertation, pk=pk)
    person = request.user.person
    new_status = dissertation.get_next_status(dissert, "go_back")
    status_dict = dict(dissertation_status.DISSERTATION_STATUS)
    new_status_display = status_dict.get(new_status, dissertation_status.DRAFT)
    form = DissertationUpdateForm(
        request.POST or None,
        dissertation=dissert,
        person=person,
        action="go_back")
    if form.is_valid():
        form.save()
        return redirect('dissertation_detail', pk=pk)

    return layout.render(request, 'dissertation_add_justification.html',
                         {'form': form, 'dissertation': dissert, "new_status_display": new_status_display})
