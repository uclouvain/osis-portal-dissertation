##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import factory
import factory.fuzzy
import string
import json
from django.conf import settings
from django.utils import timezone
from base.tests.factories.offer_enrollment import OfferEnrollmentFactory


def _get_tzinfo():
    if settings.USE_TZ:
        return timezone.get_current_timezone()
    else:
        return None


class JSONFactory(factory.DictFactory):
    """
    Use with factory.Dict to make JSON strings.
    """
    @classmethod
    def _generate(cls, create, attrs):
        obj = super()._generate(create, attrs)
        return json.dumps(obj)


class ExamEnrollmentFormFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "exam_enrollment.ExamEnrollmentForm"

    offer_enrollment = factory.SubFactory(OfferEnrollmentFactory)

    form = factory.Dict({
        "acronym": ["L{0}".format(factory.fuzzy.FuzzyText(length=8, chars=string.digits))],
    }, dict_factory=JSONFactory)
