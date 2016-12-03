# Siglator

Installation.
1. Download and Install Python 3.x + (Version 3.5.2 download: https://www.python.org/downloads/release/python-352/).
  1.1. Select all the Optional Features during install (pip, tk, etc..).
  1.2. Make sure Python is added to the PATH variable.
  1.3. Check if Python is installed: Run "python -V" from CMD.
    1.3.1. Send me a message.
  1.4. Check if pip is installed: Run "pip -V" from CMD.
    1.4.1. If the following message appears: 'command "pip" not found' you have to install pip manually.
    1.4.2. Download pip manually from here: https://bootstrap.pypa.io/get-pip.py and save it to a folder.
    1.4.3. Open CMD (as Administrator) in the same folder in which you saved "get-pip.py".
    1.4.4. Then from CMD run the following: "python get-pip.py".
    1.4.5. Check again if pip is installed: "pip -V".
    1.4.6. Update pip to the latest version: "python -m pip install -U pip".
2. Get the external dependenices for the script to work.
  2.1. Open CMD (anywhere) as Administrator.
  2.2. Get Pillow (image library): "pip install Pillow". 
  2.3. Get Color-Thief: "pip install colorthief". 
  
Usage:

1. Select the folder which contains the images. Press "Choose a folder" button.
2. Select the logo to be applied on all images. Press "Choose a logo" button.
3. Select whether to "Preview" or "Save" the images. Default is "Preview".
3. Apply the logo. Press "Add Logo" button.
