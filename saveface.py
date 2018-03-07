#! /usr/bin/python
# -*- coding: UTF-8 -*-
"""Summary
"""
from abc import ABC
from queue import Queue
import argparse
import os
import pprint
import sys
import threading
import urllib
import json
from facepy import GraphAPI
from facepy import exceptions as fpexceptions
import json
import dicttoxml
from xml.etree import ElementTree as ET

from boundinnerclasses import BoundInnerClass


##an abstract base class for the passing of the class hierarchy
##in a memory efficient and polymorphic manner.
##I lost memory by including the bound innerclass 'Download thread'
##which I am doing temporarily to examine the access ramifications
##and the ease of using the bound inner class library 
##the class hierarchy then extends from the ABC to a concrete base class
##that saves pages as an array
##which then is extended into utility types, that save as xml, or json etc
class SaveFaceABC(ABC):
    def __init__(self):
        self._num_pages = 0
        self._num_images = 0
        self._images_total = 0
        self._imgpath_element = []
        self._compact = False
        self._indent = 4
        self._depth = None
        self._width = 80
        self._graph = None
        self._img_folder = 'images'

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

    @BoundInnerClass 
    class __DownloadThread_(threading.Thread):
        """
        A bound inner thread class
        http://code.activestate.com/recipes/577070-bound-inner-classes/
        
        Attributes:
            daemon (bool): Description
        """
        def __init__(self, queue, img_folder):
            """Summary
            
            Args:
                queue (TYPE): Description
                img_folder (TYPE): Description
            """
            #print(outer)
            super(SaveFace.__DownloadThread_, self).__init__()
            self._queue = queue
            self._destfolder = img_folder
            self.daemon = True

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
            print("[%s] Downloading %s -> %s" % (self.ident, el.nodeValue, self._destfolder))
            try:
                img = urllib.FancyURLopener(el.nextSibling.nodeValue, self._destfolder)
            #get file tyoe
                imgtype = img.info().getsubtype()
            #construct name
                name = str(outer._num_images) + '.' + imgtype
                name = name.split('/')[-1]
            #construct path
                dest_path = os.path.join(self._destfolder, name)
            #store path and element to set path in xml later - may need thread.lock
                outer.imgpath_element.push((dest_path, el))
            #read file data from urllib stream
                buf = img.read()
            #write file data
                downloaded_image = file(dest_path, "wb")
                downloaded_image.write(buf)
                downloaded_image.close()
            #close urllib stream
                img.close()
            #increment counter for name and print progress
                outer._num_images += 1
                print_progress(outer._num_images, outer._images_total)
            except (urllib.ContentTooShortError, IOError) as e:
                print(type(e))
                print(e.args)
                print(e)    

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
        super.__init__()
        
        self.write_pages = False  #write pages as they are received
        self.pages = [] #the result dictionary
        self.args = {} #the args from command line input
        self.O_Auth_tkn = None # the auth token

    #graph functions
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

    def get_page_from_graph(self, request_string=None, graph=None, verbose=True):
        """
            Gets a page from the facebook graph
        
        Args:
            request_string (string, optional): a request string for facebook graph api
            graph (string, optional): facepy graph object from inst.init_graph        
        Returns:
            dict: a dictionary containing the results from facebook
        
        Raises:
            fpexceptions.OAuthError, fpexceptions.FacebookError, fpexceptions.FacepyError: 
               facepy request errors
        """
        if graph is None:
            if self._graph is None:
                raise ValueError("graph must be initialised")
            else:
                graph = self._graph

        if request_string is None:
            if self.args.request_string is not None:
                request_string = self.args.request_string

        try:
            return graph.get(request_string)
        except (fpexceptions.OAuthError, fpexceptions.FacebookError, fpexceptions.FacepyError) as e:
            print(type(e))
            print(e.args)
            print(e) 

    def get_pages_from_graph(self, graph=None, number_of_pages=None, request_string=None, verbose=True):
        """
        Gets and returns the json string from facebook
        
        Raises:
            ValueError: Raised if graph is not set is not set
        
        Args:
            graph (None, optional): Description
            verbose (bool, optional): Description
        
        Returns:
            array: array of dicts that are pages
        """
        if graph is None:
            if self._graph is None:
                raise ValueError("graph must be initialised")
            else:
                graph = self._graph
        try:
            num_pages = 0
            posts = {}
            pages = []
            while(True):
                sys.stdout.write("getting page number %d\n" % (self._num_pages + 1))
                num_pages = num_pages + 1
                print("hey there : " + str(len(posts.items())))
                if num_pages == number_of_pages:
                    request_string == posts.pop(['paging']['next'])
                    pages.push(self.get_page_from_graph(request_string))
                    if self.write_pages:
                        self.write(posts, "output_page%s" % (num_pages))
                else:
                    break
        except (fpexceptions.OAuthError, fpexceptions.FacebookError, fpexceptions.FacepyError, KeyError) as e:
                print(type(e))
                print(e.args)
                print(e)

        if verbose:
            print("received %s pages" % (num_pages))
        self._num_pages = num_pages
        self.pages = pages
        return pages

