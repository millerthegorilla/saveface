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
from savefacejson import SaveFaceJSON
from xml.etree import ElementTree as ET  # should have used lxml
import html5lib
from dicttoxml import dicttoxml
# from bs4 import BeautifulSoup as bs
import re
import html
import time
import gc
import unicodedata
import itertools
from collections.abc import Sequence


# class ControlCodes(Sequence):
#     def __init__():
        
#     def index(self, value, start, stop):
#         return 

class SaveFaceXML(SaveFaceJSON):

    def __init__(self, formatter=None):
        super().__init__(formatter=None)
        self.formatter = formatter
        self.xml_data = []

    def get_pages_from_graph(self, number_of_pages=None, verbose=True):
        super().get_pages_from_graph(number_of_pages,
                                     verbose)

    def get_pages_from_pickle(self, pickle_file):
        super().get_pages_from_pickle(pickle_file)

    def get_data_from_pages(self):
        super().get_data_from_pages()

        def repl_func(x):
            return '<![CDATA[' + x.group(0) + ']]>'

        def remove_control_characters(m):
            return "".join(ch for ch in m.group(0) if unicodedata.category(ch)[0] != "C")

        def containsAny(seq, aset):
            for item in itertools.ifilter(aset.__contains__, seq):
                return True
            return False

        for data in self.json_data:
            try:
                el = html5lib.parse(dicttoxml(data,
                                              attr_type=False,
                                              custom_root='item',
                                              root=False).decode(self.encoding),
                                    namespaceHTMLElements=False)
                self.xml_data.append(el)
                el = None
                try:
                    for m in self.xml_data[-1].findall('.//message/.'):
                        m.text = html.unescape(m.text)
                        # control codes
                        m.text = re.sub(r'[\x00-\x19]',  # [\x7F]',
                                        remove_control_characters,
                                        m.text)
                        # dud elements
                        if '<' in m.text:
                            m.text = re.sub(r'(<.*>)',
                                            repl_func,
                                            m.text,
                                            flags=re.IGNORECASE)

                    self.print_progress(len(self.xml_data), len(self.json_data), 'Constructing XML...')
                except (TypeError, KeyError, Exception) as e:
                    self.log(msg=e, level='info', std_out=False, to_disk=True)
                    pass
            except (ET.ParseError, AttributeError) as e:
                print(e)
                pass
        self.json_data = None
        gc.collect()

    @property
    def xml(self):
        return self.formatter.xml

    def write(self, filename, filepath, overwrite=True):
        """
            Writes data to file as xml
        Args:
            results (str): string to write
            type (str): Either 'json' or 'xml'
        """
        super().write(filename, filepath, overwrite)
        try:
            with open(filename, 'w') as output:
                output.write(self.formatter.template)
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

    def indent(self, elem, level=0):
        time.sleep(0.001)
        gc.collect()
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def __str__(self):
        return self.indent(self.formatter.template, 8)
