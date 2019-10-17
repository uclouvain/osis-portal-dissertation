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
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q, Subquery, OuterRef
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView

import dissertation.models.enums.defend_periode_choices
import dissertation.models.enums.dissertation_status
from base import models as mdl
from base.models import academic_year, education_group, education_group_year
from base.models.education_group_year import EducationGroupYear
from base.models.enums import offer_enrollment_state
from base.models.offer_enrollment import OfferEnrollment
from base.views import layout
from base.views.mixin import AjaxTemplateMixin
from dissertation.forms import DissertationForm, DissertationEditForm, DissertationRoleForm, \
    DissertationTitleForm, DissertationUpdateForm
from dissertation.models import dissertation, dissertation_document_file, dissertation_role, dissertation_update, \
    offer_proposition, proposition_dissertation, proposition_role
from dissertation.models.adviser import Adviser
from dissertation.models.dissertation import Dissertation
from dissertation.models.dissertation_role import DissertationRole
from dissertation.models.enums import dissertation_status, dissertation_role_status
from dissertation.models.offer_proposition import OfferProposition
from dissertation.models.proposition_dissertation import PropositionDissertation

INVISIBLE_JUSTIFICATION_KEYWORDS = ('auto_add_jury',
                                    'Auto add jury',
                                    'manager_add_jury',
                                    'Manager add jury',
                                    'Le manager a ajouté un membre du jury',
                                    'manager_creation_dissertation',
                                    'manager_delete_jury',
                                    'Manager deleted jury',
                                    'manager_edit_dissertation',
                                    'manager has edited the dissertation',
                                    'manager_set_active_false',
                                    'teacher_add_jury',
                                    'Teacher added jury',
                                    'teacher_delete_jury',
                                    'Teacher deleted jury',
                                    'teacher_set_active_false'

                                    )


@login_required
def dissertations(request):
    person = request.user.person
    student = mdl.student.find_by_person(person)
    education_groups = education_group.find_by_student_and_enrollment_states(
        student, [offer_enrollment_state.SUBSCRIBED, offer_enrollment_state.PROVISORY])
    offer_propositions = offer_proposition.search_by_education_groups(education_groups)
    dissert = Dissertation.objects.filter(author=student).exclude(active=False). \
        select_related('author__person',
                       'proposition_dissertation',
                       'proposition_dissertation__author__person',
                       'author',
                       'education_group_year_start',
                       'education_group_year_start__academic_year')
    date_now = timezone.now().date()
    visibility = False
    for offer_pro in offer_propositions:
        if offer_pro.start_visibility_dissertation <= date_now <= offer_pro.end_visibility_dissertation:
            visibility = True
    return render(request, 'dissertations_list.html', {
        'date_now': date_now,
        'dissertations': dissert,
        'student': student,
        'visibility': visibility
    })


@login_required
def dissertation_delete(request, pk):
    memory = get_object_or_404(dissertation.Dissertation, pk=pk)
    if memory.author_is_logged_student(request):
        memory.deactivate()
        dissertation_update.add(request, memory, memory.status, justification="Student set dissertation inactive")
    return redirect('dissertations')


