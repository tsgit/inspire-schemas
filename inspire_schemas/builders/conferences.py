# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE-SCHEMAS.
# Copyright (C) 2019 CERN.
#
# INSPIRE-SCHEMAS is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE-SCHEMAS is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE-SCHEMAS; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Conferences builder class and related code."""
import six

from inspire_schemas.utils import (
    validate, filter_empty_parameters, EMPTIES,
)
from inspire_utils.date import normalize_date


class ConferenceBuilder(object):
    """Conference record builder."""

    def __init__(self, record=None, source=None):
        """Initialize builder with provided source and/or conference record.

        Args:
            record (dict): sets the default value for the the current record,
            in order to edit an already existent record.
            source (string): sets the default value for the source fields of the
            current job record, which captures where the information that the
            builder populates comes from.
        """
        if record is None:
            record = {
                '_collections': ['Conferences'],
            }
        self.record = record
        self.source = source

    def _ensure_field(self, field_name, default_value, obj=None):
        if obj is None:
            obj = self.record
        if field_name not in obj:
            obj.update({field_name: default_value})

    def _ensure_list_field(self, field_name, default_value=None, obj=None):
        if default_value is None:
            default_value = []
        self._ensure_field(field_name, default_value, obj)

    def _ensure_dict_field(self, field_name, default_value=None, obj=None):
        if default_value is None:
            default_value = {}
        self._ensure_field(field_name, default_value, obj)

    def _sourced_dict(self, source=None, **kwargs):
        """Like ``dict(**kwargs)``, but where the ``source`` key is special."""
        if source:
            kwargs['source'] = source
        elif self.source:
            kwargs['source'] = self.source
        return kwargs

    @filter_empty_parameters
    def _append_to(self, field, element=None, default_list=None, **kwargs):
        """Append the ``element`` to the ``field`` of the record.

        This method is ``smart``: it does nothing if ``element`` is empty and
        creates ``field`` if it does not exit yet.

        Args:
            field (string): the name of the field of the record to append to
            element: the element to append
            default_list (list): Default list which should be sert when field is missing

        Kwargs:
            Arguments from which a dictionary will be built if element is empty
        """
        if default_list is None:
            default_list = []
        if element not in EMPTIES:
            self._ensure_list_field(field, default_list)
            if element not in self.record[field]:
                self.record[field].append(element)
        elif kwargs:
            if 'record' in kwargs and isinstance(kwargs['record'], six.string_types):
                kwargs['record'] = {'$ref': kwargs['record']}
            self._ensure_list_field(field, default_list)
            if kwargs not in self.record[field]:
                self.record[field].append(kwargs)

    @staticmethod
    def _prepare_url(value, description=None):
        """Build url dict satysfying url.yml requirements

        Args:
            value (str): URL itself
            description (str): URL description
        """
        entry = {
            'value': value
        }
        if description:
            entry['description'] = description
        return entry

    def validate_record(self):
        """Validate the record in according to the hep schema."""
        validate(self.record, 'conferences')

    @filter_empty_parameters
    def add_private_note(self, value=None, source=None):
        """Add private note to ``_private_notes`` list.

        Args:
            value (str): Value of the note.
            source (str): Source of the information in this field
        """
        self._append_to('_private_notes', source=source, value=value)

    @filter_empty_parameters
    def add_acronym(self, acronym=None):
        """Add acronyms.

        Args:
            acronym (str): acronym if the conference, e.g. ``SUSY 2018``.
        """
        self._append_to('acronyms', acronym)

    @filter_empty_parameters
    def add_address(
        self,
        cities=None,
        country_code=None,
        latitude=None,
        longitude=None,
        place_name=None,
        postal_address=None,
        postal_code=None,
        state=None,
    ):
        """Add a new address to the addresses list.

        Args:
            cities (list): list of strings containing cities.
            country_code (str): string of length 2 representing the country.
            latitude (float): latitude of the location.
            longitude (float): longitude of the location.
            place_name (str): name of the specific place where this is located.
            postal_address (str): full postal address in original language.
            postal_code (str): postal code of the location.
            state (str): state or province of the location.
        """
        self._append_to(
            'addresses',
            cities=cities,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            place_name=place_name,
            postal_address=postal_address,
            postal_code=postal_code,
            state=state,
        )

    @filter_empty_parameters
    def add_alternative_title(self, title, subtitle=None, source=None):
        """Add an alternative title.

        Args:
            title (str): an alternative title for this conference.
            subtitle (str): subtitle for this title.
            source (str): source for the given title.
        """
        title_entry = self._sourced_dict(
            source,
            title=title,
        )
        if subtitle is not None:
            title_entry['subtitle'] = subtitle

        self._append_to('alternative_titles', title_entry)

    def set_cnum(self, cnum=None):
        """Add CNUM identifier

        Args:
            cnum (str): CNUM id of this conference.
        """
        if cnum is not None:
            self.record['cnum'] = cnum

    @filter_empty_parameters
    def add_contact(self, name=None, email=None, curated_relation=None, record=None):
        """Add a contact object to the list of ``contact_details``.

        Args:
            name (str): name of the contact.
            email (str): email to the contact.
            curated_relation (bool): mark if relation is curated [NOT REQUIRED]
            record (dict): dictionary with ``$ref`` pointing to proper record.
            If string, then will be converted to proper dict.
        """
        self._append_to(
            'contact_details',
            name=name,
            email=email,
            curated_relation=curated_relation,
            record=record,
        )

    @filter_empty_parameters
    def add_external_system_identifier(self, value, schema):
        """Add external job identifier to ``external_system_identifiers`` field.

        Args:
            value (str): the identifier to add.
            schema (str): schema to which the identifier belongs.
        """
        self._append_to(
            'external_system_identifiers',
            schema=schema,
            value=value,
        )

    @filter_empty_parameters
    def add_inspire_categories(self, subject_terms, source=None):
        """Add inspire categories.

        Args:
            subject_terms (list): user categories for the current document.
            source (str): source for the given categories.
        """
        for category in subject_terms:
            category_dict = self._sourced_dict(
                source,
                term=category,
            )
            self._append_to('inspire_categories', category_dict)

    @filter_empty_parameters
    def add_keyword(self, value, schema=None, source=None):
        """Add a keyword.

        Args:
            keyword (str): keyword to add.
            schema (str): schema to which the keyword belongs.
            source (str): source for the keyword.
        """
        keyword_dict = self._sourced_dict(source, value=value)

        if schema is not None:
            keyword_dict['schema'] = schema

        self._append_to('keywords', keyword_dict)

    @filter_empty_parameters
    def add_public_note(self, value, source=None):
        """Add public note.

        Args:
            value (str): public note for the current article.
            source (str): source for the given notes.
        """
        self._append_to('public_notes', self._sourced_dict(
            source,
            value=value,
        ))

    @filter_empty_parameters
    def add_series(self, name, number=None):
        """Add conference series.

        Args:
            name (str): name of the conference series.
            number (int): number of the conference series.
        """
        serie_object = self._sourced_dict(name=name)
        if number:
            serie_object['number'] = number
        self._append_to('series', serie_object)

    @filter_empty_parameters
    def add_title(self, title, subtitle=None, source=None):
        """Add a title to this confertence.

        Args:
            title (str): title for the current document.
            subtitle (str): subtitle for the current document.
            source (str): source for the given title.
        """
        title_entry = self._sourced_dict(
            source,
            title=title,
        )
        if subtitle is not None:
            title_entry['subtitle'] = subtitle

        self._append_to('titles', title_entry)

    @filter_empty_parameters
    def add_url(self, value, description=None):
        """Add url dict to ``urls`` list.

        Args:
            value (str): url itself.
            description (str): description of the url.
        """
        entry = self._prepare_url(value, description)
        self._append_to('urls', entry)

    def set_closing_date(self, date=None):
        """Add conference closing date.

        Args:
            date (str): conference closing date.
        """
        if date is not None:
            self.record['closing_date'] = normalize_date(date=date)

    def set_core(self, core=True):
        """Set core flag.

        Args:
            core (bool): define a core article
        """
        self.record['core'] = core

    def set_opening_date(self, date=None):
        """Add conference opening date.

        Args:
            date (str): conference opening date.
        """
        if date is not None:
            self.record['opening_date'] = normalize_date(date=date)

    def set_short_description(self, value, source=None):
        """Set a short descritpion

        Args:
            value (str): the description to set.
            source (str): source of the description.
        """
        self.record['short_description'] = self._sourced_dict(
            source=source,
            value=value
        )
