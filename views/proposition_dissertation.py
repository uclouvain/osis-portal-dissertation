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
from django.shortcuts import get_object_or_404
from base import models as mdl
from base.models import education_group
from base.models.enums import offer_enrollment_state
from base.views import layout
from dissertation.models import dissertation, proposition_dissertation, proposition_document_file, proposition_role,\
    proposition_offer
from django.utils import timezone


@login_required
def proposition_dissertations(request):
    person = mdl.person.find_by_user(request.user)
    student = mdl.student.find_by_person(person)
    education_groups = education_group.find_by_student_and_enrollment_states(
        student, [offer_enrollment_state.SUBSCRIBED, offer_enrollment_state.PROVISORY])
    proposition_offers = proposition_offer.find_by_education_group_ordered_by_proposition_dissert(education_groups).\
        prefetch_related('proposition_dissertation', 'offer_proposition')
    proposition_offers = [_append_dissertations_count(prop_offer) for prop_offer in proposition_offers]
    date_now = timezone.now().date()
    return layout.render(request, 'proposition_dissertations_list.html',
                         {'date_now': date_now,
                          'proposition_offers': proposition_offers,
                          'student': student})


def _append_dissertations_count(prop_offer):
    prop_offer.proposition_dissertation.dissertations_count = \
        dissertation.count_by_proposition(prop_offer.proposition_dissertation)
    prop_offer.proposition_dissertation.remaining_places = \
        prop_offer.proposition_dissertation.max_number_student - prop_offer.proposition_dissertation.dissertations_count
    return prop_offer


@login_required
def proposition_dissertation_detail(request, pk):
    proposition = proposition_dissertation.find_by_id(pk)
    subject = get_object_or_404(proposition_dissertation.PropositionDissertation, pk=pk)
    offer_propositions = proposition_offer.search_by_proposition_dissertation(subject).\
        prefetch_related('proposition_dissertation', 'offer_proposition')
    person = mdl.person.find_by_user(request.user)
    student = mdl.student.find_by_person(person)
    using = dissertation.count_by_proposition(proposition)
    percent = using * 100 / subject.max_number_student if subject.max_number_student else 0
    count_proposition_role = proposition_role.count_by_proposition(subject)
    files = proposition_document_file.find_by_proposition(subject)
    filename = ""
    for file in files:
        filename = file.document_file.file_name
    if count_proposition_role < 1:
        proposition_role.add('PROMOTEUR', subject.author, subject)
    proposition_roles = proposition_role.search_by_proposition(subject)
    return layout.render(request, 'proposition_dissertation_detail.html',
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
    return layout.render(request, 'proposition_dissertations_list.html',
                         {'date_now': date_now,
                          'proposition_offers': proposition_offers,
                          'student': student})
