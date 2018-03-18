from savefacexml import SaveFaceXML
from bs4 import BeautifulSoup as bs


class SaveFaceHTML(SaveFaceXML):

    def __init__(self):
        super().__init__()
        self.html = ''

    def get_pages_from_pickle(self):
        super().get_pages_from_pickle()
        self.__format_()
        return self.pages

    def get_posts_from_graph(self, graph=None, number_of_pages=None,
                             request_string=None, verbose=True):
        super().get_pages_from_graph(graph=graph,
                                     number_of_pages=number_of_pages,
                                     request_string=request_string,
                                     verbose=verbose)
        self.get_posts_from_pages()
        return self.posts

    def get_posts_from_pages(self):
        super().get_posts_from_pages()
        self.__format_()
        return self.posts

    def get_posts_from_pickle(self):
        self.get_pages_from_pickle()
        self.get_posts_from_pages()
        return self.posts

    def get_html(self, cssfile='saveface.css'):

        self.xhtml.tag = 'content'
        htmlstring = ET.tostring(self.xhtml,
                                 encoding='unicode',
                                 method='html')

        self.html = u'<!doctype html>' + \
                    '<html>' + \
                    '<head>' + \
                    '<link rel="shortcut icon" href="./favicon.ico">' + \
                    '<link rel="stylesheet"' + \
                    'href="' + cssfile + '">' + \
                    '<title>SaveFacePie</title>' + \
                    '</head><body>' + \
                    htmlstring + \
                    '</body></html>'

    def htmlwrap(element_list, wrapper_element, tags):
        for element in element_list:
            wrap_element = ET.Element(wrapper_element.tag,
                                      wrapper_element.attrib)
            for el in list(element):
                if el.tag in tags:
                    element.remove(el)
                    wrap_element.append(el)
            element.append(wrap_element)

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
            output.write(bs(self.html, "html.parser").prettify(formatter=None))

    def __str__(self):
        return bs(self.html, "html.parser").prettify()
