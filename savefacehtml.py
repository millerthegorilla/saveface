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
from savefacexml import SaveFaceXML
import io


class SaveFaceHTML(SaveFaceXML):

    def __init__(self, formatter=None):
        super().__init__(formatter)

    def get_pages_from_pickle(self, pickle_file):
        super().get_pages_from_pickle(pickle_file)

    def get_data_from_graph(self, graph=None, number_of_pages=None,
                            request_string=None, verbose=True):
        super().get_pages_from_graph(graph=graph,
                                     number_of_pages=number_of_pages,
                                     request_string=request_string,
                                     verbose=verbose)

    def get_data_from_pages(self):
        super().get_data_from_pages()

    def get_data_from_pickle(self):
        self.get_pages_from_pickle()
        self.get_data_from_pages()

    @property
    def html(self):
        return self.formatter.html

    # todo - add xml_declaration
    def write(self, filename, filepath, overwrite=True):
        """
            Writes data to file as xml
        Args:
            filename (str): name of file
            filepath (str): path to file
            overwrite(bool): whether to overwrite file
        """
        # super().write(filename, filepath, 'html', overwrite)
        with open(filepath + filename, 'w') as output:
            output.write(self.html)

    def __str__(self):
        return self.formatter.html
