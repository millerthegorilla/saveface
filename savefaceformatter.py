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

from xml.etree import ElementTree as ET  # should have used lxml
from abc import ABC, abstractmethod


# this is how I will implement the class at
# some point in the future
# but for the momemt I intent to move on to some thing else
# and I have a working version in the git history
# https://www.python.org/dev/peps/pep-3119
class SaveFaceFormatterABC(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def format(self, xml):
        if xml is None:
            raise ValueError(self.__class__.__name__ +
                             '.format must be passed xml object')

    @property
    def template(self):
        pass

    @template.setter
    @abstractmethod
    def template(self, val):
        pass

    @property
    @abstractmethod
    def html(self):
        pass




def htmlwrap(element_list, wrapper_element, tags):
    for element in element_list:
        wrap_element = ET.Element(wrapper_element.tag,
                                  wrapper_element.attrib)
        for el in list(element):
            if el.tag in tags:
                element.remove(el)
                wrap_element.append(el)
        element.append(wrap_element)

default_html_template = u'<!doctype html>' + \
                        '<html>' + \
                        '<head>' + \
                        '<link rel="shortcut icon" href="./favicon.ico">' + \
                        '<link rel="stylesheet"' + \
                        'href="./saveface.css">' + \
                        '<title>SaveFacePie</title>' + \
                        '</head><body>{}' + \
                        '</body></html>'


# this can be subclassed for different request strings
class SaveFaceFormatterHTML(SaveFaceFormatterABC):
    def __init__(self):
        super().__init__()
        self._xhtml = None
        self._template = default_html_template
        self._html = ''

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, val):
        self._template = val

    @property
    def html(self):
        return self._html

    def format(self, xml):
        super().format(xml)
        self._xhtml = ET.fromstring("<content></content>")
        # convert xml to _xhtml
        if len(xml):
            for p in xml:
                self._xhtml.append(p)
                m = p.find('./message')
                if m is not None:
                    m.text = m.text.replace('\n', u'<br>')

        # format _xhtml
        if self._xhtml.findall('.//headers') is not None:
            p = self._xhtml.findall('.//headers/..')
            for e in p:
                e.remove(e.find('./headers'))

        if self._xhtml.findall('.//paging') is not None:
            p = self._xhtml.findall('.//paging/..')
            for e in p:
                e.remove(e.find('./paging'))

        for i in self._xhtml.findall('.//attachment/.'):
            if i.find('./media') is not None:
                i.remove(i.find('./media'))
            j = i.find('url')
            if j is not None and j.text is not None:
                if i.find('./title') is not None:
                    title = i.find('./title').text
                else:
                    title = "iframe"
                e = ET.Element('iframe', attrib={'src': j.text,
                                                 'title': title,
                                                 'class': 'iframe',
                                                 'sandbox': ''})

                e.text = "iframe  :  " + j.text
                i.remove(j)
                i.append(e)
                if i.find('./target') is not None:
                    i.remove(i.find('./target'))
            else:
                j = i.find('target')
                if j is not None and j.text is not None:
                    if i.find('./title') is not None:
                        title = i.find('./title').text
                    else:
                        title = "iframe"
                    e = ET.Element('iframe', attrib={'src': j.text,
                                                     'title': title,
                                                     'class': iframe,
                                                     'sandbox': ''})
                    e.text = "iframe  :  " + j.text
                    i.remove(j)
                    i.append(e)
                    if i.find('./url') is not None:
                        title = i.find('./url')
                    else:
                        title = "iframe"

        for i in self._xhtml.findall('.//posts/.'):
            e = ET.Element('p', attrib={'class': 'posts-title'})
            e.text = '<strong>Posts</strong>'
            i.insert(0, e)

        for i in self._xhtml.findall('.//comments/.'):
            e = ET.Element('p', attrib={'class': 'comments-title'})
            e.text = '<strong>Comments</strong>'
            i.insert(0, e)

        if self._xhtml.findall('.//photos/.'):
            for i in self._xhtml.findall('.//picture/..'):
                pid = i.find('./id')
                if pid.text is not None:
                    a = ET.Element('a',
                                   attrib={'class': 'photo-link',
                                           'href': 'https://www.facebook.com/photo.php?fbid=' +
                                           pid.text,
                                           'name': pid.text})
                    a.text = 'picture id : ' + pid.text
                    pid.insert(0, a)
                    pid.text = None
                    pid.tag = 'photo-id'
            for i in self._xhtml.findall('.//photos/data/item'):
                i.tag = 'photo'

        for i in self._xhtml.findall('.//item/id/.'):
            e = ET.Element('p', attrib={'class': 'comment-id'})
            e.text = 'comment id : ' + i.text
            i.append(e)
            i.text = None

        for i in self._xhtml.findall('.//post/id/.'):
            e = ET.Element('p', attrib={'class': 'post-id'})
            e.text = 'post id : ' + i.text
            i.append(e)
            i.text = None

        p = self._xhtml.findall('.//picture')
        fp = self._xhtml.findall('.//full_picture')
        fpp = p + fp
        for el in fpp:
            el.insert(0, ET.Element('img', attrib={'class': 'image',
                                                   'src': el.text}))
            el.text = None

        for el in self._xhtml.findall('.//created_time'):
            el.tag = 'a'
            el.attrib = {'class': 'created_time', 'name': el.text}

        for el in self._xhtml.iter():
            if el.tag not in ['img', 'p', 'a']:
                el.attrib = {'class': el.tag, **el.attrib}
                el.tag = 'div'

        self._xhtml.tag = 'content'
        htmlstring = ET.tostring(self._xhtml,
                                 encoding='unicode',
                                 method='html')

        self._html = self.template.format(htmlstring)
