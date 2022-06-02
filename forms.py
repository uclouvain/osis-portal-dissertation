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
from dal import autocomplete
from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from dissertation.models.dissertation_update import DissertationUpdate, JUSTIFICATION_LINK
from dissertation.models.enums import defend_periodes
from dissertation.services.dissertation_location import DissertationLocationService
from dissertation.services.offer_enrollment import OfferEnrollmentService, EducationGroupYear

EMPTY_CHOICE = ('', ' - ')


class CreateDissertationForm(forms.Form):
    title = forms.CharField(label=_('Title'))
    description = forms.CharField(label=_('Description'), required=False)
    defend_year = forms.IntegerField(label=_('Defense year'))
    defend_period = forms.ChoiceField(label=_('Defense period'), choices=defend_periodes.DEFEND_PERIODE)
    location = forms.ChoiceField(label=_('Dissertation location'))
    education_group_year = forms.ChoiceField(label=_('Offers'))
    proposition_dissertation = forms.CharField(label=_('Dissertation subject'), disabled=True, required=False)

    def __init__(self, *args, student, proposition_dissertation, **kwargs):
        self.student = student
        super().__init__(*args, **kwargs)

        education_group_years_list = OfferEnrollmentService.get_education_group_years_from_my_enrollments_list(
            self.student.person,
        )
        self.fields['education_group_year'].choices = [
            (
                f"{education_group_year['acronym']} - {education_group_year['year']}",
                f"{education_group_year['acronym']} - {education_group_year['year']}"
            )
            for education_group_year in education_group_years_list
            if education_group_year['acronym'] in proposition_dissertation["offers"]
        ]
        self.fields['education_group_year'].choices.insert(0, EMPTY_CHOICE)

        locations = DissertationLocationService.get_dissertation_locations_list(
            person=self.student.person
        ).results
        self.fields['location'].choices = [
            (location['uuid'], location['name']) for location in locations
        ]
        self.fields['location'].choices.insert(0, EMPTY_CHOICE)

    def clean_education_group_year(self) -> EducationGroupYear:
        self.cleaned_data["year"] = self.cleaned_data['education_group_year'][-4:]
        self.cleaned_data["acronym"] = self.cleaned_data['education_group_year'][:-7]
        return self.cleaned_data['education_group_year']

    def clean_description(self):
        return self.cleaned_data['description'] or ''


class UpdateDissertationForm(forms.Form):
    title = forms.CharField(label=_('Title'))
    description = forms.CharField(
        label=_('Description'),
        required=False,
        widget=forms.Textarea
    )
    defend_year = forms.IntegerField(label=_('Defense year'))
    defend_period = forms.ChoiceField(label=_('Defense period'), choices=defend_periodes.DEFEND_PERIODE)
    location = forms.ChoiceField(label=_('Dissertation location'))

    def __init__(self, person, *args, **kwargs):
        super().__init__(*args, **kwargs)
        locations = DissertationLocationService.get_dissertation_locations_list(
            person=person
        ).results
        self.fields['location'].choices = [(location['uuid'], location['name']) for location in locations]

    def clean_location(self) -> str:
        location_uuid = self.cleaned_data['location']
        return location_uuid

    def clean_description(self):
        return self.cleaned_data['description'] or ''


class UpdateDissertationTitleForm(forms.Form):
    title = forms.CharField(label=_('Title'))


class DissertationJuryAddForm(forms.Form):
    adviser = autocomplete.Select2ListCreateChoiceField(
        widget=autocomplete.ListSelect2(url='adviser-autocomplete'),
        required=True,
        label=_("Reader")
    )

    class Media:
        css = {
            'all': ('css/select2-bootstrap.css',)
        }


class DissertationJustificationForm(forms.Form):
    justification = forms.CharField(required=False, widget=forms.Textarea)

    def clean_justification(self):
        return self.cleaned_data['justification'] or ''


class DissertationUpdateForm(ModelForm):

    def __init__(self, *args, dissertation, person, action, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.dissertation = dissertation
        self.instance.person = person
        self.action = action

    class Meta:
        model = DissertationUpdate
        fields = ('justification',)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.status_from = instance.dissertation.status

        # getattr action execute go_forward or go_back
        getattr(instance.dissertation, self.action)()
        instance.status_to = instance.dissertation.status

        if not instance.justification:
            instance.justification = "%s%s%s" % (instance.person, JUSTIFICATION_LINK, instance.dissertation.status)

        instance.save()
        return instance
