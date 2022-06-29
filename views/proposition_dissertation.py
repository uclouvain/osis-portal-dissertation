##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.functional import cached_property
from django.views.generic import TemplateView

from dissertation.services.proposition_dissertation import PropositionDissertationService


class PropositionDissertationListView(LoginRequiredMixin, TemplateView):
    # TemplateView
    template_name = "proposition_dissertations_list.html"

    @cached_property
    def person(self):
        return self.request.user.person

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(),
            'propositions_dissertations': self.get_propositions_dissertations()
        }

    def get_propositions_dissertations(self):
        return PropositionDissertationService.search('', self.person)


class PropositionDissertationDetailView(LoginRequiredMixin, TemplateView):
    # TemplateView
    template_name = "proposition_dissertation_detail.html"

    @cached_property
    def person(self):
        return self.request.user.person

    @cached_property
    def proposition_dissertation(self):
        return PropositionDissertationService.get(self.kwargs['uuid'], self.person)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(),
            'document': PropositionDissertationService.retrieve_proposition_dissertation_file(
                person=self.person,
                uuid=self.proposition_dissertation.uuid,
            ),
            'proposition_dissertation': self.get_proposition_dissertation()
        }

    def get_proposition_dissertation(self):
        return PropositionDissertationService.get(self.kwargs['uuid'], self.person)
