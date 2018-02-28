#! /usr/bin/python
# -*- coding: UTF-8 -*-
"""Summary
"""
from Queue import Queue
import argparse
import os
import pprint
import sys
import threading
import urllib

from facepy import GraphAPI
from facepy import exceptions as fpexceptions
import requests
import dicttoxml
from xml.etree import ElementTree as ET

from boundinnerclasses import BoundInnerClass

class SaveFace:

    """
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
        self._num_pages = 0
        self._num_images = 0
        self._images_total = 0
        self._imgpath_element = []
        self._compact = False
        self._indent = 4
        self._depth = None
        self._width = 80
        self._graph = None

        self.fbjson = {}
        self.args = {}
        self.O_Auth_tkn = None

    def process_args(self, args):
        """
            Internal function used by script when standalone
        Args:
            args (dict): args from argparser
        
        Raises:
            ValueError: if O_Auth_tkn is not set
        """
        self.args = args

        self.set_graph(args.O_Auth_tkn)
        result = self.get_from_graph()

        if self.args.format == 'xml':
            result = dicttoxml.dicttoxml(self.fbjson, attr_type=False)
        elif self.args.format == 'pjson':
            self.__prepare_pprint_()
            result = pprint.pformat(self.fbjson, indent=self.args.pprintopts['indent'], 
                depth=self.args.pprintopts['depth'], width=self.args.pprintopts['width']) #compact is not yet instantiated compact=self._compact)
        else:
            result = self.fbjson

        if self.args.output == 'stdout':
            print(result)
        else:
            self.filename = self.args.output
            self.__write_(result)

        #images
        if self.args.images == True:
            self.get_images()
            #exchange the text in the url nodes from the node list
            #with local filepaths
            #TODO

            #self._root

    def __prepare_pprint_(self):
        """
            prepares the pprint options string
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

    def set_graph(self, O_Auth_tkn=None):
        if O_Auth_tkn is not None:
            auth = O_Auth_tkn
        else:
            auth = self.args.O_Auth_tkn

        if auth is not None:
            try:
                graph = GraphAPI(auth)
            except fpexceptions.OAuthError as e:
                print(type(e))
                print(e.args)
                print(e)
        else:
            raise ValueError("O_Auth_tkn must be present")

        self._graph = graph
        return graph

    def get_from_graph(self, graph=None, verbose=True):
        """
            Gets and returns the json string from facebook
        
        Raises:
            ValueError: Raised if graph is not set is not set
        """
        if graph is None:
            if self._graph is None:
                raise ValueError("Either pass graph or self._graph must not be none.\n\
                    Try (SaveFace)inst.set_graph()")
            else:
                graph = self._graph
        try:
            myjson = graph.get(self.args.request)['posts']
            sys.stdout.write("getting posts from %s\n" % (myjson['data'][-1]['created_time']))
            while(True):
                posts = requests.get(myjson.pop('paging')['next']).json()
                self._num_pages = self._num_pages + 1
                if len(posts['data']):
                    sys.stdout.write("getting posts from %s\n" % (posts['data'][-1]['created_time']))
                    myjson = dict(myjson, **posts)
                else:
                    break
        except (fpexceptions.OAuthError, KeyError) as e:
                print(type(e))
                print(e.args)
                print(e)

        if verbose:
            print("received %s pages" % (self._num_pages))

        self.fbjson = myjson
        return myjson

    def __write_(self, results):
        """
            writes data to file
        """
        if self.args.output is not "stdout":
            with open(self.args.output, "w") as f:
                f.write(results)

    def get_images(self, json=None, xmlstr=""):
        """
            gets the image urls from the received data
            and calls private function download
        """
        if xmlstr != "":
            xmlstring = xmlstr
        elif json != {}:
            xmlstring = dicttoxml.dicttoxml(self.fbjson, attr_type=False)
        elif self.fbjson != {}:
            xmlstring = dicttoxml.dicttoxml(self.fbjson, attr_type=False)
        else:
            raise ValueError("Either pass json or xml or SaveFace.fbjson must be populated with data")

        self._root = ET.fromstring(xmlstring)
        elements = []
        els = self._root.findall('image')
        for el in els:
            elements.push(el.find('src')[0])
        els = self._root.findall('full_picture')
        elements = elements + els
        self.__download_(elements)

    @BoundInnerClass 
    class DownloadThread(threading.Thread):
        """
            A bound inner thread class
            http://code.activestate.com/recipes/577070-bound-inner-classes/
        """
        def __init__(self, outer, queue):
            print(outer)
            super(outer.DownloadThread, self).__init__(self, outer)
            self._queue = queue
            self._destfolder = outer.args.imgfolder
            self.daemon = True
            self._outer = outer

        def run(self):
            """
                runs the threads
            """
            while True:
                el = self._queue.get()
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
            print "[%s] Downloading %s -> %s" % (self.ident, el.nodeValue, self._destfolder)
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
            t = self.DownloadThread(queue)
            t.start()

        queue.join()

# Print iterations progress
def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100):
    """
    Call in a loop to create terminal progress bar
    @params:
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
        default='images', help='Optional. The path to the images folder. Defaults to images', 
        dest='imgfolder')
    parser.add_argument('-p --pprint_options', metavar='pprint options', type=str, required=False, nargs='*',
        default='indent=4, width=80, depth=None, compact=False', help="Optional. Options string for pprint module.\n\
        Parameters must be named key=value with no comma ie indent=4 depth=80.",
        dest='pprint_opts')

    args = parser.parse_args()
    SF = SaveFace()
    SF.process_args(args)