class SaveFaceXML():

    def __init__():
        super.__init__()

    def get_images(self, results):
        """
        gets the image urls from the received data
        and calls private function download
        
        Args:
            results(dict : required): dict results returned from facebook api
        
        Raises:
            ValueError: Description
        """
        if results is not dict:
            raise TypeError("parameter of get_images must be a dictionary")

        if results != {}:
            xmlstring = dicttoxml.dicttoxml(results, attr_type=False)

        self._root = ET.fromstring(xmlstring)
    #test
        for it in self._root.iterfind('image'):
            print(it)

        elements = []
        els = self._root.findall('image')
        for el in els:
            elements.push(el.find('src')[0])
        els = self._root.findall('full_picture')
        elements = elements + els
        print ('hey' + str(len(elements)))
        self.__download_(elements)

    def embed_file_paths():
        pass  #TODO

    #output
    def write(self, results, filename, filepath, type='raw', asBytes=True):
        """
            Writes data to file as str. type is passed as
            either 'json','xml','raw'. The data is written as a
            bytes.
        
        Args:
            results (str): string to write 
            type (str): Either 'json' or 'xml'
        """
        SUPPORTED_TYPES = ['xml','json','raw'] #'pprint'
        if type not in SUPPORTED_TYPES:
            raise ValueError('Unsupported type "%s". Supported types are %s' % (type, ', '.join(SUPPORTED_TYPES)))
        if type == 'xml':
            s = dicttoxml.dicttoxml(results, attr_type=False) 
        elif type == 'json':
            s = json.dumps(results).emcpde()
        elif type is 'raw':
            s = str(results).encode()

        if asBytes:
            with open(filename, "wb") as f:
                f.write(s)
        else:
            with open(filename, "w") as f:
                f.write(s.decode())

    def prprint(self, fbjson=None, _indent=None, _width=None, _depth=None):
        """prettyprints the results string
        
        Args:
            fbjson (json, optional): json string returned from graph.get
        
        Returns:
            TYPE: Description
        """
        if _indent == None:
            if self.args.pprintopts['indent'] is not None:
                _indent = self.args.pprintopts['indent']
            else:
                _indent = 4
        if _width == None:
            if self.args.pprintopts['width'] is not None:
                _width = self.args.pprintopts['width']
            else:
                _width = 80
        if _depth == None:
            if self.args.pprintopts['depth'] is not None:
                _depth = self.args.pprintopts['depth']
        if fbjson == None:
            fbjson == self._fbjson

        return pprint.pformat(fbjson, indent=_indent, width=_width, depth=_depth)

    def process_args(self, args):
        """
        Internal function used by script when standalone
        
        Args:
            args (dict): args from argparser
        
        No Longer Raises:
            ValueError: if O_Auth_tkn is not set
        """
        self.args = args
        self._img_folder = self.args.img_folder
        self.init_graph(args.O_Auth_tkn)
        self.fbjson = self.get_from_graph()

        if self.args.format == 'xml':
            result = dicttoxml.dicttoxml(self.fbjson, attr_type=False)
        elif self.args.format == 'pjson':
            self.__prepare_pprint_()
            result = self.prprint() #compact is not yet instantiated compact=self._compact)
        else:
            result = self.pages

        if self.args.output == 'stdout':
            print(result)
        else:
            self.write(result, self.args.output, 'raw')

        #images
        if self.args.images == True:
            self.get_images(result)
            #exchange the text in the url nodes from the node list
            #with local filepaths
            #TODO

            #self._root

    def __prepare_pprint_(self):
        """
        prepares the pprint options string from the args
        
        Raises:
            ValueError: Description
        """
        SUPPORTED_TYPES = ['indent','width','depth']
        self.args.pprintopts = {}
        for a in args.pprint_opts:
            b = a.split('=')
            if b[0] not in SUPPORTED_TYPES:
                raise ValueError('Unsupported type "%s". Supported types are %s' % (b[0], ', '.join(SUPPORTED_TYPES)))
            if b[1] != 'None':
                if b[1] == 'bool':
                    self.args.pprintopts[b[0]] = bool(b[1])
                else:
                    self.args.pprintopts[b[0]] = int(b[1])
            else:
                self.args.pprintopts[b[0]] = None     