@login_required
def dissertation_detail(request, pk):
    person = request.user.person
    student = mdl.student.find_by_person(person)
    current_ac_year = academic_year.current_academic_year()
    dissert = get_object_or_404(Dissertation.objects.
                                select_related('author', 'author__person',
                                               'proposition_dissertation__author__person', 'location').
                                prefetch_related('dissertationrole_set', 'dissertationrole_set__adviser__person',
                                                 'proposition_dissertation__offer_propositions'),
                                pk=pk)
    if dissert.author_is_logged_student(request):
        student_offer_enrollments = OfferEnrollment.objects.filter(
            student=student,
            education_group_year__academic_year=current_ac_year,
            enrollment_state__in=[
                offer_enrollment_state.SUBSCRIBED,
                offer_enrollment_state.PROVISORY
            ]
        ).values_list('id', flat=True)
        educ_group = dissert.education_group_year_start.education_group
        offer_pro = offer_proposition.get_by_education_group(educ_group)
        offer_propositions = dissert.proposition_dissertation.offer_propositions.filter(
            education_group__educationgroupyear__offerenrollment__id__in=student_offer_enrollments
        ).annotate(
            last_acronym=Subquery(
                EducationGroupYear.objects.filter(
                    education_group__offer_proposition=OuterRef('pk'),
                    academic_year=current_ac_year).values('acronym')[:1]
            )
        )
        count = dissertation.count_disser_submit_by_student_in_educ_group(student, educ_group)

        files = dissertation_document_file.find_by_dissertation(dissert)
        filename = ""
        for file in files:
            filename = file.document_file.file_name

        count_dissertation_role = dissertation_role.count_by_dissertation(dissert)
        count_reader = dissertation_role.count_reader_by_dissertation(dissert)
        count_proposition_role = proposition_role.count_by_dissertation(dissert)
        proposition_roles = proposition_role.search_by_dissertation(dissert)
        jury_visibility = offer_pro.start_jury_visibility <= timezone.now().date() <= offer_pro.end_jury_visibility
        check_edit = offer_pro.start_edit_title <= timezone.now().date() <= offer_pro.end_edit_title

        if count_dissertation_role == 0:
            if count_proposition_role == 0:
                dissertation_role.add(dissertation_role_status.PROMOTEUR, dissert.proposition_dissertation.author,
                                      dissert)
            else:
                for role in proposition_roles:
                    dissertation_role.add(role.status, role.adviser, dissert)
        dissertation_roles = dissert.dissertationrole_set.all()
        return render(request, 'dissertation_detail.html',
                      {
                          'check_edit': check_edit,
                          'count': count,
                          'count_reader': count_reader,
                          'count_dissertation_role': count_dissertation_role,
                          'dissertation': dissert,
                          'dissertation_roles': dissertation_roles,
                          'jury_visibility': jury_visibility,
                          'manage_readers': offer_pro.student_can_manage_readers,
                          'filename': filename,
                          'offer_propositions': offer_propositions
                      })
    else:
        return redirect('dissertations')


@login_required
def dissertation_edit(request, pk):
    dissert = get_object_or_404(Dissertation.objects, pk=pk)
    original_title = dissert.title
    person = mdl.person.find_by_user(request.user)
    student = mdl.student.find_by_person(person)
    if dissert.author_is_logged_student(request):
        education_groups = education_group.find_by_student_and_enrollment_states(
            student, [offer_enrollment_state.SUBSCRIBED, offer_enrollment_state.PROVISORY])
        offer_pro = offer_proposition.get_by_education_group(dissert.education_group_year_start.education_group)
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
            form.fields["education_group_year_start"].queryset = education_group_year.find_by_education_groups(
                education_groups)
            form.fields[
                "proposition_dissertation"].queryset = proposition_dissertation.find_by_education_groups(
                education_groups)
    else:
        form = DissertationEditForm(instance=dissert)
        form.fields["education_group_year_start"].queryset = education_group_year.find_by_education_groups(
            education_groups)
        form.fields["proposition_dissertation"].queryset = proposition_dissertation.find_by_education_groups(
            education_groups)
    return layout.render(request, 'dissertation_edit_form.html',
                         {
                             'form': form,
                             'defend_periode_choices': dissertation.DEFEND_PERIODE_CHOICES
                         })


def build_justification_with_title(dissert, titre_original):
    return "student_edit_title: {} : {}, {} : {}".format(
        _("original title"),
        titre_original,
        _("new title"),
        dissert.title
    )


