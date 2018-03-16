#!/usr/env/bin/ python3
# -*- coding: UTF-8 -*-
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
import argparse
import json
import os
import pprint
import sys
import threading
import requests
import re

from argparse import RawTextHelpFormatter
from boundinnerclasses import BoundInnerClass
from dicttoxml import dicttoxml
from facepy import GraphAPI
from facepy import exceptions as fpexceptions
from pathlib import Path
from queue import Queue
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup as bs
import pickle


class SaveFaceABC(ABC):
    # abstract base class
    # every time I want to program, I find my lungs being deliberately
    # blocked so that my mental acuity disappears, and my logic and recall
    # skills diminish.  I do not smoke.  #intellectualslavery
    # abstract base class indeed.
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
        A bound inner thread class
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
        self.pages = pages
        self.__format_()
        return pages

    def __format_(self):
        pass

    def get_posts_from_pages(self):
        if self.pages is not None:
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


class SaveFaceXML(SaveFace):
    def __init__(self):
        super().__init__()
        self.xml = ET.fromstring("<content></content>")
        self.xmlposts = []

    def get_pages_from_graph(self, graph=None, number_of_pages=None,
                             request_string=None, verbose=True):
        super().get_pages_from_graph(graph,
                                     number_of_pages,
                                     request_string,
                                     verbose)
        self.__format_()

    def get_pages_from_pickle(self):
        super().get_pages_from_pickle()
        self.__format_()

    def get_posts_from_pages(self):
        super().get_posts_from_pages()
        for p in self.posts:
            self.xmlposts.append(ET.XML(dicttoxml(p, attr_type=False, custom_root='post')))

    def __format_(self):
        if len(self.pages):
            for page in self.pages:
                self.xml.append(ET.XML(dicttoxml(page, attr_type=False, custom_root='page')))

    def write(self, filename, filepath, overwrite=True):
        """
            Writes data to file as xml
        Args:
            results (str): string to write
            type (str): Either 'json' or 'xml'
        """
        super().write(filename, filepath, overwrite)
        try:
            with open(filename, 'wb') as output:
                ET.ElementTree(self.xml).write(output,
                                               encoding="UTF-8",
                                               xml_declaration=True)
        except IOError as e:
            print(type(e))
            print(e.args)
            print(e)

    def get_images(self):
        """
        gets the image urls from the received data
        and calls private function download
        Args:
            results(dict : required): dict results returned from facebook api
        Raises:
            ValueError: Description
        """
        # test
        for it in self.xml.iterfind('image'):
            print(it)

        elements = []
        els = self.xml.findall('image')
        for el in els:
            elements.push(el.find('src')[0])
        els = self.xml.findall('full_picture')
        elements = elements + els
        self.__download_(elements)

    def embed_file_paths():
        pass  # TODO

    def __str__(self):
        return ET.tostring(self.xml, encoding="unicode", method="xml")


class SaveFaceHTML(SaveFaceXML):

    def __init__(self):
        super().__init__()
        self.html = ''

    def get_pages_from_graph(self, graph=None, number_of_pages=None,
                             request_string=None, verbose=True):
        super().get_pages_from_graph(graph,
                                     number_of_pages,
                                     request_string,
                                     verbose)
        self.__format_()

    def get_pages_from_pickle(self):
        super().get_pages_from_pickle()
        self.__format_()

    def __format_(self, cssfile='saveface.css'):
        self.xhtml = ET.fromstring("<content></content>")
        super().get_posts_from_pages()

        if len(self.xmlposts):
            for p in self.xmlposts:
                self.xhtml.append(p)

        htmllist = self.xhtml.findall('.//full_picture')
        for el in htmllist:
            el.insert(0, ET.Element('img', attrib={'class': 'image',
                                                   'src': el.text}))
            el.text = None

        for el in self.xhtml.iter():
            if el.tag is not 'img':
                el.attrib = {'class': el.tag, **el.attrib}
                el.tag = 'div'

        self.xhtml.tag = 'content'

        self.html = '<html> \
                    <head> \
                    <link rel="stylesheet"' + \
                    'href="' + cssfile + '">' + \
                    '<title>SaveFacePie</title>' + \
                    '</head><body>' + \
                    ET.tostring(self.xhtml,
                                encoding='unicode',
                                method='html') + \
                    '</body></html>'
        # self.xml.find('.//root').append
        # (self.xml.find('.//root/posts/data'))

        # self.xml.find('.//root/posts/..').remove
        # (self.xml.find('.//root/posts'))

        # newroot = ET.fromstring("<content></content>")
        # for i in self.xml.findall('.//data'):
        #     newroot.append(i)

        # self.xml = newroot
        # # images
        

        # for i in self._root.findall('.//item/id/.'):
        #     e = ET.Element('p', attrib={'class': 'title post'})
        #     e.text = 'post id : ' + i.text
        #     i.append(e)
        #     i.text = None

        # for i in self._root.findall('.//paging/..'):
        #     i.remove(i.find('./paging'))

        # for i in self._root.findall('.//item/.'):
        #     i.attrib = {'class': 'post'}

        # htmlwrap(self._root.findall('.//item/..'),
        #          ET.Element('div', attrib={'class': 'page'}),
        #          ['item'])
        # htmlwrap(self._root.findall('.//from/.'),
        #          ET.Element('div', attrib={'class': 'user id'}),
        #          ['id'])
        # htmlwrap(self._root.findall('.//item/.'),
        #          ET.Element('div', attrib={'class': 'from'}),
        #          ['created_time', 'from'])
        # htmlwrap(self._root.findall('.//item/.'),
        #          ET.Element('div', attrib={'class': 'picture'}),
        #          ['full_picture'])
        # htmlwrap(self._root.findall('.//item/.'),
        #          ET.Element('div', attrib={'class': 'post msg'}),
        #          ['message'])
        # htmlwrap(self._root.findall('.//item/.'),
        #          ET.Element('div', attrib={'class': 'post id'}),
        #          ['id'])

    def htmlwrap(element_list, wrapper_element, tags):
        for element in element_list:
            wrap_element = ET.Element(wrapper_element.tag,
                                      wrapper_element.attrib)
            for el in list(element):
                if el.tag in tags:
                    element.remove(el)
                    wrap_element.append(el)
            element.append(wrap_element)

    # todo - add xml_declaration
    def write(self, filename, filepath, method='html', overwrite=True):
        """
            Writes data to file as xml
        Args:
            filename (str): name of file
            filepath (str): path to file
            overwrite(bool): whether to overwrite file
        """
        # super().write(filename, filepath, 'html', overwrite)
        with open(filepath + filename, 'w') as output:
            output.write(bs(self.html,
                            "html.parser").prettify())

    def __str__(self):
        return bs(self.html, "html.parser").prettify()