def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100):
    """
    Call in a loop to create terminal progress bar
    https://gist.github.com/aubricus/f91fb55dc6ba5557fbab06119420dd6a
    Args:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix))

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()

if __name__ == "__main__":
    #me?fields=id,name,posts.include_hidden(true){created_time,from,message,comments{created_time,from,message,comments{created_time,from,message},attachment},full_picture}
    defaultqstring = "me?fields=id,name,posts.include_hidden(true)\
                     {created_time,from,message,comments\
                     {created_time,from,message,comments\
                     {created_time,from,message},attachment},full_picture}"
    
    parser = argparse.ArgumentParser(epilog="Saving Face with saveface.py", description="Download facebook posts,comments,images etc.\n\
        Default request string is :\n" + defaultqstring)
    
    parser.add_argument('-a --auth_tkn', metavar='facebook auth token', type=str, required=True, nargs='?', 
        help='Required. Your app\'s facebook authorisation token', 
        dest='O_Auth_tkn')
    parser.add_argument('-r --request_string', metavar='rest api request string', type=str, required=False, nargs='?',
        default=defaultqstring, 
        help='Optional. The request string to query facebook\'s api. Defaults to posts,comments,images',
        dest='request')
    parser.add_argument('-f --format', metavar='output format for results', type=str, required=False, nargs='?',
        default='json', help='Optional. Can be one of json, pjson (prettyprinted) or xml. Defaults to json', 
        choices=['json', 'pjson', 'xml'], 
        dest='format')
    parser.add_argument('-o --output', metavar='how to output the results', type=str, required=False, nargs='?',
        default='stdout', help='Optional. Accepts a string filename. Defaults to stdout', 
        dest='output')
    parser.add_argument('-i --images', metavar='download images?',  type=bool, required=False, nargs='?',
        default=False, help='Optional.  A boolean to indicate whether or not to download images. Defaults to false', 
        dest='images')
    parser.add_argument('-d --image_path', metavar='path to images', type=str, required=False, nargs='?',
        default='images', help='Optional. The path to the images folder. Defaults to ./images', 
        dest='img_folder')
    parser.add_argument('-p --pprint_options', metavar='pprint options', type=str, required=False, nargs='*',
        default='indent=4, width=80, depth=None, compact=False', help="Optional. Options string for pprint module.\n\
        Parameters must be named key=value with no comma ie indent=4 depth=80.",
        dest='pprint_opts')

    args = parser.parse_args()
    SF = SaveFace()
    SF.process_args(args)