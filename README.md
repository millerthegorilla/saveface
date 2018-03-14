---


---

<h1 id="saveface.py"><a href="http://saveface.py">saveface.py</a></h1>
<hr>
<p>[pickle the array of pages]<br>
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
-i [download images?], --images [download images?]<br>
Optional. A boolean to indicate whether or not to<br>
download images. Defaults to False<br>
-d [path to images], --image_path [path to images]<br>
Optional. The path to the images folder. Defaults to<br>
./images<br>
-c [css filename], --css [css filename]<br>
Optional. The filename of the css file. Defaults to<br>
saveface.css</p>
<p>Saving Face with <a href="http://saveface.py">saveface.py</a></p>
<p>Currently this will download json, xml, or html (which I’m in the process of styling).<br>
The next step is a config file, which will include a templated html representation.<br>
Eventually it will be able to make a local copy of images, referenced from<br>
the xml file by relative file paths to the local copies.</p>

