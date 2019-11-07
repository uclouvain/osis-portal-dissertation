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

from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Sum, Case, When, Q, F, ExpressionWrapper, OuterRef, Subquery, Prefetch
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from base import models as mdl
from base.models import education_group, academic_year
from base.models.education_group_year import EducationGroupYear
from base.models.enums import offer_enrollment_state
from base.models.offer_enrollment import OfferEnrollment
from dissertation.models import dissertation, proposition_role, \
    proposition_offer
from dissertation.models.offer_proposition import OfferProposition
from dissertation.models.proposition_dissertation import PropositionDissertation
from dissertation.models.proposition_document_file import PropositionDocumentFile
from dissertation.models.proposition_role import PropositionRole


@login_required
def proposition_dissertations(request):
    person = mdl.person.find_by_user(request.user)
    student = mdl.student.find_by_person(person)
    starting_academic_year = academic_year.starting_academic_year()

    student_offer_enrollments = OfferEnrollment.objects.filter(
            student=student,
            education_group_year__academic_year=starting_academic_year,
            enrollment_state__in=[
                offer_enrollment_state.SUBSCRIBED,
                offer_enrollment_state.PROVISORY
            ]
        ).values_list('id', flat=True)
    student_offer_propositions_id_list = OfferProposition.objects.filter(
        education_group__educationgroupyear__offerenrollment__id__in=student_offer_enrollments
    ).values_list('id', flat=True)
    prefetch_propositions = Prefetch(
        "offer_propositions",
        queryset=OfferProposition.objects.annotate(last_acronym=Subquery(
            EducationGroupYear.objects.filter(
                education_group__offer_proposition=OuterRef('pk'),
                academic_year=starting_academic_year).values('acronym')[:1]
        )).distinct()
    )
    propositions_dissertations = PropositionDissertation.objects.filter(
        active=True,
        visibility=True,
        offer_propositions__education_group__educationgroupyear__offerenrollment__in=student_offer_enrollments
    ).select_related('author__person', 'creator').prefetch_related(prefetch_propositions).annotate(
        dissertations_count=Sum(
            Case(
                When(
                    Q(
                        Q(dissertations__active=True,
                          dissertations__education_group_year_start__academic_year=
                          starting_academic_year),
                        ~Q(dissertations__status__in=('DRAFT', 'DIR_KO'))
                    ), then=1
                ), default=0, output_field=models.IntegerField()
            )
        )
    ).annotate(
        remaining_places=ExpressionWrapper(
            F('max_number_student') - F('dissertations_count'),
            output_field=models.IntegerField()
        )
    ).prefetch_related('dissertations', 'offer_propositions')
    date_now = timezone.now().date()
    return render(request, 'proposition_dissertations_list.html',
                  {'date_now': date_now,
                   'propositions_dissertations': propositions_dissertations,
                   'student': student,
                   'student_offer_propositions_id_list': student_offer_propositions_id_list})


@login_required
def proposition_dissertation_detail(request, pk):
    person = mdl.person.find_by_user(request.user)
    starting_academic_year = academic_year.starting_academic_year()
    subject = get_object_or_404(PropositionDissertation.objects.select_related('author', 'author__person').
                                prefetch_related('propositionrole_set',
                                                 'propositionrole_set__adviser__person',
                                                 'offer_propositions'), pk=pk)
    offer_propositions = subject.offer_propositions.all().annotate(last_acronym=Subquery(
            EducationGroupYear.objects.filter(
                education_group__offer_proposition=OuterRef('pk'),
                academic_year=starting_academic_year).values('acronym')[:1]
        ))

    student = mdl.student.find_by_person(person)
    using = dissertation.count_by_proposition(subject)
    percent = using * 100 / subject.max_number_student if subject.max_number_student else 0
    count_proposition_role = PropositionRole.objects.filter(proposition_dissertation=subject).count()
    files = PropositionDocumentFile.objects.filter(proposition=subject)
    filename = ""
    for file in files:
        filename = file.document_file.file_name
    if count_proposition_role < 1:
        proposition_role.add('PROMOTEUR', subject.author, subject)
    proposition_roles = subject.propositionrole_set.all()
    return render(request, 'proposition_dissertation_detail.html',
                  {'percent': round(percent, 2),
                   'proposition_roles': proposition_roles,
                   'proposition_dissertation': subject,
                   'offer_propositions': offer_propositions,
                   'student': student,
                   'using': using,
                   'filename': filename})


@login_required
def proposition_dissertations_search(request):
    person = mdl.person.find_by_user(request.user)
    student = mdl.student.find_by_person(person)
    education_groups = education_group.find_by_student_and_enrollment_states(
        student,
        [offer_enrollment_state.SUBSCRIBED, offer_enrollment_state.PROVISORY])
    proposition_offers = proposition_offer.search(
        education_groups=education_groups,
        terms=request.GET['search'],
        active=True, visibility=True
    )
    date_now = timezone.now().date()
    return render(request, 'proposition_dissertations_list.html',
                  {'date_now': date_now,
                   'proposition_offers': proposition_offers,
                   'student': student})
