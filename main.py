import visiontextcoordinates as vision
import perspective as p
import routing as route
import cv2

size = 4    #variable for image size


#============================================================================
#                            MAIN PROGRAM
#============================================================================

# begin processing phase of map and directory images
p.initialize_images()

# obtain a dictionary of directory labels and lots
directory_dict = vision.return_directorydict()

# obtain an array of map labels
map_data = vision.receiveimg_map_text("maptest.png")
    
print "Finished processing map and directory!"
print ""
print"number of lots retrieved: ", len(directory_dict)

#print ""
#for label in directory_dict:
#    print label, "-", directory_dict[label]

startflag = True
endflag = True
resume = True

# loops till user decides to quit
while (resume):
    
    print ""
    for label in directory_dict:
        print label, "-", directory_dict[label]

    # prompts user to input starting location
    while (startflag):
        count = 0
        start_loc = raw_input("Please input your starting location (nearest shop to you): ")
        for x in range(len(map_data)):
            count +=1
            
            # compares map label values and dictionary key values
            # if match, stores matching map label coordinates
            if map_data[x].description == directory_dict.get(start_loc):
                print "Found starting location!"
                print ""
                startflag = False
                startx = map_data[x].bounding_poly.vertices[0].x
                starty = map_data[x].bounding_poly.vertices[0].y
                break
            
            if count == len(map_data):
                print "Starting location not found, please try again."
           
    #prompts user to input destination goal        
    while (endflag):
        count = 0
        end_loc = raw_input("Please input your intended destination: ")
        for x in range(len(map_data)):
            count+=1
            
            # compares map label values and dictionary key values
            # if match, stores matching map label coordinates
            # then, inserts start and goal coordinates to obtain route
            if map_data[x].description == directory_dict.get(end_loc):
                print "Found destination!"
                print ""
                endflag = False
                endx = map_data[x].bounding_poly.vertices[0].x
                endy = map_data[x].bounding_poly.vertices[0].y
                
                # returns and plots route between supplied coordinates in an output image
                route.return_route(startx, starty, endx, endy)
                
                # read image to obtain dimensions
                dimensions = cv2.imread("route.png",0)  
                w,h = dimensions.shape
                
                # enlarge image
                m_img = cv2.imread("route.png")  
                m_img = cv2.resize(m_img, (int(h*size),int(w*size)), interpolation = cv2.INTER_CUBIC)
                
                # label starting and goal destination
                cv2.putText(m_img,"Start", (startx,starty), cv2.FONT_HERSHEY_SIMPLEX, 1, 255,3)
                cv2.putText(m_img,"Goal", (endx,endy), cv2.FONT_HERSHEY_SIMPLEX, 1, 255,3)
                
                # saves result image
                cv2.imwrite("route.png", m_img)
                
                # displays route image
                cv2.namedWindow('Result', cv2.WINDOW_NORMAL)
                temp = cv2.imread("route.png")
                cv2.imshow('Result', temp)
                cv2.waitKey()
                cv2.destroyAllWindows()
                break
            
            if count == len(map_data):
                print "Destination not found, please try again"
                
    # allows user to run navigation search again or quit program
    again = raw_input("Do you wish to continue? (Y/N): ")
    resumestatus = True
    
    # if yes, the whole while loop will execute once more
    # if no, exits loop and program ends
    while (resumestatus):
        if (again == "Y" or again == "y"):
            resumestatus = False
            startflag = True
            endflag = True
            #break
        
        elif (again == "N" or again == "n"):
            resumestatus = False
            resume = False
        
        # prompts user input again if invalid
        else:
            print "Invalid input, please try again"
            again = raw_input("Do you wish to continue? (Y/N): ")
        

print ""
print "==================="
print "      BYE BYE"
print "==================="

