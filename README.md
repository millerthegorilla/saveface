# saveface
python script to download facebook posts and comments etc using graph api through facepy

usage: saveface.py [-h] [-g [Where to source the pages from]] -a
                   [facebook auth token] [-r [rest api request string]]
                   [-f [output format for results]] [-o [output to stdout]]
                   [-s [pickle the array of pages]]
                   [-n [filename for the output]]
                   [-l [filepath for the output]]
                   [-p [pprint options [pprint options ...]]]
                   [-i [download images?]] [-d [path to images]]
                   [-c [css filename]]

Download facebook posts, comments,images etc. Default request string is :
me?fields=posts.include_hidden(true) {created_time,from,message,comments
{created_time,from,message,comments
{created_time,from,message},attachment},full_picture}

optional arguments:
  -h, --help            show this help message and exit
  -g [Where to source the pages from], --getfrom [Where to source the pages from]
                        Optional. Can be one of facebook or pickle. Defaults
                        to facebook
  -a [facebook auth token], --auth_tkn [facebook auth token]
                        Required. Your app's facebook authorisation token
  -r [rest api request string], --request_string [rest api request string]
                        Optional. The request string to query facebook's api.
                        Defaults to posts,comments,images
  -f [output format for results], --format [output format for results]
                        Optional. Can be one of json, pjson (prettyprinted),
                        xml or html. Defaults to json
  -o [output to stdout], --stdout [output to stdout]
                        Optional. Output to stdout. Defaults to False
  -s [pickle the array of pages], --save [pickle the array of pages]
                        Optional. Use Pickle to store the array of pages.
                        Defaults to False
  -n [filename for the output], --filename [filename for the output]
                        Optional. A filename for the results. Results will not
                        be saved without filename being specified
  -l [filepath for the output], --location [filepath for the output]
                        Optional. A filepath for the results file. Defaults to
                        ./
  -p [pprint options [pprint options ...]], --pprint_options [pprint options [pprint options ...]]
                        Optional. Options for pprint module. key=value with
                        comma ie -p [indent=4, depth=80]
  -i [download images?], --images [download images?]
                        Optional. A boolean to indicate whether or not to
                        download images. Defaults to False
  -d [path to images], --image_path [path to images]
                        Optional. The path to the images folder. Defaults to
                        ./images
  -c [css filename], --css [css filename]
                        Optional. The filename of the css file. Defaults to
                        saveface.css

Saving Face with saveface.py

Currently this will download json, xml, or html (which I'm in the process of styling).
The next step is a config file, which will include a templated html representation.
Eventually it will be able to make a local copy of images, referenced from
the xml file by relative file paths to the local copies.
