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
import pprint
import json
from saveface import SaveFace


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