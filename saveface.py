#! /usr/bin/python
from Queue import Queue
import argparse
import json
import os
from pprint import pprint
import sys
import threading
import urllib
import xmlrpclib

from facepy import GraphAPI
import requests
from xml.etree import ElementTree


parser = argparse.ArgumentParser(description='Download facebook posts,comments,and images')
parser.add_argument('-a --auth_tkn', metavar='facebook auth token', type=str, required=True, nargs='?', 
					help='Required. Your app\'s facebook authorisation token', dest='O_Auth_tkn')
parser.add_argument('-r --request', metavar='rest api request string', type=str, required=False, nargs='?',
					default='me?fields=id,name,posts.include_hidden(true){created_time,from,message,comments{created_time,from,message,comments{created_time,from,message},attachment},full_picture}',
					help='Optional. The request string to query facebook\'s api', dest='req')

args = parser.parse_args()

graph = GraphAPI(args.O_Auth_tkn)

p_json = graph.get(args.req)
str = p_json['posts']
p_json = {}

numofpages = 0
elements = []
els = []
imagenum = 0
lock = threading.Lock()

while(True):
	try:
		str = requests.get(str.pop('paging')['next']).json()
		numofpages = numofpages + 1

		if 'next' in str['paging']:
			pjson.update(str)
	except Exception as inst:
		print(type(inst))
		print(inst.args)
		print(inst)
		break

xmlstring = ElementTree.XML(p_json)
elements = xmlstring.findall('image')
for el in elements:
	els.push(el.find('src')[0])

elements = xmlstring.findall('full_picture')
els = els + elements

download(els, "images" if sys.argv[2] is None else sys.argv[2])
#change url for path
for tup in DownloadThread.imgpath_el:
	tup[1].text = tup[0]

##serialize xmlobject .... todo

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
			except Exception,e:
				print "   Error: %s"%e
			self.queue.task_done()

	def download_url(self, el):
		# change it to a different way if you require
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

def download(elements, destfolder, numthreads=4):
	queue = Queue()
	for el in elements:
		queue.put(el)

	for i in range(numthreads):
		t = DownloadThread(queue, destfolder)
		t.start()

	queue.join()
