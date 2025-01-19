import cv2
import time
import glob
import os
import numpy as np
from emailing import send_email

video=cv2.VideoCapture(0)
time.sleep(1)
first_frame=None
status_list=[]
count=1

def clean_folder():
    images=glob.glob("images/*.png")
    for image in images:
        os.remove(image)
        
while True:
    status=0
    check,frame=video.read()
    gray_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    gray_frame_gblur=cv2.GaussianBlur(gray_frame,(21,21),0)
    
    if first_frame is None:
        first_frame=gray_frame_gblur
    diff_frame=cv2.absdiff(first_frame,gray_frame_gblur)
    
    thresh_frame=cv2.threshold(diff_frame,60,255,cv2.THRESH_BINARY)[1]
    kernel = np.ones((3, 3), np.uint8)
    dil_frame=cv2.dilate(thresh_frame,kernel,iterations=2)
    contours,check=cv2.findContours(dil_frame,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        if cv2.contourArea(contour)<5000:
            continue
        x,y,w,h=cv2.boundingRect(contour)
        rect=cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0))
        if rect.any():
            status=1
            cv2.imwrite(f"images/{count}.png",frame)
            count=count+1
        try:
            all_images=glob.glob("images/*.png")
            index=int(len(all_images)/2)
            image_with_obj=all_images[index]
        except Exception:
            print("No image is detected to Capture!!")
            
    status_list.append(status)
    status_list=status_list[-2:]
    if status_list[0]==1 and status_list[1]==0:
        send_email(image_with_obj)
        clean_folder()
        break
    cv2.imshow("Video",frame)
    key=cv2.waitKey(1)
    
    if key==ord("q"):
        break
video.release()
cv2.destroyAllWindows()