class SaveFaceJSON(SaveFace):

    def __init__(self, ispretty=False, indent=4, width=80, depth=None):
        super().__init__()
        self.json = {}
        self._indent = indent
        self._width = width
        self._depth = None
        self._ispretty = ispretty

    def get_pages_from_graph(self,
                             graph=None,
                             number_of_pages=None,
                             request_string=None,
                             verbose=True):
        super().get_pages_from_graph(graph,
                                     number_of_pages,
                                     request_string,
                                     verbose)
        page_string = ''
        if len(self.pages):
            for page in self.pages:
                page_string = page_string + str(page)
        self.json = json.loads(json.dumps(page_string))

    def write(self, filename, filepath, overwrite=True):
        super().write(filename, filepath, overwrite)
        try:
            with open(filename, 'w') as output:
                if self._ispretty:
                    json.dump(pprint(indent=self._indent,
                                     width=self._width,
                                     depth=self._depth), output)
                else:
                    json.dump(self.json, output)
        except IOError as e:
            print(type(e))
            print(e.args)
            print(e)

    def prprint(self, indent=None, width=None, depth=None):
        """prettyprints the results string
        Args:
            indent: int
            width: int
            depth: int    values for pprint
        Returns:
            str: pretty printed string representation
        """
        if indent is not None:
            indent = self._indent
        if width is not None:
            width = self._width
        if depth is not None:
            depth = self._depth

        if self.json is None:
            raise ValueError("Json object can not be none.  Get Page/s first")
        else:
            return pprint.pformat(self.json, indent=indent | self._indent,
                                  width=self._width, depth=self._depth)

    def __str__(self):
        if self._ispretty:
            return pprint()
        else:
            return json.dumps(self.json)


def process_args(args):
    """
    Internal function used by script when standalone
    Args:
        args (dict): args from argparser
    No Longer Raises:
        ValueError: if O_Auth_tkn is not set
    """
    sf = None
    if args.format == 'xml':
        sf = SaveFaceXML()
    elif args.format == 'json':
        sf = SaveFaceJSON()
    elif args.format == 'pjson':
        __prepare_pprint_()
        sf = SaveFaceJSON(ispretty=True,
                          indent=args.pprint_opts['indent'],
                          width=args.pprint_opts['width'],
                          depth=args.pprint_opts['depth'])
    elif args.format == 'html':
        sf = SaveFaceHTML()

    if args.source == 'facebook':
        sf.init_graph(args.O_Auth_tkn)
        sf.get_pages_from_graph(request_string=args.request_string)
    elif args.source == 'pickle':
        sf.get_pages_from_pickle()

    if args.pickle:
        sf.save_pages_to_pickle()
    # if args.images:
    #     sf.get_images() args.img_folder

    if args.stdout:
        print(str(sf))
    if args.filename is not None:
        sf.write(args.filename, args.filepath)

    # images
    # if self.args.images == True:
        # self.sf.get_images(result)
        # exchange the text in the url nodes from the node list
        # with local filepaths
        # TODO


