import numpy as np
import cv2
import matplotlib.pyplot as plt
from copy import deepcopy
from collections import defaultdict
import math

GAUSSIAN_BLUR_SIZE = 3
GAUSSIAN_BLUR_COUNT = 1
BLOCKSIZE = 7
C = 2

MIN_CONTOUR_SIZE = 100
MIN_RECTANGULARITY = 0.5

# Classes
class Contour():
    def __init__(self, contour):
        self.contour = contour
        self.area = cv2.contourArea(contour)
        self.x, self.y, self.w, self.h = cv2.boundingRect(contour)
        self.rectangularity = self.area/(self.w*self.h)

class GridSquare():
    def __init__(self, x_min, x_max, y_min, y_max, grid_x, grid_y, full_image):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.width = x_max-x_min
        self.height = y_max-y_min
        self.image = deepcopy(full_image[y_min:y_max, x_min:x_max])
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.brightness = np.mean(self.gray)/255
        self.type = None #SquareType

    def __repr__(self):
        return f"{self.x_min, self.x_max}, {self.y_min, self.y_max}"

    def display(self):
        display_image(self.image)

def get_grid_from_image(img):
    cropped_image = crop_image_to_crossword_outline(img)
    
    contours = detect_contours(cropped_image)
    clusters = range_clustering(contours)
    selected_contours = clusters[0]
    
    grid = create_grid_from_contours(selected_contours, cropped_image)
    return grid

