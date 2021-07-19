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
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from base.models.education_group_year import EducationGroupYear
from dissertation.models import dissertation_role
from dissertation.models.dissertation import Dissertation
from dissertation.models.dissertation_location import DissertationLocation
from dissertation.models.dissertation_role import DissertationRole
from dissertation.models.dissertation_update import DissertationUpdate, JUSTIFICATION_LINK
from dissertation.models.enums import defend_periodes


class CreateDissertationForm(forms.Form):
    title = forms.CharField(label=_('Title'))
    description = forms.CharField(label=_('Description'), required=False)
    defend_year = forms.IntegerField(label=_('Defense year'))
    defend_period = forms.ChoiceField(label=_('Defense period'), choices=defend_periodes.DEFEND_PERIODE)
    location = forms.ModelChoiceField(label=_('Dissertation location'), queryset=DissertationLocation.objects.all())
    education_group_year = forms.ModelChoiceField(label=_('Offers'), queryset=EducationGroupYear.objects.all())
    proposition_dissertation = forms.CharField(label=_('Dissertation subject'), disabled=True, required=False)

    def __init__(self, *args, student, proposition_dissertation, **kwargs):
        self.student = student
        super().__init__(*args, **kwargs)

        # TODO: Make a webservice to get enrollment
        self.fields['education_group_year'].queryset = EducationGroupYear.objects.filter(
            offerenrollment__student=student,
            # acronym__in=[offer for offer in proposition_dissertation.offers]
        ).order_by(
            "academic_year__year", "acronym"
        )

    def clean_education_group_year(self) -> str:
        education_group_year_obj = self.cleaned_data['education_group_year']
        return str(education_group_year_obj.uuid)

    def clean_location(self) -> str:
        location_obj = self.cleaned_data['location']
        return str(location_obj.uuid)


class DissertationEditForm(ModelForm):
    class Meta:
        model = Dissertation
        fields = ('title', 'author', 'education_group_year', 'proposition_dissertation', 'description',
                  'defend_year', 'defend_periode', 'location')
        widgets = {
            'author': forms.HiddenInput(),
            'education_group_year': forms.HiddenInput(),
            'proposition_dissertation': forms.HiddenInput()
        }


class DissertationRoleForm(ModelForm):

    def clean(self):
        data = self.cleaned_data
        if dissertation_role.count_by_status_student_dissertation(data['status'],
                                                                  data['adviser'],
                                                                  data['dissertation']):
            raise ValidationError('This reader has already been added')
        return super().clean()

    class Meta:
        model = DissertationRole
        fields = ('dissertation', 'status', 'adviser')
        widgets = {
            'dissertation': forms.HiddenInput(),
            'status': forms.HiddenInput(),
            'adviser': autocomplete.ModelSelect2(url='adviser-autocomplete', )
        }

    class Media:
        css = {
            'all': ('css/select2-bootstrap.css',)
        }


class DissertationTitleForm(ModelForm):
    class Meta:
        model = Dissertation
        fields = ('title',)


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
