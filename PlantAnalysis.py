import cv2
import matplotlib.pyplot as plt
import numpy as np

def analyze_file(filepath):
  img = cv2.imread(filepath)
  img=np.array(img,dtype='float64')
  print(len(img))
  #Declare the three 0 matrices, and put the R,G, and B values of the picture into the three matrices.
  b = np.zeros((img.shape[0],img.shape[1]), dtype=img.dtype)
  g = np.zeros((img.shape[0],img.shape[1]), dtype=img.dtype)
  r = np.zeros((img.shape[0],img.shape[1]), dtype=img.dtype)
  b[:,:] = img[:,:,0]
  g[:,:] = img[:,:,1]
  r[:,:] = img[:,:,2]
  #A formula for generating grayscale images
  new=2*g-r-b
  w=new.min()
  e=new.max()
  new=new-w
  new=new/e*255
  new=np.array(new,dtype='uint8')

  ret2, th2 = cv2.threshold(new, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
  #Check the threshold of Otsu filtering method
  print("threshold of Otsu filtering:",ret2)
  # Otsu filtering's results are replicated to hole
  hole=th2.copy()
  #Find the hole and fill it
  cv2.floodFill(hole,None,(0,0),255) 
  hole=cv2.bitwise_not(hole)
  filledEdgesOut=cv2.bitwise_or(th2,hole)

  kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
  #image of corrosion
  eroded = cv2.erode(filledEdgesOut,kernel)
  #-------------------------------------------------------------------------------

  #Eliminate connected region
  #-------------------------------------------------------------------------------
  def baweraopen(image,size):
      output=image.copy()
      nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(image)
      for i in range(1,nlabels-1):
          regions_size=stats[i,4]
          if regions_size<size:
              x0=stats[i,0]
              y0=stats[i,1]
              x1=stats[i,0]+stats[i,2]
              y1=stats[i,1]+stats[i,3]
              for row in range(y0,y1):
                  for col in range(x0,x1):
                      if labels[row,col]==i:
                          output[row,col]=0
      return output
  im2=baweraopen(eroded,180)#200 is the size of the connected region to be eliminated.
  #---------------------------------------------------------------------------------

  # Count the number of pixels in the plant
  #---------------------------------------------------------------------------------
  print("number of pixels in the plant:",len(im2.nonzero()[0]))
  #distance is 50
  distance_top=50
  Area=(pow((0.000122*(distance_top-0.304)/0.304),2)*len(im2.nonzero()[0]))
  print("leaf area:",round(Area, 2))
  #---------------------------------------------------------------------------------

  #show the new image.
  #---------------------------------------------------------------------------------
  img[:,:,0]=im2*r
  img[:,:,1]=im2*g
  img[:,:,2]=im2*b

  img = (img * 255).astype(np.uint8)
  # plt.imshow(img)
  # plt.show()

  count_matrix = np.empty([len(img), len(img[0])])
  count_matrix.shape

  print(len(img), len(img[0]))


  def dfs_count(orig_matrix, count_matrix, x, y, current_group_id):
    if (x < 0 or y < 0 or x >= len(count_matrix) or y >= len(count_matrix[0])):
      return 0
    if (count_matrix[x][y] != 0 or orig_matrix[x][y].sum() == 0):
      count_matrix[x][y] = -1
      return 0
    else:
      count_matrix[x][y] = current_group_id
      count = 1
      for x_delta in [-1, 0, 1]:
        for y_delta in [-1, 0, 1]:
          if (x_delta == 0 and y_delta == 0):
            continue
          count += dfs_count(orig_matrix, count_matrix, x + x_delta, y + y_delta, current_group_id)
      return count

  def dfs_count_stack(orig_matrix, count_matrix, orig_x, orig_y, current_group_id):
    stack = []
    stack.append((orig_x, orig_y))
    count = 0
    pos_x = 0
    pos_y = 0
    while (len(stack) > 0):
      next_x, next_y = stack.pop()
      if (next_x < 0 or next_y < 0 or next_x >= len(orig_matrix) or next_y >= len(orig_matrix[0])
          or count_matrix[next_x][next_y] != 0):
        continue
      elif (orig_matrix[next_x][next_y].sum() == 0):
        count_matrix[next_x][next_y] = -1
        continue
      else:
        count += 1
        pos_x += next_x
        pos_y += next_y
        count_matrix[next_x][next_y] = current_group_id
        for x_delta in [-1, 0, 1]:
          for y_delta in [-1, 0, 1]:
            if (x_delta == 0 and y_delta == 0):
              continue
            stack.append((next_x + x_delta, next_y + y_delta))
    return (count, (pos_x / count if count != 0 else 0, pos_y / count if count != 0 else 0))

  count_matrix = np.empty([len(img), len(img[0])])
  groups = []
  for i in range(len(img)):
    for j in range(len(img[0])):
      group_size, center = dfs_count_stack(img, count_matrix, i, j, len(groups) + 1)
      if (group_size > 0):
        print(f"Group {len(groups) + 1} of size: {group_size} at location {center}")
        groups.append((group_size, center))

  # plt.imshow(count_matrix)
  # plt.show()

  def distance(elem1, elem2):
    return (elem1[0] - elem2[0])**2 + (elem1[1] - elem2[1])**2

  # Locations of centers, index is the plant id
  locations = [(140, 150), (110, 400), (100, 600), (380, 360), (420, 130), (360, 565)]
  plant_size_measurements = []

  if (len(groups) < 6):
    return None
  for location in locations:
    closest_group = groups[0]
    for candidate_group in groups:
      if (distance(closest_group[1], location) > distance(candidate_group[1], location)):
        closest_group = candidate_group
    plant_size_measurements.append(closest_group)

  # If multiple ones have same location, then it means they merged, do not use
  return plant_size_measurements