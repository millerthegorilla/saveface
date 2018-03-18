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
import json
import os
import sys
import threading
import requests
import re
import pickle

from boundinnerclasses import BoundInnerClass
from facepy import GraphAPI
from facepy import exceptions as fpexceptions
from pathlib import Path
from queue import Queue


# this is my first go at python
# so if it seems to be ignoring a host
# of conventions then that is because
# I hack first, to get a feel for the
# strucures and terminology, and then
# I read the books in detail.
# as I work, I learn.  #nevergiveuphope
class SaveFaceABC(ABC):
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
    def __init__(self):
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


class SaveFace(SaveFaceABC):
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
    def __init__(self):
        """
        initialise class variables
        """
        super().__init__()

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
        self.posts = []
        self.post_classes = []  # the post class objects
        self.args = {}  # the args from command line input

    def __download_(self, elements, numthreads=4):
        """
        start threads downloading
        Args:
            elements (list): a list of elements
            numthreads (int, optional): number of threads
        """
        queue = Queue()
        for el in elements:
            queue.put(el)

        self._images_total = len(elements)

        for i in range(numthreads):
            t = SaveFace.__DownloadThread_(queue, self._img_folder)
            t.start()

        queue.join()

    def __update_images_(self, eltuple):
        self._imgpath_element.append(eltuple)
        self._num_images += 1
        self.print_progress(self._num_images, self._images_total)

    @BoundInnerClass
    class __DownloadThread_(threading.Thread):
        """
        A bound inner thread class - again for study purposes
        Python doesn't need or require inner classes
        and so far I can't see any reason to use it other than the
        reason I am investigating which is to examine, when I get round to
        it, how member access can be meaninfully and sensibly controlled
        both in the main and in worker threads.  If I continue to use
        multithreading (when implemented), then I'm better off putting
        the class at module level, and placing it in a different file
        to import, I guess, but I'm still learning about python, and want
        to examine memory usage in terms of structure instantiation, with
        a particular focus on the security model.  App programming with
        python is a potential possibility.
        http://code.activestate.com/recipes/577070-bound-inner-classes/
        Attributes:
            daemon (bool): Description
        """
        # def __init__(self, queue, img_folder):
        """Summary
        Args:
            queue (TYPE): Description
            img_folder (TYPE): Description
        """
        lock = threading.Lock()

        def __init__(self, group=None, target=None, name=None,
                     args=(), kwargs=None, verbose=None):
            super(SaveFace.__DownloadThread_, self).__init__(group=group,
                                                             target=target,
                                                             name=name,
                                                             verbose=verbose)
            self.args = args
            self.kwargs = kwargs
            self._queue = kwargs.queue
            self._destfolder = kwargs.img_folder
            self.daemon = True
            # super(SaveFace.__DownloadThread_, self).__init__()
            # self._queue = queue
            # self._destfolder = img_folder
            # self.daemon = True

        def run(self):
            """
            runs the threads
            """
            while True:
                el = self._queue.get()
                print('hello :' + el)
                try:
                    self.__download_img_(el)
                except Exception as e:
                    print(type(e))
                    print(e.args)
                    print(e)
                self._queue.task_done()

        def __download_img_(self, outer, el):
            """
            downloads images, makes filenames, prints download progress
            makes filename  mostly semi-psuedocode currently
            Args:
                outer (object): Outer class instance
                el (ElementTree<node>): element   TODO - check type
            """
            print("[%s] Downloading %s -> %s" % (self.ident,
                                                 el.nodeValue,
                                                 self._destfolder))
            try:
                r = requests.get(settings.STATICMAP_URL.format(**data),
                                 stream=True)
                if r.status_code == 200:
                    name = str(outer._num_images) + '.' + re.search
                    ('([^\/]+$)', r.headers['content-type'])
                    name = name.split('/')[-1]
                # construct path
                    dest_path = os.path.join(self._destfolder, name)
                    with open(dest_path, 'wb') as f:
                        for chunk in r:
                            f.write(chunk)

                # increment counter for name and print progress
                with SaveFace.__DownloadThread_.lock.acquire():
                    outer.__update_images_((el, dest_path))

            except (urllib.ContentTooShortError, IOError) as e:
                print(type(e))
                print(e.args)
                print(e)

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
            auth = O_Auth_tkn
        else:
            auth = self.args.O_Auth_tkn

        if auth is not None:
            try:
                graph = GraphAPI(auth)
            except (fpexceptions.OAuthError, fpexceptions.HTTPError) as e:
                print(type(e))
                print(e.args)
                print(e)
        else:
            raise ValueError("O_Auth_tkn must be present")

        self._graph = graph
        return graph

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

        if graph is None:
            if self._graph is None:
                raise ValueError("graph must be initialised")
            else:
                graph = self._graph

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

        if request_string is None:
            raise ValueError("request_string must be defined")

        try:
            return json.loads(json.dumps(requests.get(request_string).json()))
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

        if graph is None:
            if self._graph is None:
                raise ValueError("graph must be initialised")
            else:
                graph = self._graph

        num_pages = 0
        pages = []
        found = False
        pages.append(self.get_page_from_graph(request_string))

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
        self.__format_()
        return pages

    def __format_(self):
        pass

    def get_posts_from_pages(self):
        if self.pages is not None:
            if 'posts' in self.pages[0]:
                if 'data' in self.pages[0]['posts']:
                    self.posts = self.pages[0]['posts']['data']
                    for i in self.pages[1:]:
                        self.posts = self.posts + i['data']
                    for i in self.posts:
                        if 'comments' in i:
                            i['comments'] = i['comments']['data']
                            for j in i['comments']:
                                if 'comments' in j:
                                    j['comments'] = j['comments']['data']
        return self.posts

    def get_posts_as_classes(self):

        class Post:
            @classmethod
            def from_dict(cls, dict):
                obj = cls()
                obj.__dict__.update(dict)
                return obj

        if len(self.posts):
            for i in self.posts:
                self.post_classes.append
                (json.loads(json.dumps(i), object_hook=Post.from_dict))
        else:
            raise ValueError("posts list is empty. \
                             Call get_posts_from_pages first!")
        return self.post_classes

    # pickle the pages array
    def save_pages_to_pickle(self):
        if self.pages is not None:
            with open('savefacepickle', 'wb') as outfile:
                pickle.dump(self.pages, outfile)

    def get_pages_from_pickle(self):
        with open('savefacepickle', 'rb') as infile:
            self.pages = pickle.load(infile)
        self.__format_()

    # https://stackoverflow.com/questions/9807634/find-all-occurrences-of-a-key-in-nested-python-dictionaries-and-lists
    def dict_extract(self, key, var):
        if hasattr(var, 'items'):
            for k, v in var.items():
                if k == key:
                    yield v
                if isinstance(v, dict):
                    for result in self.dict_extract(key, v):
                        yield result
                elif isinstance(v, list):
                    for d in v:
                        for result in self.dict_extract(key, d):
                            yield result

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

    def __repr__(self):
        return "<%s()>" % (self.__class__.__name__)