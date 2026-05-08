from sys import argv
import os
import shutil
from PIL import Image
from PIL.ExifTags import TAGS


#-------------------/
##
## USAGE: Enter your Photos folder in the photosPath below.
#         Run the Program by writing python3 followed by the folder path you want to sort
##        and optionaly add a second argument "r" after that to go through every subfolder
#         aswell.
#-------------------/



#Constants -------------------/
#Hardcoded photo target path //ENTER YOUR OWN PATH
photosPath = "/Users/timo/Pictures"
months = ["1_Jan", "2_Feb", "3_Mar", "4_Apr", "5_May", "6_Jun", "7_Jul", "8_Aug", "9_Sep", "10_Okt", "11_Nov", "12_Dec"]

#Edit here to add suffixes
imageSuffixes = (".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG")

#TODO
editingSuffixes = (".afphoto")
rawSuffixes = ("CR2", "cr2", "DNG", "dng", "RAW", "raw")

#Get the Files from the Directory -------------------/

#Get folder path with photos to sort
userDir = argv[1]
#If user types r at the end the program will go through every subfolder of the specified directory
recursiveFlag = argv[2] if len(argv) >= 3 else 0


#Functions -------------------/

#Returns all file paths that are nested in @rootDirPath
def getFilePathsRecursivly(rootDirPath):
   res = []
   for root, dirs, files in os.walk(rootDirPath):
      for filename in files:
         res.append(os.path.join(root, filename))
   return res

#Returns all file paths in @rootDir
def getFilePathsSingle(rootdirPath):
   res = []
   entries = os.scandir(rootdirPath)
   for e in entries:
      if(e.is_file()):
         res.append(e.path)
   return res

#Adds a number to the end of the name until the name is free
# @targetPath: Specifies the directory in wich the duplicate should be searched
# @newName: The name calculated by the programm
def handleDuplicateNames(targetPath, newName):
   i=1
   newName = newName.split(".", 1)
   while(os.path.exists(os.path.join(targetPath, newName[0] + " " + str(i) + "." + newName[1]))):
      i+=1
   return(newName[0] + " " + str(i) + "." + newName[1])


#Handles the sorting logic for one file
# @rootDirPath: target folder
def handleFile(unsortedDir, filePath):
    
    #Validation -------------------/
    #Sort out non-image files
    if(not filePath.endswith(imageSuffixes)): 
       return
    
   #Getting image meta data -------------------/

    #Path to the current image
    imagePath = filePath

    targetPath = ""
    newName = ""

   #Gives Images a new name using the timestamp in the meta data
    #Get the date from meta data
    image = Image.open(imagePath)
    exifdata = image.getexif()
    date = exifdata.get(306)

    if(not date):
       print("WARNING: No date found at " + imagePath)
       return

    #Formatting Values -------------------/

    #Formated values
    date = date.split(" ")
    time = date[1]
    date = date[0].split(":")
    year = date[0]
    month = months[int(date[1])-1]
    day = date[2]

    #Generates a new Name for the file with the pattern: DAY HR/MIN/SEC
    newName = day + " " + time + "." + imagePath.split(".")[-1]


    #Target path with the correct attributes
    targetPath = os.path.join(photosPath, year, month)

   #If file is already at the correct position with the correct name function returns
    if(imagePath == os.path.join(targetPath, newName)): return()
      
    #Handle Duplicates in target directory
    if(os.path.exists(os.path.join(targetPath, newName))): 
       newName = handleDuplicateNames(targetPath=targetPath, newName=newName)

    #Handles Duplicates in the starting directory
    if(os.path.exists(os.path.join(unsortedDir, newName)) and imagePath != os.path.join(unsortedDir, newName)):
       newName = handleDuplicateNames(targetPath=unsortedDir,newName=newName)



    #Rename file
    os.rename(imagePath, os.path.join(unsortedDir, newName))
    print(os.path.join(unsortedDir, newName))

   #If the file is in the correct folder with the wrong name the function will cancel after renaming
    if(unsortedDir == targetPath): return()

    #Create new folders if needed
    if not os.path.exists(targetPath):
      os.makedirs(targetPath)
      print("Directory created successfully!")

    #Moving the renamed image file to the new location
    dest = shutil.move(os.path.join(unsortedDir, newName), targetPath) 
    print(dest)



#Main -------------------/

#Choose right function
filePaths = []
if(recursiveFlag == "r"):
   filePaths = getFilePathsRecursivly(userDir)
else:
   filePaths = getFilePathsSingle(userDir)


for entry in filePaths:
   handleFile(unsortedDir=userDir, filePath=entry)