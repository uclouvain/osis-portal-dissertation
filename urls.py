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

from django.urls import path, include

from dissertation.views import common
from dissertation.views.dissertation import AdviserAutocomplete, DissertationCreateView, DissertationListView, \
    DissertationDeleteView, DissertationDetailView, DissertationHistoryView, \
    DissertationUpdateView, DissertationJuryDeleteView, DissertationJuryAddView, DissertationSubmitView, \
    DissertationBackToDraftView
from dissertation.views.proposition_dissertation import PropositionDissertationListView, \
    PropositionDissertationDetailView

urlpatterns = [
    path('', common.home, name='dissertation'),

    path('dissertations/', include(([
        path('', DissertationListView.as_view(), name='dissertations'),
        path('<str:uuid>/', DissertationDetailView.as_view(), name='dissertation_detail'),
        path('<str:uuid>/history', DissertationHistoryView.as_view(), name='dissertation_history'),
        path('<str:uuid>/delete', DissertationDeleteView.as_view(), name='dissertation_delete'),
        path('<str:uuid>/update', DissertationUpdateView.as_view(), name='dissertation_edit'),
        path('<str:uuid>/submit', DissertationSubmitView.as_view(), name='dissertation_to_dir_submit'),
        path('<str:uuid>/back_to_draft', DissertationBackToDraftView.as_view(), name='dissertation_back_to_draft'),
        path('<str:uuid>/jury/', DissertationJuryAddView.as_view(), name='add_reader'),
        path(
            '<str:uuid>/jury/<str:uuid_jury_member>/delete',
            DissertationJuryDeleteView.as_view(),
            name='dissertation_jury_delete',
        ),
    ]))),

    path('adviser-autocomplete/', AdviserAutocomplete.as_view(),
        name='adviser-autocomplete'),
    path('proposition_dissertations/', include(([
        path('', PropositionDissertationListView.as_view(), name='proposition_dissertations'),
        path('<str:uuid>/', PropositionDissertationDetailView.as_view(), name='proposition_dissertation_detail'),

        path('<str:uuid>/create_dissertation', DissertationCreateView.as_view(), name='dissertation_new')
    ]))),
]
