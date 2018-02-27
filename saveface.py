#! /usr/bin/python
from Queue import Queue
import argparse
import os
from pprint import pprint
import sys
import threading
import urllib

from facepy import GraphAPI
from facepy import exceptions as fpexceptions
import requests
import dicttoxml
from xml.etree import ElementTree as ET


from boundinnerclasses import BoundInnerClass


class DownloadThread(threading.Thread):
        #static variables
        imgidx = 0
        imgpath_el = []

        def __init__(self, queue, destfolder):
            super(DownloadThread, self).__init__()
            self.queue = queue
            self.destfolder = destfolder
            self.daemon = True

        def run(self):
            while True:
                el = self.queue.get()
                try:
                    self.download_url(el)
                except Exception as e:
                    print "   Error: %s"%e
                self.queue.task_done()

        def download_url(self, el):
            print "[%s] Downloading %s -> %s"%(self.ident, el.nodeValue, dest)
            try:
                img = urllib.FancyURLopener(el.nextSibling.nodeValue, dest)
                imgtype = ret.info().getsubtype()
                DownloadThread.imgidx += 1
                name = str(DownloadThread.imgidx) + '.' + imgtype
                buf = img.read()
                name = name.split('/')[-1]
                dest = os.path.join(self.destfolder, name)
                DownloadThread.imgpath_el.push((dest,el))
                downloaded_image = file(dest, "wb")
                downloaded_image.write(buf)
                downloaded_image.close()
                img.close()
            except (urllib.ContentTooShortError, IOError) as inst:
                print(type(inst))
                print(inst.args)
                print(inst)

class SaveFace:

    def __init__(self):
        self.numofpages = 0
        self.fbjson = {}

    def __process_args_(self, args):
        if args.O_Auth_tkn:
            self.get_from_graph(args.O_Auth_tkn)
        else:
            raise ValueError("O_Auth_tkn must be set")

        if self.args.format == 'xml':
            result = dicttoxml.dicttoxml(self.fbjson, attr_type=False)
        elif self.args.format == 'pjson':
            result = pprint.pformat(self.fbjson, self.args.pprint_opts)
        else:
            result = self.fbjson

        if self.args.output_type == 'stdout':
            sys.stdout(result)
        else:
            self.filename = self.args.output_type
            self.__write_(result)

        if self.args.images == True:
            self.get_images()

    def get_from_graph(self, O_Auth_tkn = None):
        if O_Auth_tkn is not None:
            graph = GraphAPI(O_Auth_tkn)
        else:
            raise ValueError("O_Auth_tkn must be present")

        try:
            myjson = graph.get(self.args.request)
            while(True):
                posts = requests.get(myjson.pop('paging')['next']).json()
                self.numofpages = self.numofpages + 1
                if 'next' in self.posts['paging']:
                    myjson.update(posts)
        except fpexceptions.OAuthError as inst:
            print(type(inst))
            print(inst.args)
            print(inst)
            break
        self.fbjson = myjson

    def __write_(self):
        if self.args.output_type is not "stdout":
            with open(self.args.output_type, "w") as f:
                f.write(self.results)

    def get_images(self):
        xmlstring = dicttoxml.dicttoxml(self.fbjson, attr_type=False)
        root = ET.fromstring(xmlstring)
        els = root.findall('image')
        elements = []
        for el in els:
            elements.push(el.find('src')[0])
        els = xmlstring.findall('full_picture')
        elements = elements + els
        self.__download_(elements)
    
    #change url for path
    for tup in DownloadThread.imgpath_el:
        tup[1].text = tup[0]

    ##serialize xmlobject .... todo

    def __download_(self, destfolder, numthreads=4):
        queue = Queue()
        for el in self.elements:
            queue.put(el)

        for i in range(numthreads):
            t = DownloadThread(queue, destfolder)
            t.start()

        queue.join()

if __name__ == "__main__":
    defaultqstring = "me?fields=id,name,posts.include_hidden(true)" \
                     "{created_time,from,message,comments" \
                     "{created_time,from,message,comments" \
                     "{created_time,from,message},attachment},full_picture}"
    
    parser = argparse.ArgumentParser(description="Download facebook posts,comments,and images. \n"
        "Default request string is :\n" + defaultqstring)
    
    parser.add_argument('-a --auth_tkn', metavar='facebook auth token', type=str, required=True, nargs='?', 
        help='Required. Your app\'s facebook authorisation token', 
        dest='O_Auth_tkn')
    parser.add_argument('-r --request_string', metavar='rest api requestuest string', type=str, required=False, nargs='?',
        default=defaultqstring, 
        help='Optional. The request string to query facebook\'s api. Defaults to posts,comments,images',
        dest='request')
    parser.add_argument('-f --format', metavar='output format for results', type=str, required=False, nargs='?',
        default='json', help='Optional. Can be one of json, pjson (prettyprinted) or xml. Defaults to json', 
        choices=['json', 'pjson', 'xml'], 
        dest='output_type')
    parser.add_argument('-o --output_type', metavar='how to output the results', type=str, required=False, nargs='?',
        default='stdout', help='Optional. Accepts a string filename. Defaults to stdout', 
        dest='output_type')
    parser.add_argument('-i --images', metavar='download images?',  type=bool, required=False, nargs='?',
        default=False, help='Optional.  A boolean to indicate whether or not to download images', 
        dest='bimages')
    parser.add_argument('-d --image_path', metavar='path to images', type=str, required=False, nargs='?',
        default='images', help='Optional. The path to the images folder. Defaults to images', 
        dest='imgfolder')
    parser.add_argument('-p --pprint_options', metavar='pprint options', type=str, required=False, nargs='?',
        default='indent=4, width=80, depth=None, *, compact=False', help="Optional. Options string for pprint module. /n" \
        "Defaults to: 'indent=1, width=80, depth=None, *, compact=False'",
        dest='pprint_opts')

    args = parser.parse_args()
    SF = SaveFace()
    SF.process_args(args)