def crop_image_to_crossword_outline(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    blurred = cv2.GaussianBlur(gray, (GAUSSIAN_BLUR_SIZE, GAUSSIAN_BLUR_SIZE), GAUSSIAN_BLUR_COUNT)
    thresh = cv2.adaptiveThreshold(blurred,255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,BLOCKSIZE,C)
    
    initial_contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    initial_contours = sorted(initial_contours, key=cv2.contourArea, reverse=True)

    x,y,w,h = cv2.boundingRect(initial_contours[0])
    cropped_image = deepcopy(img[y:y+h, x:x+w])
    return cropped_image

def detect_contours(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(gray, (GAUSSIAN_BLUR_SIZE, GAUSSIAN_BLUR_SIZE), GAUSSIAN_BLUR_COUNT)
    thresh = cv2.adaptiveThreshold(blurred,255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,BLOCKSIZE,C)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[1:] # Exclude the surrounding box
    
    contours = [Contour(c) for c in contours]
    filtered_contours = list(filter(lambda x: x.area>MIN_CONTOUR_SIZE and x.rectangularity>MIN_RECTANGULARITY, contours))
    return filtered_contours

    

#Grid creation
def create_all_corners(selected_contours):
    corners = []
    for c in selected_contours:
        corners.append((c.x, c.y))
        corners.append((c.x+c.w, c.y))
        corners.append((c.x+c.w, c.y+c.h))
        corners.append((c.x, c.y+c.h))
    
    return list(set(corners))

# Creates ranges from a list of coordinates
# Output is list of ranges [(1, 3)] means that the range for that line was from 1 to 3
def create_ranges(unique_vals, max_error):
    ranges = []
    range_start = unique_vals[0]
    for i in range(len(unique_vals)-1):
        current = unique_vals[i]
        next_val = unique_vals[i+1]
        
        diff = next_val-current
        if diff>max_error:
            ranges.append((range_start, current))
            range_start = next_val

    ranges.append((range_start, unique_vals[-1]))
    return ranges

# Create ranges for x and y
def create_grid_ranges(corners, max_error = 10):
    unique_x_vals = sorted(list(set([c[0] for c in corners])))
    x_ranges = create_ranges(unique_x_vals, max_error)
    
    unique_y_vals = sorted(list(set([c[1] for c in corners])))
    y_ranges = create_ranges(unique_y_vals, max_error)

    return x_ranges, y_ranges


def create_grid_from_contours(selected_contours, img):
    corners = create_all_corners(selected_contours)
    x_ranges, y_ranges = create_grid_ranges(corners)

    grid = np.empty(shape=(len(x_ranges)-1, len(y_ranges)-1), dtype = np.dtype(GridSquare))
    for grid_x in range(len(x_ranges)-1):
        for grid_y in range(len(y_ranges)-1):
            x_min = x_ranges[grid_x][0]
            x_max = x_ranges[grid_x+1][1]
            y_min = y_ranges[grid_y][0]
            y_max = y_ranges[grid_y+1][1]
            gs = GridSquare(x_min, x_max, y_min, y_max, grid_x, grid_y, img)
            grid[grid_x, grid_y] = gs
    
    return grid


# Display in jupyter notebook
def display_image(img):
    plt.figure(figsize = (math.ceil(img.shape[0]/75),math.ceil(img.shape[1]/75)))
    if len(img.shape)!=3 or img.shape[2]==1:
        plt.imshow(img,cmap='gray')
        plt.show()
        return
    img = img[:, :, ::-1].copy()
    plt.imshow(img)
    plt.show()

def show_contour_on_image(img, contours, idx):
    if isinstance(contours[0], Contour):
        contours = [c.contour for c in contours]
    image = deepcopy(img)
    cv2.drawContours(image, contours, idx, (0,255,0), thickness=3)
    display_image(image)


# Clustering
def calc_rectangularity(contour):
    x,y,w,h = cv2.boundingRect(contour)
    return cv2.contourArea(contour)/(w*h)

def mean_clustering(contours, max_diff = 0.15):
    upper_bound = 1+max_diff
    lower_bound = 1-max_diff

    clusters = [] # ([], mean area, mean_rect)
    for contour in contours:
        found = False
        for cluster in clusters:
            conditions = (
                contour.area < cluster[1] * upper_bound,
                contour.area > cluster[1] * lower_bound,
                contour.rectangularity < cluster[2] * upper_bound,
                contour.rectangularity > cluster[2] * lower_bound,
            )
            if all(conditions):
                cluster[0].append(contour)
                found = True
                cluster[1] = sum([c.area for c in cluster[0]])/len(cluster[0])
                cluster[2] = sum([c.rectangularity for c in cluster[0]])/len(cluster[0])
        
        if not found:
            clusters.append([[contour], contour.area, contour.rectangularity])
    clusters = sorted([c[0] for c in clusters], key = len, reverse = True)  
    return clusters

def range_clustering(contours, max_diff = 0.05):
    upper_bound = 1+max_diff
    lower_bound = 1-max_diff

    clusters = [] # ([], area_lower, area_upper, rect_lower, rect_upper)
    for contour in contours:
        found = False
        for cluster in clusters:
            conditions = (
                contour.area < cluster[2]*upper_bound,
                contour.area > cluster[1]*lower_bound,
                contour.rectangularity < cluster[4]*upper_bound,
                contour.rectangularity > cluster[3]*lower_bound,
            )
            
            if all(conditions):
                cluster[0].append(contour)
                found = True
                cluster[2] = max([c.area for c in cluster[0]])
                cluster[1] = min([c.area for c in cluster[0]])
                cluster[4] = max([c.rectangularity for c in cluster[0]])
                cluster[3] = min([c.rectangularity for c in cluster[0]])
                break
        
        if not found:
            clusters.append([[contour], contour.area, contour.area, contour.rectangularity, contour.rectangularity])

    overlapping_clusters = find_overlapping_clusters(clusters)
    clusters = combine_clusters(overlapping_clusters, clusters)
    
    return sorted(clusters, key = len, reverse = True)

def find_overlapping_clusters(clusters):
    overlapping_clusters = defaultdict(list)
    for i in range(len(clusters)):
        overlapping_clusters[i] # Create the list
        cluster1 = clusters[i]
        for j in range(i+1, len(clusters)):
            cluster2 = clusters[j]
            conditions = conditions = (
                cluster1[1] <= cluster2[2] <= cluster1[2] or cluster1[2] >= cluster2[1] >= cluster1[1],
                cluster1[3] <= cluster2[4] <= cluster1[4] or cluster1[4] >= cluster2[3] >= cluster1[3],
            )
            if all(conditions):
                overlapping_clusters[i].append(j)
        
    return overlapping_clusters

def find_all_children(clusters_to_combine, parent):
    children = set()
    for child in clusters_to_combine[parent]:
        children.add(child)
        if child in clusters_to_combine:
            children = children | find_all_children(clusters_to_combine, child)
    return children

def combine_clusters(overlapping_clusters, clusters):
    clusters_to_combine = []
    for parent in overlapping_clusters:
        l = find_all_children(overlapping_clusters, parent)
        l.add(parent)
        if not any([l.issubset(cluster) for cluster in clusters_to_combine]):
            clusters_to_combine.append(l)

    new_clusters = []
    for cluster_ids_to_combine in clusters_to_combine:
        new_clusters.append(sum([clusters[i][0] for i in cluster_ids_to_combine], []))
    return new_clusters