from savefacexml import SaveFaceXML
from savefacehtml import SaveFaceHTML
from savefacejson import SaveFaceJSON

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

    if args.source == 'facebook':
        sf.init_graph(args.O_Auth_tkn)
        sf.get_posts_from_graph(request_string=args.request_string)
    elif args.source == 'pickle':
        sf.get_pages_from_pickle()

    if args.format == 'html':
        sf.get_posts_from_pages()
    if args.pickle:
        sf.save_pages_to_pickle()
    # if args.images:
    #     sf.get_images() args.img_folder

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
    parser.add_argument('-g', '--getfrom',
                        metavar='Where to source the pages from',
                        type=str, required=False, nargs='?',
                        default='facebook',
                        help='Optional. Can be one of facebook or pickle.\n\
                              Defaults to facebook\n',
                        choices=['facebook', 'pickle'],
                        dest='source')
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
    parser.add_argument('-s', '--save',
                        metavar='pickle the array of pages',
                        type=bool, required=False, nargs='?',
                        default=False, help='Optional. Use Pickle to store the array of pages. \
                                             Defaults to False',
                        dest='pickle')
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

    process_args(parser.parse_args())