@login_required
def dissertation_history(request, pk):
    dissert = get_object_or_404(Dissertation.objects.select_related('author', )
                                .prefetch_related('dissertation_updates', 'dissertation_updates__person'), pk=pk)
    if dissert.author_is_logged_student(request):
        dissertation_updates = dissert.dissertation_updates.all().prefetch_related('person')
        for keyword in INVISIBLE_JUSTIFICATION_KEYWORDS:
            dissertation_updates = dissertation_updates.exclude(justification__contains=keyword)
        return render(request, 'dissertation_history.html',
                      {
                          'dissertation': dissert,
                          'dissertation_updates': dissertation_updates
                      })
    else:
        return redirect('dissertations')


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
        offer_pro = offer_proposition.get_by_education_group(dissert.education_group_year_start.education_group)
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


@login_required
def dissertation_new(request, pk):
    person = request.user.person
    student = person.student_set.first()
    this_academic_year = academic_year.current_academic_year()
    offer_enrollements = OfferEnrollment.objects.filter(
        student=student,
        education_group_year__academic_year=this_academic_year,
        enrollment_state__in=[
            offer_enrollment_state.SUBSCRIBED,
            offer_enrollment_state.PROVISORY
        ]).select_related('education_group_year', 'education_group_year__education_group')
    offer_propositions = OfferProposition.objects.filter(
        education_group__in=[
            offer_enrollment.education_group_year.education_group for offer_enrollment in offer_enrollements
        ]
    )
    date_now = timezone.now().date()
    if any(o.start_visibility_dissertation <= date_now <= o.end_visibility_dissertation for o in offer_propositions):
        initial = {
            'active': True,
            'author': student
        }
        if pk:
            prop_diss = get_object_or_404(PropositionDissertation, pk=pk)
            initial['proposition_dissertation'] = prop_diss.pk
        form = DissertationForm(request.POST or None, initial=initial)
        if form.is_valid():
            memory = form.save()
            dissertation_update.add(request, memory,
                                    memory.status,
                                    justification="Student created the dissertation : {}".format(memory.title)
                                    )
            return redirect('dissertation_detail', pk=memory.pk)

        form.fields["education_group_year_start"].queryset = EducationGroupYear.objects.filter(
            offerenrollment__student=student,
            education_group__in=[offer_prop.education_group for offer_prop in offer_propositions]
        ).order_by(
            "academic_year__year", "acronym"
        )

        form.fields["proposition_dissertation"].queryset = \
            proposition_dissertation.find_by_education_groups(
                [offer_enroll.education_group_year.education_group for offer_enroll in offer_enrollements]
            )
        return render(request, 'dissertation_form.html',
                      {
                          'form': form,
                          'defend_periode_choices': dissertation.DEFEND_PERIODE_CHOICES
                      })
    else:
        return redirect('dissertations')


@login_required
def dissertation_reader_delete(request, pk):
    role = get_object_or_404(dissertation_role.DissertationRole, pk=pk)
    dissert = role.dissertation
    if dissert.author_is_logged_student(request):
        offer_pro = offer_proposition.get_by_education_group(dissert.education_group_year_start.education_group)
        if offer_pro.student_can_manage_readers and dissert.status == 'DRAFT':
            justification = "Student deleted reader {}".format(role)
            dissertation_update.add(request, dissert, dissert.status, justification=justification)
            role.delete()
        return redirect('dissertation_detail', pk=dissert.pk)
    else:
        return redirect('dissertations')


@login_required
def dissertations_search(request):
    person = mdl.person.find_by_user(request.user)
    student = mdl.student.find_by_person(person)
    memories = dissertation.search(terms=request.GET['search'], author=student)
    return layout.render(request, "dissertations_list.html",
                         {
                             'student': student,
                             'dissertations': memories
                         })


@login_required
def dissertation_to_dir_submit(request, pk):
    dissert = get_object_or_404(dissertation.Dissertation, pk=pk)
    person = request.user.person
    student = person.student_set.first()
    submitted_memories_count = dissertation.count_disser_submit_by_student_in_educ_group(
        student,
        dissert.education_group_year_start.education_group)
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
