import numpy as np
import cv2 
import os
from numpy import binary_repr
import shutil
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
        print(zipName)
        print("Zipping secret Done!")
    return zipName

def unzipSecretFile(file_name: str):
    # Determine the extraction path based on the zip file name
    extract_path = os.path.splitext(file_name)[0]
    
    # Create the extraction directory if it doesn't exist
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)
    
    # Unzip the contents into the extraction directory
    with ZipFile(file_name, 'r') as zip:
        print("Unzipping secret...")
        print(file_name)
        zip.extractall(extract_path)
        print("Unzipping secret Done!")
        
    # Move the contents of the extraction directory to the parent directory
    first_file = None
    for item in os.listdir(extract_path):
        source = os.path.join(extract_path, item)
        destination = os.path.join(os.path.dirname(extract_path), item)
        
        if os.path.exists(destination):
            if os.path.isdir(destination):
                shutil.rmtree(destination)
            else:
                os.remove(destination)

        shutil.move(source, destination)
        first_file = destination  # Since there's only one file, this will be it
    
    # Delete the extraction directory
    shutil.rmtree(extract_path)
    
    print("unzipped")
    return first_file
