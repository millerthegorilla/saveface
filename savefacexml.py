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
from savefacejson import SaveFaceJSON
from xml.etree import ElementTree as ET  # should have used lxml
import html5lib
from dicttoxml import dicttoxml
import re
import unicodedata
import gc
import html
import time
import io


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
            for item in filter(aset.__contains__, seq):
                return True
            return False

        for data in self.json_data:
            try:
                el = html5lib.parseFragment(dicttoxml(data,
                                            attr_type=False,
                                            custom_root='item',
                                            root=False),
                                            namespaceHTMLElements=False)
                self.xml_data.append(el)
                el = None
                try:
                    for m in self.xml_data[-1].findall('.//message/.'):
                        if 'â€™' in m.text:
                            m.text = m.text.encode('windows-1252', errors='xmlcharrefreplace').decode('windows-1252', errors='xmlcharrefreplace')
                        m.text = m.text.encode('utf-8', errors='xmlcharrefreplace').decode()
                        #m.text = html.escape(m.text)
                        # m.text = re.sub(r'[\x00-\x19]![\x09-\x15]',  # [\x7F]',
                        #                 remove_control_characters,
                        #                 m.text)
                        # control codes
                        # dud elements
                        # if '<' in m.text:
                        #     m.text = re.sub(r'(<.*>)',
                        #                     repl_func,
                        #                     m.text,
                        #                     flags=re.IGNORECASE)
                    time.sleep(0.05)
                except (TypeError, KeyError) as e:
                    self.log(msg=e, level='info', std_out=False, to_disk=True)

            except (ET.ParseError, AttributeError) as e:
                print(e)

            self.print_progress(len(self.xml_data), len(self.json_data), 'Constructing XML...')
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
                output.write(str(self.formatter))
                # ET.ElementTree(self.xml).write(output,
                #                                encoding="unicode",
                #                                xml_declaration=None,
                #                                default_namespace=None,
                #                                method="xml",
                #                                short_empty_elements=False)
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

    def __str__(self):
        return str(self.formatter)
