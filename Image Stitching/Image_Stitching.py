import cv2
import numpy as np
import sys

def load_images(image_paths):
    images = []
    for path in image_paths:
        img = cv2.imread(path)
        if img is None:
            print(f"Error: Could not load image {path}")
            sys.exit(1)
        images.append(img)
    return images

def stitch_images(img1, img2):
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    sift = cv2.SIFT_create()
    keypoints1, descriptors1 = sift.detectAndCompute(gray1, None)
    keypoints2, descriptors2 = sift.detectAndCompute(gray2, None)
    
    index_params = dict(algorithm=1, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(descriptors1, descriptors2, k=2)
    
    good_matches = [m for m, n in matches if m.distance < 0.7 * n.distance]
    
    if len(good_matches) > 4:
        src_pts = np.float32([keypoints1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        
        H, status = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        
        if H is None:
            print("Error: Homography computation failed")
            sys.exit(1)
        
        height, width = img2.shape[:2]
        panorama = cv2.warpPerspective(img1, H, (width * 2, height))
        panorama[0:height, 0:width] = img2
        return panorama
    else:
        print("Error: Not enough matches found")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python Image_Stitching.py <image1> <image2>")
        sys.exit(1)
    
    images = load_images(sys.argv[1:3])
    result = stitch_images(images[0], images[1])
    cv2.imwrite("stitched_output.jpg", result)
    print("Stitching complete. Saved as 'stitched_output.jpg'")
