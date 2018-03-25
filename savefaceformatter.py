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
from abc import ABC, abstractmethod, abstractproperty
from bs4 import BeautifulSoup as bs
from xmljson import yahoo as yh


# https://www.python.org/dev/peps/pep-3119
class SaveFaceFormatter(ABC):
    def __init__(self, formatter_func=None):
        pass

    @abstractmethod
    def format(self, data):
        if data is None:
            raise ValueError(self.__class__.__name__ +
                             '.format must be passed xml object')

    @property
    def template(self):
        pass

    @template.setter
    def template(self, val):
        pass


def htmlwrap(element_list, wrapper_element, tags):
    # helper function
    for element in element_list:
        wrap_element = ET.Element(wrapper_element.tag,
                                  wrapper_element.attrib)
        for el in list(element):
            if el.tag in tags:
                element.remove(el)
                wrap_element.append(el)
        element.append(wrap_element)


default_json_template = u''

default_xml_template = u'<root>{}</root>'

default_html_template = u'<!doctype html>' + \
                        '<html>' + \
                        '<head>' + \
                        '<link rel="shortcut icon" href="./favicon.ico">' + \
                        '<link rel="stylesheet"' + \
                        'href="./saveface.css">' + \
                        '<title>SaveFacePie</title>' + \
                        '</head><body>{}' + \
                        '</body></html>'


class SaveFaceFormatterJSON(SaveFaceFormatter):
    def __init__(self, formatter_func=None):
        super().__init__(formatter_func=None)
        self._formatter_func = formatter_func
        self._json = ''
        self._template = default_json_template

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, val):
        super().template = val
        self._template = val

    @property
    def xml(self):
        return self._template.format(ET.tostring(self._xml,
                                                 encoding='unicode',
                                                 method='xml'))

    @xml.setter
    def xml(self, val):
        super().xml = val
        self._xml = val

    def format(self, data):
        super().format(data)


class SaveFaceFormatterXML(SaveFaceFormatterJSON):
    def __init__(self, formatter_func=None):
        super().__init__(formatter_func=None)
        self._formatter_func = formatter_func
        self._xml = ET.fromstring('<?xml version="1.0" encoding="UTF-8"?><content></content>')
        self._template = default_xml_template

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, val):
        super().template = val
        self._template = val

    @property
    def xml(self):
        return self._template.format(ET.tostring(self._xml,
                                                 encoding='unicode',
                                                 method='xml'))

    @xml.setter
    def xml(self, val):
        super().xml = val
        self._xml = val

    def format(self, data):
        super().format(data)
        if len(data):
            for p in data:
                    for el in p:
                        self._xml.append(el)
                        m = el.find('./message')
                        if m is not None and m.text is not None:
                            m.text = m.text.replace('\n', u'<br>')
        if xmlfunction is not None:
            self._xml = xmlfunction(self._xml)


# this can be subclassed for different request strings
class SaveFaceFormatterHTML(SaveFaceFormatterXML):
    def __init__(self):
        super().__init__(formatter_func=None)
        self._html = ET.fromstring("<content></content>")
        self._template = default_html_template

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, val):
        super().template = val
        self._template = val

    @property
    def html(self):
        return self._template.format(ET.tostring(self._html,
                                                 encoding='unicode',
                                                 method='html'))

    @html.setter
    def xhtml(self, val):
        super().html = val
        self._html = val

    def format(self, data):
        super().format(xmlitems, xmlfunction)


def htmlformat(xmlitems):
    # format _xhtml
    if xmlitems.findall('.//headers') is not None:
        p = xmlitems.findall('.//headers/..')
        for e in p:
            e.remove(e.find('./headers'))

    if xmlitems.findall('.//paging') is not None:
        p = xmlitems.findall('.//paging/..')
        for e in p:
            e.remove(e.find('./paging'))

    for i in xmlitems.findall('.//attachment/.'):
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

    for i in xmlitems.findall('.//posts/.'):
        e = ET.Element('p', attrib={'class': 'posts-title'})
        e.text = '<strong>Posts</strong>'
        i.insert(0, e)

    for i in xmlitems.findall('.//comments/.'):
        import pdb; pdb.set_trace()  # breakpoint 2448c19b //
        e = ET.Element('p', attrib={'class': 'comments-title'})
        e.text = '<strong>Comments</strong>'
        i.insert(0, e)

    if xmlitems.findall('.//photos/.'):
        for i in xmlitems.findall('.//picture/..'):
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
        for i in xmlitems.findall('.//photos/data/item'):
            i.tag = 'photo'

    for i in xmlitems.findall('.//item/id/.'):
        e = ET.Element('p', attrib={'class': 'comment-id'})
        e.text = 'comment id : ' + i.text
        i.append(e)
        i.text = None

    for i in xmlitems.findall('.//post/id/.'):
        e = ET.Element('p', attrib={'class': 'post-id'})
        e.text = 'post id : ' + i.text
        i.append(e)
        i.text = None

    p = xmlitems.findall('.//picture')
    fp = xmlitems.findall('.//full_picture')
    fpp = p + fp
    for el in fpp:
        el.insert(0, ET.Element('img', attrib={'class': 'image',
                                               'src': el.text}))
        el.text = None

    for el in xmlitems.findall('.//created_time'):
        el.tag = 'a'
        el.attrib = {'class': 'created_time', 'name': el.text}

    for el in xmlitems.iter():
        if el.tag not in ['img', 'p', 'a']:
            el.attrib = {'class': el.tag, **el.attrib}
            el.tag = 'div'

    return xmlitems
