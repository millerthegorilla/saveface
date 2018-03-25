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
import json
import pickle
import sys
import requests
from time import strftime
from facepy import GraphAPI
from facepy import exceptions as fpexceptions
from pathlib import Path
from saveface import SaveFace
from saveface import pretty_search


class SaveFaceJSON(SaveFace):
    """
    A class to download information using the facebook graph api
    and save them in a variety of formats.  My first python, more or less,
    to teach myself some of the language features
    Attributes:
        args (dict): args that get passed in from argparser
        fbjson (dict): dict representation of json string
        filename (string): filename to store data in
        O_Auth_tkn (TYPE): Description
    """
    def __init__(self, formatter=None):
        """
        initialise class variables
        """
        super().__init__(formatter)

        # private
        self._num_pages = 0
        self._num_images = 0
        self._images_total = 0
        self._imgpath_element = []

        # pprint options
        self._compact = False
        self._indent = 4
        self._depth = None
        self._width = 80
        self._graph = None
        self._img_folder = 'images'

        # public variables
        self.filename = ""
        self.filepath = ""
        self.pages = []  # the result dictionary
        self.json_data = []
        self.data_classes = []  # the data class objects
        self._default_pickle = strftime("sfp_%d_%m_%y-%H:%M:%S")
        self._last_pickle = self.__get_last_pickle_()

    @property
    def json(self):
        return self.formatter.json

    # graph functions
    def init_graph(self, O_Auth_tkn=None):
        """
            set the internal graph object
        Args:
            O_Auth_tkn (None, optional): Description
        Returns:
            TYPE: Description
        Raises:
            ValueError: Description
        """
        super().init_graph(O_Auth_tkn)

        if O_Auth_tkn is not None:
            try:
                graph = GraphAPI(O_Auth_tkn)
            except (fpexceptions.OAuthError, fpexceptions.HTTPError) as e:
                print(type(e))
                print(e.args)
                print(e)
        else:
            raise ValueError("O_Auth_tkn must be present")

        self._graph = graph

    def get_page_from_graph(self, request_string=None,
                            graph=None, verbose=True):
        """
            Gets a page from the facebook graph
        Args:
           request_string (string, optional): facebook graph api request string
           graph (string, optional): facepy graph object from inst.init_graph
        Returns:
            dict: a dictionary containing the results from facebook
        Raises:
            fpexceptions.OAuthError,
            fpexceptions.FacebookError,
            fpexceptions.FacepyError:
               facepy request errors
        """
        super().get_page_from_graph(request_string, graph, verbose)

        if self._graph is None:
            raise ValueError("graph must be initialised")

        if request_string is None:
            raise ValueError("request_string must be defined")

        try:
            return graph.get(request_string)
        except (fpexceptions.OAuthError,
                fpexceptions.FacebookError,
                fpexceptions.FacepyError) as e:
            raise e

    def request_page_from_graph(self, request_string=None, verbose=True):
        super().request_page_from_graph(request_string, verbose)

        if self._graph is None:
            raise ValueError("graph must be initialised")

        if request_string is None:
            raise ValueError("request_string must be defined")

        try:
            return requests.get(request_string).json()
        except (fpexceptions.OAuthError,
                fpexceptions.FacebookError,
                fpexceptions.FacepyError) as e:
            raise e

    def get_pages_from_graph(self, graph=None, number_of_pages=None,
                             request_string=None, verbose=True):
        """
        Populates a list of dicts representing pages of stored
                    in an array from facebook
        I wasn't able to get the facepy iterator working, and it
        may be my knowledge of python rather than the code on github
        so I will look more at it when I have time.  The code on github
        returned a generator but it cleaned the request dictionary
        after each page was returned, so would only succesfully
        return one page.  If I can't get it working, then I may
        write a function here that returns a generator for the
        sake of learning, and also to challenge the practical problem
        that I have faced generally here, which is to write a general purpose
        program to handle an unknown json structure and parse it meaningfully
        into something useful.
        Raises:
            ValueError: Raised if graph is not set is not set
        Args:
            graph (None, optional): Description
            verbose (bool, optional): Description
        Returns:
            array: array of dicts that are pages
        """
        super().get_pages_from_graph(graph,
                                     number_of_pages,
                                     request_string,
                                     verbose)

        num_pages = 0
        pages = []
        found = False
        pages.append(self.request_page_from_graph(request_string))
        try:
            while True:
                for np in self.dict_extract('next', pages[-1]):
                    found = True
                    pages.append(self.request_page_from_graph(np))
                    num_pages = num_pages + 1
                if found:
                    found = False
                else:
                    break
                if number_of_pages is not None and num_pages < number_of_pages:
                    break

                if verbose:
                    print('received \
                        page number {}   '.format(num_pages), end="\r")

        except (fpexceptions.OAuthError,
                fpexceptions.FacebookError,
                fpexceptions.FacepyError,
                KeyError) as e:
            print(type(e))
            print(e.args)
            print(e)

        if verbose:
            print('received {} pages            '.format(num_pages), end='\r')
        self._num_pages = num_pages
        self.pages = pages[:-1]

    def get_data_from_pages(self):
        for page in self.pages:
            # TODO :  Here I need to put any top level data that is
            # above the first instance of data
            e = pretty_search(page, 'data', True)
            if e is not None:
                self.json_data = self.json_data + e

    def get_data_as_classes(self):
        class Post:
            @classmethod
            def from_dict(cls, dict):
                obj = cls()
                obj.__dict__.update(dict)
                return obj

        if len(self.data):
            for i in self.data:
                self.data_classes.append
                (json.loads(json.dumps(i), object_hook=Post.from_dict))
        else:
            raise ValueError("posts list is empty. \
                             Call get_data_from_pages first!")
        return self.data_classes

    # pickle the pages array
    def save_pages_to_pickle(self, pickler='default_pickle'):
        if pickler is 'default_pickle':
            pickler = self._default_pickle
        if self.pages is not None:
            with open(pickler, 'wb') as outfile:
                pickle.dump(self.pages, outfile)
            with open('sfdefault', 'wb') as outfile:
                pickle.dump(pickler, outfile)

    def get_pages_from_pickle(self, pickler=None):
        if pickler == 'last':
            pickler = self._last_pickle
        with open(pickler, 'rb') as infile:
            self.pages = pickle.load(infile)

    def __get_last_pickle_(self):
        try:
            with open('sfdefault', 'rb') as infile:
                try:
                    return pickle.load(infile)
                except EOFError:
                    return self._default_pickle
        except FileNotFoundError:
            return self._default_pickle

    def init_path(self, filename, filepath, overwrite):
        if not Path(filepath).exists():
            Path(filepath).mkdir(parents=True, exist_ok=True)
        file = filepath + filename
        if Path(file).is_file():
            if overwrite is False:
                raise OSError("File Exists")
                return False
            else:
                return True
        else:
            return file

    def write(self, filename, filepath, overwrite=True):
        super().write(filename, filepath, overwrite)
        self.init_path(filename, filepath, overwrite)

    def print_progress(iteration, total, prefix='',
                       suffix='', decimals=1, bar_length=100):
        """
        Call in a loop to create terminal progress bar
        https://gist.github.com/aubricus/f91fb55dc6ba5557fbab06119420dd6a
        Args:
        iteration(Int)- Required  : current iteration
        total    (Int)- Required  : total iterations
        prefix   (Str)- Optional  : prefix string
        suffix   (Str)- Optional  : suffix string
        decimals (Int)- Optional  : positive number of decimals in % complete
        bar_length(Int)- Optional : character length of bar
        """
        str_format = "{0:." + str(decimals) + "f}"
        percents = str_format.format(100 * (iteration / float(total)))
        filled_length = int(round(bar_length * iteration / float(total)))
        bar = '█' * filled_length + '-' * (bar_length - filled_length)

        sys.stdout.write('\r%s |%s| %s%s %s' %
                         (prefix, bar, percents, '%', suffix))

        if iteration == total:
            sys.stdout.write('\n')
        sys.stdout.flush()

    def __str__(self):
        string = ""
        for page in self.pages:
            string = string + page
        return string

    # def __repr__(self):
    #     return "<%s()>" % (self.__class__.__name__)
