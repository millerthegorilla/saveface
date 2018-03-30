#!/usr/env/bin/ python3
# Copyright (c) <2018> <James Miller>

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
import logging


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
                                request_url):
        pass

    @abstractmethod
    def get_page_from_graph(self):
        pass

    @abstractmethod
    def get_pages_from_graph(self,
                             number_of_pages=None,
                             verbose=True):
        pass

    @abstractmethod
    def write(self, results, filename, filepath, overwrite=True):
        pass

    def log(self, msg='', level='info',
            exception=None, std_out=False, to_disk=False):
        log_level = {
            'debug'     : logging.debug,
            'info'      : logging.info,
            'warning'   : logging.warning,
            'error'     : logging.error,
            'critical'  : logging.critical
        }.get(level, logging.debug('unable to log - check syntax'))
        if exception is not None:
            raise type(exception)(msg)
        if std_out is not False:
            log_level(msg)


# https://stackoverflow.com/questions/9807634/find-all-occurrences-of-a-key-in-nested-python-dictionaries-and-lists
def dict_extract(key, var, first=False):
    if hasattr(var, 'items'):
        for k, v in var.items():
            if k == key:
                yield v
                if first:
                    raise StopIteration('found')
            if isinstance(v, dict):
                for result in dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in dict_extract(key, d):
                        yield result
