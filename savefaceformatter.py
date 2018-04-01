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
from xml.etree import ElementTree as ET
from abc import ABC, abstractmethod, abstractproperty
import re
import html5lib
from bs4 import BeautifulSoup as bs
import html
import ftfy
from time import sleep


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


default_json_template = u'{}'

default_xml_template = u'<?xml version="1.0" encoding="UTF-8" standalone="yes" ?><root>{}</root>'

default_html_template = u'<!doctype html>' + \
                        '<html lang=\'en\'>' + \
                        '<head>' + \
                        '<meta charset="utf-8"/>' + \
                        '<link rel="shortcut icon" href="./favicon.ico">' + \
                        '<link rel="stylesheet"' + \
                        'href="./saveface.css">' + \
                        '<title>SaveFacePie</title>' + \
                        '</head><body>{}' + \
                        '</body></html>'


class SaveFaceFormatterJSON(SaveFaceFormatter):
    def __init__(self, formatter_func=None):
        super().__init__(formatter_func)
        self._formatter_func = formatter_func
        self._json = ''
        self._template = default_json_template

    @property
    def template(self):
        return self._template.format(self._json)

    @template.setter
    def template(self, val):
        super().template = val
        self._template = val

    @property
    def json(self):
        return self._json

    def format(self, data):
        super().format(data)


class SaveFaceFormatterXML(SaveFaceFormatterJSON):
    def __init__(self, formatter_func=None):
        super().__init__(formatter_func)
        self._xml = ET.fromstring('<content><items></items></content>')
        self._template = default_xml_template

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, val):
        super().template = val

    @property
    def xml(self):
        return self._xml

    # @property
    # def xhtml(self):
    #    # return bs.prettify(self._template.format(ET.tostring(self._xml,
    #     #                                         encoding='unicode',
    #      #                                        method='html')))
    #     pass

    def format(self, data):
        super().format(data)
        rn = self._xml.find('.//items/.')
        if len(data):
            for item in data:
                items_rt = ET.XML('<item></item>')
                for el in item:
                    items_rt.append(el)
                    if el.tag == 'attachment':
                        self.media_proc(el)
                rn.append(items_rt)
        for el in rn.iter():
            if el.text:
                el.text = ftfy.fix_text_segment(el.text, fix_entities='auto', remove_terminal_escapes=True, fix_encoding=True, fix_latin_ligatures=True, fix_character_width=True, uncurl_quotes=True, fix_line_breaks=True, fix_surrogates=True, remove_control_chars=True, remove_bom=True, normalization='NFKC')
        if self._formatter_func is not None:
            self._xml = self._formatter_func(self._xml)

    def media_proc(self, item):
        pass

    def __str__(self):
        return self.template.format(bs(ET.tostring(self._xml, method='xml').decode(), 'html.parser').content.prettify())


# this can be subclassed for different request strings
class SaveFaceFormatterHTML(SaveFaceFormatterXML):
    def __init__(self, formatter_func=None):
        super().__init__(formatter_func)
        self._template = default_html_template

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, val):
        super().template = val

    @property
    def html(self):
        return self.__str__()

    def format(self, data):
        super().format(data)

    def __str__(self):
        return bs(self.template.format(ET.tostring(self._xml, method='html').decode()), 'html.parser').prettify()


def xmlformat(xmltree):

    if xmltree.findall('.//headers') is not None:
        p = xmltree.findall('.//headers/..')
        for e in p:
            e.remove(e.find('./headers'))

    if xmltree.findall('.//paging') is not None:
        p = xmltree.findall('.//paging/..')
        for e in p:
            e.remove(e.find('./paging'))

    return xmltree


def htmlformat(xmltree):
    # TODO replace all None checks with except
    # try:
    #     el = xmltree.findall('.//message')
    #     for e in el:
    #         e.text = e.text.replace('\n', u'<br>')
    # except AttributeError:   # find out what type of exception is thrown
    #     pass
    try:
        p = xmltree.findall('.//headers/..')
        for e in p:
            e.remove(e.find('./headers'))
    except AttributeError:
        pass
    try:
        p = xmltree.findall('.//paging/..')
        for e in p:
            e.remove(e.find('./paging'))
    except AttributeError:
        pass

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

    for i in xmltree.findall('.//items/.'):
        e = ET.Element('p', attrib={'class': 'posts-title'})
        inner = ET.Element('strong')
        inner.text = "Posts"
        e.append(inner)
        i.insert(0, e)

    for i in xmltree.findall('.//comments/.'):
        e = ET.Element('p', attrib={'class': 'comments-title'})
        inner = ET.Element('strong')
        inner.text = "Comments"
        e.append(inner)
        i.insert(0, e)

    if xmltree.findall('.//photos/.'):
        for i in xmltree.findall('.//picture/..'):
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
        for i in xmltree.findall('.//photos/data/item'):
            i.tag = 'photo'

    for i in xmltree.findall('.//item/comment/id/.'):
        e = ET.Element('p', attrib={'class': 'comment-id'})
        e.text = 'comment id : ' + i.text
        i.append(e)
        i.text = None

    for i in xmltree.findall('.//item/id/.'):
        e = ET.Element('p', attrib={'class': 'post-id'})
        e.text = 'post id : ' + i.text
        i.append(e)
        i.text = None

    # p = xmltree.findall('.//picture')
    # fp = xmltree.findall('.//full_picture')
    # fpp = p + fp
    # for el in fpp:
    #     el.insert(0, ET.Element('img', attrib={'class': 'image',
    #                                            'src': el.text}))
    #     el.text = None

    for el in xmltree.findall('.//created_time'):
        el.tag = 'a'
        el.attrib = {'class': 'created_time', 'name': el.text}

    for el in xmltree.iter():
        if el.tag not in ['img', 'p', 'a']:
            el.attrib = {'class': el.tag, **el.attrib}
            el.tag = 'div'

    return xmltree


def re_cdata(x):
    return '<![CDATA[' + x.group(0) + ']]>'


def re_remove_control_characters(m):
    return "".join(ch for ch in m.group(0) if unicodedata.category(ch)[0] != "C")


def containsAny(seq, aset):
    for item in filter(aset.__contains__, seq):
        return True
    return False
