# PhotoFrame
Photo Frame Plugin for Indigo
By Bert Martin

Moved to: https://github.com/IndigoDomotics/PhotoFrame

This is a simple plugin that randomly grabs a single photo from a directory, and copies 
it to a directory.  It is designed to be used to create a photo frame as part of a 
control page.

Photo Frame requires the Python Image Library module to be installed.  To install 
run the following from the terminal: 

		'sudo pip install Pillow' .

Plugin Configuration:
---------------------
There is no configuration for the plugin itself.


Device Configuration:
---------------------
Picture Directory:  The directory where the pictures are retrieved from.  Current Photo 
Frame will only work with JPG images.

Destination Directory:  Where the picture is copied to.  The default is: 

/Library/Application Support/Perceptive Automation/Indigo 7/IndigoWebServer/photoalbum/album.jpg

Group Photos: If this is checked, Photo Frame will display 10 photos from a similar time frame.  
It will grab a random photo followed by the next nine images based on their file date.

Actions:
---------------------
Toggle Photo Frame: This will toggle pausing the photo.