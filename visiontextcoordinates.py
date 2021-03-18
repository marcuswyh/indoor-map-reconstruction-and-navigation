import io
import os
import copy

# Imports the Google Cloud client library
from google.cloud import vision

#desktop
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:/Users/Marcus/AppData/Local/Google/Cloud SDK/apikey.json"

#laptop
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:/Users/DELL/AppData/Local/Google/Cloud SDK/apikey.json"



#=============================================================================================================

# to check if coordinates are inside a polygon
def inside(x,y,poly):

    n = len(poly)
    inside = False
    
    # p1 variable for first polygon vertice
    p1x,p1y = poly[0]
    
    for i in range(n+1):
        # p2 variable for next polygon vertice 
        p2x,p2y = poly[i % n]
        # if point is within y axis
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                # if point within max of x axis
                if x <= max(p1x,p2x):
                    # if not same y axis, calculate new x threshold
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    # if x is lesser than new x threshold, point is inside polygon
                    if p1x == p2x or x <= xints:
                        inside = not inside
                        
        # assign 2nd polygon vertice to p1 variable for future comparison with next vertice                
        p1x,p1y = p2x,p2y
    
    # return boolean
    return inside

#=======================================================================================

# to get the max y coordinate
def getYMax(data):
    v = data.text_annotations[0].bounding_poly.vertices
    yArray = []
    for i in range (0,4):
        yArray.append(v[i].y)
    
    return max(yArray)

#=======================================================================================

def invertAxis(data, yMax):
    data = fillMissingValues(data);
    for i in range (1, len(data.text_annotations)):
        v = data.text_annotations[i].bounding_poly.vertices
        
        for j in range (0,4):
            v[j].y = yMax - v[j].y
        
    return data

#=======================================================================================

def fillMissingValues(data):
    for i in range (1, len(data.text_annotations)):
        v = data.text_annotations[i].bounding_poly.vertices
        
        for vertex in v:
            if vertex.x == None:
                vertex.x = 0
            
            if vertex.y == None:
                vertex.y = 0
        
    return data

#=======================================================================================

def getBoundingPolygon(mergedArray):

    external = []
    for i in range (0, len(mergedArray)):
        arr = []

        # calculate merged text height (left and right)
        h1 = mergedArray[i].bounding_poly.vertices[0].y - mergedArray[i].bounding_poly.vertices[3].y
        h2 = mergedArray[i].bounding_poly.vertices[1].y - mergedArray[i].bounding_poly.vertices[2].y
        h = h1;
        # get larger height value
        if(h2> h1):
            h = h2
        # calculate height threshold for gradient purposes in future
        avgHeight = h * 0.6;
        
        # get coordinates for top line of merged text
        arr.append(mergedArray[i].bounding_poly.vertices[1])
        arr.append(mergedArray[i].bounding_poly.vertices[0])
        line1 = getRectangle(copy.deepcopy(arr), True, avgHeight, True)
        
        # get coordinates for bottom line of merged text
        arr = []
        arr.append(mergedArray[i].bounding_poly.vertices[2])
        arr.append(mergedArray[i].bounding_poly.vertices[3])
        line2 = getRectangle(copy.deepcopy(arr), True, avgHeight, False)
        
        # initialize array to store individual merged text bounding box info
        internal = []
        # insert big bounding box coordinates of merged text, index, empty array and matched line boolean
        internal.append(createRectCoordinates(line1, line2))
        internal.append(i)
        internal.append([])
        internal.append(False)
        
        # append individual merged array bounding box info
        external.append(internal)
    
    return external

#=======================================================================================

def combineBoundingPolygon(mergedArray, arr):
    # select one merged text from the array
    for i in range (0, len(mergedArray)):
        # get big bounding box coordinates
        bigBB = arr[i][0]

        # iterate through all the array to find the match
        for k in range (i, len(mergedArray)):
            # if its not own bounding box and has never been matched before
            if(k != i and arr[i][3] == False):
                insideCount = 0;
                
                # for each coordinate points of merged text
                for j in range (0,4):
                    coordinate = mergedArray[k].bounding_poly.vertices[j]
                    
                    # check if each coordinate point is inside big bounding box
                    if(inside(coordinate.x, coordinate.y, bigBB)):
                        # increment by 1 if true
                        insideCount += 1
           
                # if all four point were inside the big bb
                if(insideCount == 4):
                    # append match info dictionary into array and set matched status as true
                    # matchLineNum indicates the index of matched word in merged text array
                    match = {"matchCount": insideCount, "matchLineNum": k}
                    arr[i][2].append(match)
                    arr[i][3] = True

    return arr

#=======================================================================================

def getRectangle(v, isRoundValues, avgHeight, isAdd):
    if(isAdd):
        v[1].y = v[1].y + int(avgHeight)
        v[0].y = v[0].y + int(avgHeight)
    else:
        v[1].y = v[1].y - int(avgHeight)
        v[0].y = v[0].y - int(avgHeight)

    yDiff = (v[1].y - v[0].y)
    xDiff = (v[1].x - v[0].x)
    
    if xDiff != 0: 
        gradient = yDiff / xDiff
    else:
        gradient = 0

    xThreshMin = 1
    xThreshMax = 2000

    if (gradient == 0):
        #extend the line
        yMin = v[0].y
        yMax = v[0].y
    else:
        yMin = (v[0].y) - (gradient * (v[0].x - xThreshMin))
        yMax = (v[0].y) + (gradient * (xThreshMax - v[0].x))
    
    
    if(isRoundValues):
        yMin = int(yMin)
        yMax = int(yMax)
    
    return {"xMin" : xThreshMin, "xMax" : xThreshMax, "yMin": yMin, "yMax": yMax}

