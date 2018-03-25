#!/usr/env/bin/ python3
# Copyright (c) <2018> <James Miller>
# -*- coding: utf-8 -*-
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""A work in progress to download facebook information using facepy
   It will output json, xml, or html with pictures.
"""
from abc import ABC, abstractmethod


# TODO: determine what methods go here, for
# the sake of a useful isinstance() call.
class SaveFace(ABC):
    # abstract base class
    # I now realise that python uses duck typing
    # rather than upcasting etc
    # so I guess that I'd have to write a helper
    # function internally to allow me to upcast
    # but this is here for study purposes as
    # well as more practical reasons.
    # As far as I understand abc allows the
    # definition of an interface, which is useful
    # for standardising data exchange structures
    # such as json classes and also formatting
    # like savefaceformatter
    # Then isinstance can be used in conditional
    # logic based on the capabilities of the object
    # https://www.python.org/dev/peps/pep-3119/
    @abstractmethod
    def __init__(self, formatter=None):
        super().__init__()

    @abstractmethod
    def init_graph(self, O_Auth_tkn=None):
        pass

    @abstractmethod
    def request_page_from_graph(self,
                                request_string=None,
                                graph=None,
                                verbose=True):
        pass

    @abstractmethod
    def get_page_from_graph(self,
                            request_string=None,
                            graph=None,
                            verbose=True):
        pass

    @abstractmethod
    def get_pages_from_graph(self,
                             graph=None,
                             number_of_pages=None,
                             request_string=None,
                             verbose=True):
        pass

    @abstractmethod
    def write(self, results, filename, filepath, overwrite=True):
        pass


# https://stackoverflow.com/questions/9807634/find-all-occurrences-of-a-key-in-nested-python-dictionaries-and-lists
def dict_extract(key, var):
    if hasattr(var, 'items'):
        for k, v in var.items():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in dict_extract(key, d):
                        yield result


# https://stackoverflow.com/questions/8383136/parsing-json-and-searching-through-it
def pretty_search(dict_or_list, key_to_search, search_for_first_only=False):
    """
    Give it a dict or a list of dicts and a dict key (to get values of),
    it will search through it and all containing dicts and arrays
    for all values of dict key you gave, and will return you set of them
    unless you wont specify search_for_first_only=True

    :param dict_or_list:
    :param key_to_search:
    :param search_for_first_only:
    :return:
    """
    search_result = set()
    if isinstance(dict_or_list, dict):
        for key in dict_or_list:
            key_value = dict_or_list[key]
            if key == key_to_search:
                if search_for_first_only:
                    return key_value
                else:
                    search_result.add(key_value)
            if isinstance(key_value, dict) or isinstance(key_value, list) or isinstance(key_value, set):
                _search_result = pretty_search(key_value, key_to_search, search_for_first_only)
                if _search_result and search_for_first_only:
                    return _search_result
                elif _search_result:
                    for result in _search_result:
                        search_result.add(result)
    elif isinstance(dict_or_list, list) or isinstance(dict_or_list, set):
        for element in dict_or_list:
            if isinstance(element, list) or isinstance(element, set) or isinstance(element, dict):
                _search_result = pretty_search(element, key_to_search, search_result)
                if _search_result and search_for_first_only:
                    return _search_result
                elif _search_result:
                    for result in _search_result:
                        search_result.add(result)
    return search_result if search_result else None
