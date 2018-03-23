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
import sys
from savefacexml import SaveFaceXML
from savefacehtml import SaveFaceHTML
from savefacejson import SaveFaceJSON
from savefaceformatter import SaveFaceFormatterHTML as sfmt
from savefaceformatter import htmlformat
import argparse
# below needs to be overloaded to do anything useful
# from argparse import RawTextHelpFormatter


def process_args(args):
    """
    Internal function used by script when standalone
    Args:
        args (dict): args from argparser
    No Longer Raises:
        ValueError: if O_Auth_tkn is not set
    """
    sf = None
    if args.format == 'xml':
        sf = SaveFaceXML()
    elif args.format == 'json':
        sf = SaveFaceJSON()
    elif args.format == 'pjson':
        __prepare_pprint_()
        sf = SaveFaceJSON(ispretty=True,
                          indent=args.pprint_opts['indent'],
                          width=args.pprint_opts['width'],
                          depth=args.pprint_opts['depth'])
    elif args.format == 'html':
        sf = SaveFaceHTML()

    if args.pickle_load_file is not None:
        sf.get_pages_from_pickle(args.pickle_load_file)
    elif args.O_Auth_tkn is not None:
        sf.init_graph(args.O_Auth_tkn)
        sf.get_pages_from_graph(request_string=args.request_string)
    else:
        sys.exit("check auth tkn is present")

    if args.format == 'html':
        sf.get_data_from_pages()
        sf.init_html(Formatter=sfmt, function=htmlformat)
    if args.pickle_save_file is not None:
        sf.save_pages_to_pickle(args.pickle_save_file)

    if args.stdout:
        print(str(sf))
    if args.filename is not None:
        sf.write(args.filename, args.filepath)

    # images
    # if self.args.images == True:
        # self.sf.get_images(result)
        # exchange the text in the url nodes from the node list
        # with local filepaths
        # TODO


def __prepare_pprint_(args):
    """
    prepares the pprint options string from the args
    Raises:
        ValueError: Description
    """
    SUPPORTED_TYPES = ['indent', 'width', 'depth']
    for a in args.pprint_opts:
        b = a.split('=')
        if b[0] not in SUPPORTED_TYPES:
            raise ValueError('Unsupported type "%s". Supported types are %s'
                             % (b[0], ', '.join(SUPPORTED_TYPES)))
        if b[1] != 'None':
            args.pprint_opts[b[0]] = int(b[1])
        else:
            args.pprint_opts[b[0]] = None

    if args.pprint_opts['indent'] is None:
        args.pprint_opts['indent'] = 4
    if args.pprint_opts['width'] is None:
        args.pprint_opts['width'] = 80
    if args.pprint_opts['depth'] is None:
        args.pprint_opts['depth'] = 20

defaultqstring = 'me?fields=posts.include_hidden(true) \
                 {created_time,from,message,comments \
                 {created_time,from,message,comments \
                 {created_time,from,message},attachment},full_picture}'

if __name__ == "__main__":
    # me?fields=id,name,posts.include_hidden(true){created_time,from,message,comments{created_time,from,message,comments{created_time,from,message},attachment},full_picture}
    parser = argparse.ArgumentParser(epilog="Saving Face with saveface.py",
                                     description="Download your facebook posts, \
                                                  comments,images etc.\n\
                                                  Default request \
                                                  string is :\n\
                                                  " + defaultqstring)
    parser.add_argument('-s', '--save',
                        metavar='the pickle filename',
                        type=str, required=False, nargs='?',
                        default=None, const="default_pickle",
                        help='Optional. Use pickle \'filename\' \
                              to store the array of pages. \
                              Defaults to sp_d_m_y-H:m:s \
                              (save time)',
                        dest='pickle_save_file')
    parser.add_argument('-g', '--getfrom',
                        metavar='the pickle file name',
                        type=str, required=False, nargs='?',
                        default=None, const='last',
                        help='Optional. Pickle filename.\n\
                              If no filename then last saved \
                              pickle is loaded. Fails if file is \
                              not present.\n',
                        dest='pickle_load_file')
    parser.add_argument('-a', '--auth_tkn',
                        metavar='facebook auth token',
                        type=str, required=False, nargs='?',
                        help='Optional. Your app\'s facebook \
                              authorisation token. Must be set \
                              to retrieve from facebook (see -g)',
                        dest='O_Auth_tkn')
    parser.add_argument('-r', '--request_string',
                        metavar='rest api request string',
                        type=str, required=False, nargs='?',
                        default=defaultqstring,
                        help='Optional. The request string \
                              to query facebook\'s api. \
                              Default request string above',
                        dest='request_string')
    parser.add_argument('-f', '--format',
                        metavar='output format for results',
                        type=str, required=False, nargs='?',
                        default='json', help='Optional. \
                                              Can be one of json, \
                                              pjson (prettyprinted), \
                                              xml or html. \
                                              Defaults to json',
                        choices=['json', 'pjson', 'xml', 'html'],
                        dest='format')
    parser.add_argument('-o', '--stdout',
                        metavar='output to stdout',
                        type=bool, required=False, nargs='?',
                        default=False, help='Optional. Output to stdout. \
                                             Defaults to False',
                        dest='stdout')
    parser.add_argument('-n', '--filename',
                        metavar='filename for the output',
                        type=str, required=False, nargs='?',
                        default=None, help='Optional. A filename for \
                                            the results. Results will \
                                            not be saved without \
                                            filename being specified',
                        dest="filename")
    parser.add_argument('-l', '--location',
                        metavar='filepath for the output',
                        type=str, required=False, nargs='?',
                        default='./', help='Optional. A filepath \
                                            for the results file. \
                                            Defaults to ./',
                        dest='filepath')
    parser.add_argument('-p', '--pprint_options',
                        metavar='pprint options',
                        type=str, required=False, nargs='*',
                        default='[indent=4, width=80, depth=None]',
                        help="Optional. Options for pprint module.\n\
                              key=value with comma ie -p [indent=4, depth=80]",
                        dest='pprint_opts')
    parser.add_argument('-i', '--images',
                        metavar='download images?',
                        type=bool, required=False, nargs='?',
                        default=False, help='Optional.  A boolean to indicate \
                                             whether or not to download \
                                             images. Defaults to False',
                        dest='images')
    parser.add_argument('-d', '--image_path',
                        metavar='path to images',
                        type=str, required=False, nargs='?',
                        default='images', help='Optional. The path to the \
                                                images folder.\
                                                Defaults to ./images',
                        dest='img_folder')
    parser.add_argument('-c', '--css',
                        metavar='css filename',
                        type=str, required=False, nargs='?',
                        default='saveface.css', help='Optional. The filename of the \
                                                css file.\
                                                Defaults to saveface.css',
                        dest='cssfile')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        print('\nYou need to supply some arguments...\n')
        sys.exit(1)

    process_args(parser.parse_args())


def htmlformat(xmlitems):
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