#=======================================================================================

def createRectCoordinates(line1, line2):
    return [[line1["xMin"], line1["yMin"]], [line1["xMax"], line1["yMax"]], [line2["xMax"], line2["yMax"]],[line2["xMin"], line2["yMin"]]]

#=============================================================================================================
    
    
def mergeNearByWords(data):

    yMax = getYMax(data)
    data = invertAxis(data, yMax)
    
    rawText = []

    # Auto identified and merged lines from gcp vision
    lines = data.text_annotations[0].description.split('\n')
    # gcp vision full text
    for data in data.text_annotations:
        rawText.append(data)
    
    #reverse to use lifo
    lines.reverse()
    rawText.reverse()
    #to remove the zeroth element which gives the total summary of the text
    rawText.pop()
    
    # returns array containing all merged nearby texts
    mergedArray = getMergedLines(lines, rawText)
    
    # returns array containing big bounding box info for each merged text
    arr = getBoundingPolygon(mergedArray)

    # returns array that contains words within big bounding boxes
    arr = combineBoundingPolygon(mergedArray, arr)

    #This returns final array containing all lines with shop name and lot number
    finalArray = constructLineWithBoundingPolygon(mergedArray, arr)
    
    return finalArray

#=======================================================================================

def constructLineWithBoundingPolygon(mergedArray, arr):
    finalArray = []
    
    # loop through all merged texts
    for i in range (0, len(mergedArray)):
        # only execute on matched words
        if(arr[i][3] == True):
            
            # if there is no matched info
            if(len(arr[i][2]) == 0):
                finalArray.append(mergedArray[i].description)
                print "xxxxxxxx"
            # append line containing shop name and lot number into array
            else:
                finalArray.append(arrangeWordsInOrder(mergedArray, i, arr))
    
    # return final array containing all lines with shop name and lot number
    return finalArray

#=======================================================================================

def getMergedLines(lines,rawText):

    mergedArray = []
    
    while(len(lines) != 1):
        
        l = lines.pop()
        l1 = copy.deepcopy(l)
        status = True

        while (True):
            wElement = rawText.pop()
            
            if(wElement == None):
                break;
            
            w = wElement.description

            try:
                index = l.index(w)
            except ValueError:
                index = -1
                continue

            
            #check if the word is inside
            l = l[index + len(w):]
            if(status):
                status = False
                #set starting coordinates
                mergedElement = wElement
            
            if(l == ""):
                #set ending coordinates
                mergedElement.description = l1
                mergedElement.bounding_poly.vertices[1].x = wElement.bounding_poly.vertices[1].x
                mergedElement.bounding_poly.vertices[1].y = wElement.bounding_poly.vertices[1].y
                mergedElement.bounding_poly.vertices[2].x = wElement.bounding_poly.vertices[2].x
                mergedElement.bounding_poly.vertices[2].y = wElement.bounding_poly.vertices[2].y
                mergedArray.append(mergedElement)
                
                break

    return mergedArray

#=======================================================================================

def arrangeWordsInOrder(mergedArray, k, arr):
    mergedLine = ''
    
    # get matched info of selected merged text
    line = arr[k][2]
    
    for i in range (0, len(line)):
        # get index of matched word
        index = line[i]["matchLineNum"]
        # get text info of matched word
        matchedWordForLine = mergedArray[index].description

        mainX = mergedArray[k].bounding_poly.vertices[0].x
        compareX = mergedArray[index].bounding_poly.vertices[0].x
        
        # if matched word is positioned after word in k position of mergeeArray
        if(compareX > mainX):
            mergedLine = mergedArray[k].description +':'+ matchedWordForLine
        else:
            mergedLine = matchedWordForLine + ':' + mergedArray[k].description
    
    # return final line that contains shop name and lot number
    return mergedLine


#=============================================================================================================

def receiveimg_directory_text(filename):
    # Instantiates a client
    client = vision.ImageAnnotatorClient()
    # The name of the image file to annotate
    file_name = os.path.join(
        os.path.dirname(__file__),
        filename)
    
    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()
    
    image = vision.types.Image(content=content)
    
    response = client.text_detection(image=image)
    
    result = mergeNearByWords(response)
    
    return result

#=======================================================================================

def receiveimg_map_text(filename):
    # Instantiates a client
    client = vision.ImageAnnotatorClient()
    # The name of the image file to annotate
    file_name = os.path.join(
        os.path.dirname(__file__),
        filename)
    
    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()
    
    image = vision.types.Image(content=content)
    
    response = client.text_detection(image=image)
    
    texts = response.text_annotations
    
    arr = []
    for text in texts:
        arr.append(text)
    
    return arr

#=======================================================================================
    
def return_directorydict():
    # get directory lot and shop name data
    directory_data = receiveimg_directory_text("dirtest.png")
    
    print ""
    print "info retrieved!"
    print ""
    
    # initialize dictionary to store lot and label
    directory_dict = {}
    
    # insert directory data into dictionary
    for x in range (len(directory_data)):
        a = directory_data[x]
        b = a.split(':')
        directory_dict[b[0]] = b[1]
        
    return directory_dict

#=======================================================================================

def return_maplabel():
    # get map label data and initialize array for the data
    map_data = receiveimg_map_text('maptest.png')
    maplabel = []
    
    # assigning map label into array
    for text in map_data:
        maplabel.append(text.description)
    
    return maplabel

#=======================================================================================