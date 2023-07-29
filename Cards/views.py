
from django.shortcuts import render
from django.http import StreamingHttpResponse,HttpResponse,JsonResponse

import requests
import base64
from rest_framework.response import Response 
import cv2
import torch
from yolov5.utils.torch_utils import select_device
from yolov5.utils.plots import Annotator, colors
from rest_framework.decorators import api_view
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from yolov5.detect import *
import json

pred_classes = [0,1,2,3,5,7,15,16,24,26,32,34,36,43,63,64,67,76]
#from django.http import JsonResponse
show_vid=False,  # show results
save_txt=False,  # save results to *.txt
save_conf=False,  # save confidences in --save-txt labels
save_crop=False,  # save cropped prediction boxes
save_vid=False, 
#pred_classes = torch.tensor([0,1,2,3,10]) 
imgsz=(1280, 1280)
#uploaded_file_url = 0
source = 0
data2 = None
frame_keys = []
def index(request): 
    return HttpResponse('Hello world')

device = select_device('cpu')

#torch.hub._validate_not_a_forked_repo=lambda a,b,c: True
#model = torch.hub.load('ultralytics/yolov5', 'custom', path='cardsdices.pt', force_reload = True)  # local custom model
model = torch.hub.load('ultralytics/yolov5','yolov5s')
model.conf = 0.35
stride, names, pt = model.stride, model.names, model.pt
imgsz = check_img_size(imgsz, s=stride)  # check image size 
import time
#cap = cv2.VideoCapture(0)
global json_value
json_value = {}

# #out = cv2.VideoWriter('drone_detection.avi',cv2.VideoWriter_fourcc(*'XVID'), 20, (1366,720))

seen = 0
# @smart_inference_mode
# @torch.no_grad()
# @api_view(['GET'])
def show_image(request):
    TMP_FOLDER = os.path.expanduser('~') + r"\temp"
    if not os.path.exists(TMP_FOLDER):
        os.makedirs(TMP_FOLDER)
    TMP_FILE = os.path.join(TMP_FOLDER, "temp.txt")
    #check TMP_FILE exists or not 
    if os.path.exists(TMP_FILE):
        with open(TMP_FILE, "r") as f:
            path = f.read()
    else:
        path = 'image.jpg'
    global data2,mydata,mydata2
    #json_value = {}
    mydata = {}
    mydata2 = []
    frame = cv2.imread(path)
    #ret,frame = cap.read()      
    if frame is not None:
        #frame = cv2.resize(frame,(1366,720),interpolation=cv2.INTER_AREA)
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY )
        print(frame.shape)

        results = model(frame, augment= True)

        det = results.pred[0]
        annotator = Annotator(frame, line_width=2,pil= not ascii)
        if det is not None and len(det):
            
            for j in det:
                if int(j[5]) not in pred_classes:
                    det = det[det.eq(j).all(dim=1).logical_not()]
            mylist = []
            for *xyxy, conf, cls in reversed(det):  
                # xywhs = xyxy2xywh(det[:, 0:4])
                # xyxy = det[:, 0:4]
                # confs = det[:, 4]
                # clss = det[:, 5]
                #print(c)
                c = int(cls)  # integer class
                label = f'{names[c]} {conf:.2f}'
                mylist.append(names[c])
                annotator.box_label(xyxy, label, color=colors(c, True))
                mydata = {'x1':int(xyxy[0]), 'y1':int(xyxy[1]), 'x2':int(xyxy[2]), 'y2':int(xyxy[3]),'class': names[c],'color': colors(c,True),'score':round(float(label.split(' ')[1]) * 100,2)}
                mydata2.append(mydata)
  
        frame = annotator.result()
        #frame = frame*255.0
        #data = im.fromarray(frame[:,:,::-1])
        _,data = cv2.imencode('.jpg',frame)
        data = base64.b64encode(data).decode('utf-8')
        json_value['detections'] = mydata2
        
        return JsonResponse(data, safe=False)
        
        
                  
           

def detection_json(request):
   
    return JsonResponse(json_value, safe=False)




            

        
        
            
            
        
            
            
            
          
            
            



    


