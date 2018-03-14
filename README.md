---


---

<h1 id="saveface.py"><a href="http://saveface.py">saveface.py</a></h1>
<p>python script to download facebook posts and comments etc using graph api through facepy</p>
<p>usage: python <a href="http://saveface.py">saveface.py</a> [-h] [-g [Where to source the pages from]] -a<br>
[facebook auth token] [-r [rest api request string]]<br>
[-f [output format for results]] [-o [output to stdout]]<br>
[-s [pickle the array of pages]]<br>
[-n [filename for the output]]<br>
[-l [filepath for the output]]<br>
[-p [pprint options [pprint options …]]]<br>
[-i [download images?]] [-d [path to images]]<br>
[-c [css filename]]</p>
<p>Download facebook posts, comments,images etc. Default request string is :<br>
me?fields=posts.include_hidden(true) {created_time,from,message,comments<br>
{created_time,from,message,comments<br>
{created_time,from,message},attachment},full_picture}</p>
<p>optional arguments:<br>
-h, --help            show this help message and exit<br>
-g [Where to source the pages from], --getfrom [Where to source the pages from]<br>
Optional. Can be one of facebook or pickle. Defaults<br>
to facebook<br>
-a [facebook auth token], --auth_tkn [facebook auth token]<br>
Required. Your app’s facebook authorisation token<br>
-r [rest api request string], --request_string [rest api request string]<br>
Optional. The request string to query facebook’s api.<br>
Defaults to posts,comments,images<br>
-f [output format for results], --format [output format for results]<br>
Optional. Can be one of json, pjson (prettyprinted),<br>
xml or html. Defaults to json<br>
-o [output to stdout], --stdout [output to stdout]<br>
Optional. Output to stdout. Defaults to False<br>
-s [pickle the array of pages], --save [pickle the array of pages]<br>
Optional. Use Pickle to store the array of pages.<br>
Defaults to False<br>
-n [filename for the output], --filename [filename for the output]<br>
Optional. A filename for the results. Results will not<br>
be saved without filename being specified<br>
-l [filepath for the output], --location [filepath for the output]<br>
Optional. A filepath for the results file. Defaults to<br>
./<br>
-p [pprint options [pprint options …]], --pprint_options [pprint options [pprint options …]]<br>
Optional. Options for pprint module. key=value with<br>
comma ie -p [indent=4, depth=80]<br>
-i [download images?], --images [download images?]  Optional. <br>
	 A boolean to indicate whether or not to download images. Defaults to False<br>
-d [path to images], --image_path [path to images]     Optional. <br>
    The path to the images folder. Defaults to ./images<br>
-c [css filename], --css [css filename] Optional.<br>
    The filename of the css file. Defaults to saveface.css</p>
<p>Saving Face with <a href="http://github.com/millerthegorilla/saveface.py">saveface.py</a></p>
<p>Currently this will download json, xml, or html (which I’m in the process of styling).<br>
The next step is a config file, which will include a templated html representation.<br>
Eventually it will be able to make a local copy of images, referenced from<br>
the xml file by relative file paths to the local copies.</p>

<!--stackedit_data:
eyJoaXN0b3J5IjpbLTEzOTU1ODIyOTJdfQ==
-->