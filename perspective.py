import cv2
import numpy as np

#==========================================================================

def selectCoord(event, x, y, flags, param):
    global coo, i   

    if event == cv2.EVENT_LBUTTONDBLCLK:   
        coo.append((x,y))
        i = i + 1

#==========================================================================
        
def arrayreturn(pts):
    
    temp_rect = np.zeros((4,2), dtype = "float32")
    
    s = np.sum(pts, axis = 2)

    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]

    diff = np.diff(pts, axis = -1)
    tr = pts[np.argmin(diff)]
    bl = pts[np.argmax(diff)]
    
    temp_rect[0] = tl
    temp_rect[1] = tr
    temp_rect[2] = br
    temp_rect[3] = bl
    
    return temp_rect

#==========================================================================

def autoprocess(filename):

    k = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    
    mapimg = cv2.imread(filename,1)
    
    mapgray = cv2.cvtColor(mapimg,cv2.COLOR_BGR2GRAY)
    mapthresh = cv2.adaptiveThreshold(mapgray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
                cv2.THRESH_BINARY,7,7)
    
    
    width, height = mapthresh.shape
    
    mapsharp = cv2.filter2D(mapthresh, -1, k)  
    mapinvert = cv2.bitwise_not(mapsharp)  
    mapdilate = cv2.dilate(mapinvert, cv2.getStructuringElement(cv2.MORPH_RECT,(3,3)), iterations = 3)  
    mapclose = cv2.morphologyEx(mapdilate, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT,(4,4)), iterations = 1)
    
    _,cnts,hier = cv2.findContours(mapclose,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    

    cnts = sorted(cnts, key=cv2.contourArea,reverse=True)
    
    for i in range (0, len(cnts)):
        
        if i != 0:
            continue
           
        x,y,w,h = cv2.boundingRect(cnts[i])
        hull = cv2.convexHull(cnts[i])
        peri = cv2.arcLength(hull,True)
        approx = cv2.approxPolyDP(hull,0.001*peri,True)
        pts = np.float32(approx)  
        
        
        src = arrayreturn(pts)
        dst = np.array([[int(w*0.05),int(h*0.05)],[w+int(w*0.05),int(h*0.05)],[w+int(w*0.05),h-int(h*0.05)],[int(w*0.05), h-int(h*0.05)]], np.float32)
        
        M = cv2.getPerspectiveTransform(src,dst)
        warp = cv2.warpPerspective(mapimg, M, (int(w*1.1),int(h*1.2)))
        
        cv2.imwrite("maptestcolor.png", warp)
        
        warp = cv2.cvtColor(warp,cv2.COLOR_BGR2GRAY)
        warp = cv2.adaptiveThreshold(warp,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
                cv2.THRESH_BINARY,11,11)
        
        return warp

#==========================================================================    

def manualprocess(filename):
    k = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    
    mapimg = cv2.imread(filename,1)
    
    mapgray = cv2.cvtColor(mapimg,cv2.COLOR_BGR2GRAY)
    mapthresh = cv2.adaptiveThreshold(mapgray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
                cv2.THRESH_BINARY,7,7)
    
    
    width, height = mapthresh.shape
    
    mapsharp = cv2.filter2D(mapthresh, -1, k)
    mapinvert = cv2.bitwise_not(mapsharp)
    mapdilate = cv2.dilate(mapinvert, cv2.getStructuringElement(cv2.MORPH_RECT,(3,3)), iterations = 3)
    mapclose = cv2.morphologyEx(mapdilate, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT,(4,4)), iterations = 1)
    
    print ""
    print('Double click to select 4 quadrangle points on the image in a clock-wise manner')
    
    cv2.namedWindow('Image',cv2.WINDOW_NORMAL)
    cv2.setMouseCallback('Image', selectCoord)

    while(i < 4):    
        cv2.imshow('Image', mapimg)
        cv2.waitKey(1)   
        
    cv2.destroyWindow('Image')
    
    
    _,cnts,hier = cv2.findContours(mapclose,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        
    cnts = sorted(cnts, key=cv2.contourArea,reverse=True)
    
    
    for x in range (0, len(cnts)):
        
        if x != 0:
            continue
           
        x,y,w,h = cv2.boundingRect(cnts[x])
    
    dst = np.array([[0,0],[w-1,0],[w-1,h-1],[0, h-1]], np.float32)
   
    tl = coo[0]
    tr = coo[1]
    bl = coo[3]
    br = coo[2]
    
    
    pts = np.float32([[tl], [tr], [br], [bl]])
    
    
    M = cv2.getPerspectiveTransform(pts,dst)
    warp = cv2.warpPerspective(mapimg, M, (w,h))
    
    cv2.imwrite("maptestcolor.png", warp)
    
    warp = cv2.cvtColor(warp,cv2.COLOR_BGR2GRAY)
    warp = cv2.adaptiveThreshold(warp,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
            cv2.THRESH_BINARY,11,11)
    
    cv2.imwrite("maptest.png", warp)
    return warp
    
#==========================================================================

def manualprocessdirect(filename):
    global i, coo
    i=0
    coo= []
    
    mapimg = cv2.imread(filename,1)
    
    mapgray = cv2.cvtColor(mapimg,cv2.COLOR_BGR2GRAY)
    mapthresh = cv2.adaptiveThreshold(mapgray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
                cv2.THRESH_BINARY,7,7)
    
    
    width, height = mapthresh.shape
    
    print ""
    print('Double click to select 4 quadrangle points on the image in a clock-wise manner')
    
    cv2.namedWindow('Image',cv2.WINDOW_NORMAL)
    cv2.setMouseCallback('Image', selectCoord)

    while(i < 4):    
        cv2.imshow('Image', mapimg)
        cv2.waitKey(1)   
        
    cv2.destroyWindow('Image')
   
    tl = coo[0]
    tr = coo[1]
    bl = coo[3]
    br = coo[2]
    
    pts = np.float32([[tl], [tr], [br], [bl]])
    
    x,y,w,h = cv2.boundingRect(pts)
    
    
    dst = np.array([[0,0],[w-1,0],[w-1,h-1],[0, h-1]], np.float32)
    
    
    M = cv2.getPerspectiveTransform(pts,dst)
    warp = cv2.warpPerspective(mapimg, M, (w,h))
    warp = cv2.cvtColor(warp,cv2.COLOR_BGR2GRAY)
    warp = cv2.adaptiveThreshold(warp,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
            cv2.THRESH_BINARY,11,11)
    
    cv2.imwrite("dirtest.png", warp)
    return warp

#==========================================================================
    
def prompt_processmap(map_filename):
    flag = True
    global i, coo
    i = 0
    coo = []
    
    print ""
    print "1. Automatic processing"
    print "2. Manual processing"
    mapinput = raw_input("Choose map image processing method: ")
    
    while (flag):
        if mapinput == "1":
            m = autoprocess(map_filename)
            cv2.imwrite("maptest.png", m)
            flag = False
        elif mapinput == "2":
            m = manualprocess(map_filename)
            flag = False
        else:
            print "Invalid input. Try again"
            
        if (mapinput != "1" and mapinput != "2"):
            print ""
            print "1. Automatic processing"
            print "2. Manual processing"
            mapinput = raw_input("Choose map image processing method: ")
    
    print "Map image processed!"    
    return m
    

#==========================================================================

def confirm_satisfaction(processedmap, mapname):
    flag = True
    
    cv2.namedWindow('Processed map output',cv2.WINDOW_NORMAL)
    cv2.imshow('Processed map output', processedmap)
    cv2.waitKey()
    cv2.destroyAllWindows()
    userinput = raw_input("Are you satisfied with the processed map image? (Y/N):")
    
    while (flag):
        if (userinput=="Y" or userinput=="y"):
            flag = False
            
        elif (userinput=="N" or userinput=="n"):
            proc_map = prompt_processmap(mapname)
            cv2.namedWindow('Processed map output',cv2.WINDOW_NORMAL)
            cv2.imshow('Processed map output', proc_map)
            cv2.waitKey()
            cv2.destroyAllWindows()
            userinput = raw_input("Are you satisfied with the processed map image? (Y/N):")
            
        else:
            print "Invalid input. Try again."
            userinput = raw_input("Are you satisfied with the processed map image? (Y/N):")
            
#==========================================================================

def confirm_satisfaction_dir(processed_dir, dirname):
    flag = True
    
    cv2.namedWindow('Processed directory output',cv2.WINDOW_NORMAL)
    cv2.imshow('Processed directory output', processed_dir)
    cv2.waitKey()
    cv2.destroyAllWindows()
    userinput = raw_input("Are you satisfied with the processed directory image? (Y/N):")
    
    while (flag):
        if (userinput=="Y" or userinput=="y"):
            flag = False
            
        elif (userinput=="N" or userinput=="n"):
            proc_dir = manualprocessdirect(dirname)
            cv2.namedWindow('Processed directory output',cv2.WINDOW_NORMAL)
            cv2.imshow('Processed directory output', proc_dir)
            cv2.waitKey()
            cv2.destroyAllWindows()
            userinput = raw_input("Are you satisfied with the processed directory image? (Y/N):")
        else:
            print "Invalid input. Try again."
            userinput = raw_input("Are you satisfied with the processed directory image? (Y/N):")
            
#==========================================================================

def initialize_images():
    
    # users to input directory and map image 
    map_filename = raw_input("Please insert map image file name: ")
    direct_filename = raw_input("Please insert directory image file name: ")
    
    # allow users to choose map processing style
    processedmap = prompt_processmap(map_filename)
    # to allow users to re-do map correction if unsatisfactory
    confirm_satisfaction(processedmap, map_filename)
    
    
    # manual processing of directory image
    processed_dir = manualprocessdirect(direct_filename)
    # to allow users to re-do directory correction if unsatisfactory
    confirm_satisfaction_dir(processed_dir, direct_filename)


#==========================================================================

# initialize global variables i and coo as 0    
i=0
coo = []

  