def __prepare_pprint_(args):
    """
    prepares the pprint options string from the args
    Raises:
        ValueError: Description
    """
    SUPPORTED_TYPES = ['indent', 'width', 'depth']
    for a in args.pprint_opts:
        b = a.split('=')
        if b[0] not in SUPPORTED_TYPES:
            raise ValueError('Unsupported type "%s". Supported types are %s'
                             % (b[0], ', '.join(SUPPORTED_TYPES)))
        if b[1] != 'None':
            args.pprint_opts[b[0]] = int(b[1])
        else:
            args.pprint_opts[b[0]] = None

    if args.pprint_opts['indent'] is None:
        args.pprint_opts['indent'] = 4
    if args.pprint_opts['width'] is None:
        args.pprint_opts['width'] = 80
    if args.pprint_opts['depth'] is None:
        args.pprint_opts['depth'] = 20


if __name__ == "__main__":
    # me?fields=id,name,posts.include_hidden(true){created_time,from,message,comments{created_time,from,message,comments{created_time,from,message},attachment},full_picture}
    defaultqstring = 'me?fields=posts.include_hidden(true) \
                     {created_time,from,message,comments \
                     {created_time,from,message,comments \
                     {created_time,from,message},attachment},full_picture}'
    parser = argparse.ArgumentParser(epilog="Saving Face with saveface.py",
                                     description="Download your facebook posts, \
                                                  comments,images etc.\n\
                                                  Default request \
                                                  string is :\n\
                                                  " + defaultqstring)
    parser.add_argument('-g', '--getfrom',
                        metavar='Where to source the pages from',
                        type=str, required=False, nargs='?',
                        default='facebook',
                        help='Optional. Can be one of facebook or pickle.\n\
                              Defaults to facebook\n',
                        choices=['facebook', 'pickle'],
                        dest='source')
    parser.add_argument('-a', '--auth_tkn',
                        metavar='facebook auth token',
                        type=str, required=False, nargs='?',
                        help='Optional. Your app\'s facebook \
                              authorisation token. Must be set \
                              to retrieve from facebook (see -g)',
                        dest='O_Auth_tkn')
    parser.add_argument('-r', '--request_string',
                        metavar='rest api request string',
                        type=str, required=False, nargs='?',
                        default=defaultqstring,
                        help='Optional. The request string \
                              to query facebook\'s api. \
                              Default request string above',
                        dest='request_string')
    parser.add_argument('-f', '--format',
                        metavar='output format for results',
                        type=str, required=False, nargs='?',
                        default='json', help='Optional. \
                                              Can be one of json, \
                                              pjson (prettyprinted), \
                                              xml or html. \
                                              Defaults to json',
                        choices=['json', 'pjson', 'xml', 'html'],
                        dest='format')
    parser.add_argument('-o', '--stdout',
                        metavar='output to stdout',
                        type=bool, required=False, nargs='?',
                        default=False, help='Optional. Output to stdout. \
                                             Defaults to False',
                        dest='stdout')
    parser.add_argument('-s', '--save',
                        metavar='pickle the array of pages',
                        type=bool, required=False, nargs='?',
                        default=False, help='Optional. Use Pickle to store the array of pages. \
                                             Defaults to False',
                        dest='pickle')
    parser.add_argument('-n', '--filename',
                        metavar='filename for the output',
                        type=str, required=False, nargs='?',
                        default=None, help='Optional. A filename for \
                                            the results. Results will \
                                            not be saved without \
                                            filename being specified',
                        dest="filename")
    parser.add_argument('-l', '--location',
                        metavar='filepath for the output',
                        type=str, required=False, nargs='?',
                        default='./', help='Optional. A filepath \
                                            for the results file. \
                                            Defaults to ./',
                        dest='filepath')
    parser.add_argument('-p', '--pprint_options',
                        metavar='pprint options',
                        type=str, required=False, nargs='*',
                        default='[indent=4, width=80, depth=None]',
                        help="Optional. Options for pprint module.\n\
                              key=value with comma ie -p [indent=4, depth=80]",
                        dest='pprint_opts')
    parser.add_argument('-i', '--images',
                        metavar='download images?',
                        type=bool, required=False, nargs='?',
                        default=False, help='Optional.  A boolean to indicate \
                                             whether or not to download \
                                             images. Defaults to False',
                        dest='images')
    parser.add_argument('-d', '--image_path',
                        metavar='path to images',
                        type=str, required=False, nargs='?',
                        default='images', help='Optional. The path to the \
                                                images folder.\
                                                Defaults to ./images',
                        dest='img_folder')
    parser.add_argument('-c', '--css',
                        metavar='css filename',
                        type=str, required=False, nargs='?',
                        default='saveface.css', help='Optional. The filename of the \
                                                css file.\
                                                Defaults to saveface.css',
                        dest='cssfile')

    process_args(parser.parse_args())
