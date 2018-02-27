#! /usr/bin/python
# This Python file uses the following encoding: utf-8
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
    def __init__(self):
        self.num_pages = 0
        self.num_images = 0
        self.images_total = 0
        self.fbjson = {}
        self.imgpath_element = []
        self.args = {}
        self._compact = False
        self._indent = 4
        self._depth = None
        self._width = 80
        self.O_Auth_tkn = None

    def process_args(self, args):
        self.args = args
        if self.args.O_Auth_tkn:
            self.get_from_graph(self.args.O_Auth_tkn)
        else:
            raise ValueError("O_Auth_tkn must be set")

        if self.args.format == 'xml':
            result = dicttoxml.dicttoxml(self.fbjson, attr_type=False)
        elif self.args.format == 'pjson':
            self.__prepare_pprint_()
            result = pprint.pformat(self.fbjson, indent=self._indent,
                width=self._width, depth=self._depth) #compact is not yet instantiated compact=self._compact)
        else:
            result = self.fbjson

        if self.args.images == True:
            self.get_images()
            #self._root

        if self.args.output_type == 'stdout':
            print(result)
        else:
            self.filename = self.args.output_type
            self.__write_(result)

    def __prepare_pprint_(self):
        for j in self.args.pprint_opts.split(','):
            j = j.split('=')
            if j[0] == 'compact':
                try:
                    self._compact = bool(j[1])
                except:
                    self._compact = False
                    pass
            if j[0] == 'indent':
                try:
                    self._indent = int(j[1])
                except:
                    self._indent = 4
                    pass
            if j[0] == 'width':
                try:
                    self._width = int(j[1])
                except:
                    self._width = 80
                    pass
            if j[0] == 'depth':
                try:
                    self._depth = int(j[1])
                except:
                    self._depth = None
                    pass

    def get_from_graph(self, O_Auth_tkn = None):
        if O_Auth_tkn is not None:
            self.O_Auth_tkn = O_Auth_tkn

        if self.O_Auth_tkn is not None:
            try:
                graph = GraphAPI(O_Auth_tkn)
            except fpexceptions.OAuthError as e:
                print(type(e))
                print(e.args)
                print(e)
        else:
            raise ValueError("O_Auth_tkn must be present")

        try:
            myjson = graph.get(self.args.request)['posts']
            sys.stdout.write("getting posts from %s\n" % (myjson['data'][-1]['created_time']))
            while(True):
                posts = requests.get(myjson.pop('paging')['next']).json()
                self.num_pages = self.num_pages + 1
                if len(posts['data']):
                    sys.stdout.write("getting posts from %s\n" % (posts['data'][-1]['created_time']))
                    myjson = dict(myjson, **posts)
                else:
                    break
        except (fpexceptions.OAuthError, KeyError) as e:
                print(type(e))
                print(e.args)
                print(e)

        print("received %s pages" % (self.num_pages))
        self.fbjson = myjson

    def __write_(self):
        if self.args.output_type is not "stdout":
            with open(self.args.output_type, "w") as f:
                f.write(self.results)

    def get_images(self):
        xmlstring = dicttoxml.dicttoxml(self.fbjson, attr_type=False)
        self._root = ET.fromstring(xmlstring)
        els = self._root.findall('image')
        elements = []
        for el in els:
            elements.push(el.find('src')[0])
        els = xmlstring.findall('full_picture')
        elements = elements + els
        self.__download_(elements)

    @BoundInnerClass #http://code.activestate.com/recipes/577070-bound-inner-classes/
    class DownloadThread(threading.Thread):
        def __init__(self, outer, queue, destfolder):
            super(outer.DownloadThread, self).__init__()
            self.queue = queue
            self.destfolder = destfolder
            self.daemon = True
            self.outer = outer

        def run(self):
            while True:
                el = self.queue.get()
                try:
                    self.download_img(el)
                except Exception as e:
                    print(type(e))
                    print(e.args)
                    print(e)
                self.queue.task_done()

        def download_img(self, outer, el):
            print "[%s] Downloading %s -> %s" % (self.ident, el.nodeValue, self.destfolder)
            try:
                img = urllib.FancyURLopener(el.nextSibling.nodeValue, self.destfolder)
                imgtype = img.info().getsubtype()
                name = str(outer.num_images) + '.' + imgtype
                buf = img.read()
                name = name.split('/')[-1]
                dest = os.path.join(self.destfolder, name)
                outer.imgpath_element.push((self.destfolder, el))
                downloaded_image = file(dest, "wb")
                downloaded_image.write(buf)
                downloaded_image.close()
                outer.num_images += 1
                print_progress(outer.num_images, outer.images_total)
                img.close()
            except (urllib.ContentTooShortError, IOError) as e:
                print(type(e))
                print(e.args)
                print(e)    

    def __download_(self, destfolder, numthreads=4):
        queue = Queue()
        for el in self.elements:
            queue.put(el)

        self.images_total = len(self.elements)

        for i in range(numthreads):
            t = self.DownloadThread(queue, destfolder)
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
    
    parser = argparse.ArgumentParser(description="Download facebook posts,comments,images etc.\n\
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
    parser.add_argument('-o --output_type', metavar='how to output the results', type=str, required=False, nargs='?',
        default='stdout', help='Optional. Accepts a string filename. Defaults to stdout', 
        dest='output_type')
    parser.add_argument('-i --images', metavar='download images?',  type=bool, required=False, nargs='?',
        default=False, help='Optional.  A boolean to indicate whether or not to download images. Defaults to false', 
        dest='images')
    parser.add_argument('-d --image_path', metavar='path to images', type=str, required=False, nargs='?',
        default='images', help='Optional. The path to the images folder. Defaults to images', 
        dest='imgfolder')
    parser.add_argument('-p --pprint_options', metavar='pprint options', type=str, required=False, nargs='*',
        default='indent=4, width=80, depth=None, compact=False', help="Optional. Options string for pprint module.\n\
        Parameters must be named key=value ie indent=4.\n\
        Defaults to: 'indent=4, width=80, depth=None, compact=False'",
        dest='pprint_opts')

    args = parser.parse_args()
    SF = SaveFace()
    SF.process_args(args)
