import numpy as np
import cv2 
import os
from numpy import binary_repr

from zipfile import ZipFile

ZIPPED_SECRET_FILE_NAME = 'zippedSecret.zip'


def zipSecretFile(inputFile):
    # Remove the existing extension and add .zip
    base_name = os.path.splitext(inputFile)[0]
    zipName = base_name + ".zip"
    
    # Create the zip file
    with ZipFile(zipName, 'w') as zip:
        print("Zipping secret...")
        zip.write(inputFile, os.path.basename(inputFile))
        print("Zipping secret Done!")
    
    return zipName

def unzipSecretFile(file_name: str):
    with ZipFile(file_name, 'r') as zip:
        print("Unzipping secret...")
        zip.extractall() 
        print("Unzipping secret Done!")

