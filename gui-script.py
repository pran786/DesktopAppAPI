# import os
# activate_this = "DesktopAppAPI/CRD_ENV/Scripts/activate"
# exec(open(activate_this).read(), {'_file_': activate_this})
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic
import sys
import os
import time
from PIL import Image
import base64
import requests
from qt_material import apply_stylesheet 
import threading
import subprocess


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.layout_filename = "gui-layout.ui"
        uic.loadUi(self.layout_filename, self)
        self.InitWindow()

    def InitWindow(self):
        self.setWindowTitle("Image Processing")
        self.setting.clicked.connect(self.setting_clicked)
        self.save_and_continue.clicked.connect(self.save_and_continue_clicked)
        self.stackedWidget.setCurrentIndex(0)
        apply_stylesheet(app, theme='dark_teal.xml')
        self.light_theme.toggled.connect(self.light_theme_clicked)
        self.browse1.clicked.connect(self.browser1_clicked)
        self.browse2.clicked.connect(self.browser2_clicked)
        self.detect.clicked.connect(self.detect_clicked)
        self.export_.clicked.connect(self.export_clicked)

        #create temp folder
        # self.TMP_FOLDER = os.path.expanduser('~') + r"\temp"
        self.TMP_FOLDER = os.path.join(os.path.expanduser('~'), "temp")

        #check if temp folder exists or not if not create it
        if not os.path.exists(self.TMP_FOLDER):
            os.makedirs(self.TMP_FOLDER)
        self.TMP_FILE = os.path.join(self.TMP_FOLDER, "temp.txt")
        


        self.show()

    def browser1_clicked(self):
        filename = QFileDialog.getOpenFileName(self, 'Open File', 'c:\\', "Image files (*.jpg *.gif *.png *.jpeg)")
        if filename[0]:
            filename1 = filename[0].replace("/", "\\")
            self.input_image_path.setText(filename1)

    def browser2_clicked(self):
        #get folder path
        foldername = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if foldername:
            foldername = foldername.replace("/", "\\")
        self.output_folder_path.setText(foldername)

    def light_theme_clicked(self):
        if self.light_theme.isChecked():
            apply_stylesheet(app, theme='light_teal.xml')
        else:
            apply_stylesheet(app, theme='dark_teal.xml')

    def setting_clicked(self):
        self.stackedWidget.setCurrentIndex(0)
        

    def save_and_continue_clicked(self):
        
        # self.input_img_path_ = self.input_image_path.text()
        try:
            self.img_path_ = self.input_image_path.text()
            #change the border color to normal
            self.input_image_path.setStyleSheet("border: 1px transparent;")
            if self.img_path_ == "":
                raise ValueError
            if os.path.exists(self.img_path_) == False:
                raise ValueError
        except ValueError:
            # red border 
            self.input_image_path.setStyleSheet("border: 2px solid red;")
            return
        try:
            self.output_folder_path_ = self.output_folder_path.text()
            #change the border color to normal
            self.output_folder_path.setStyleSheet("border: 1px transparent;")
            if self.output_folder_path_ == "":
                raise ValueError
            if os.path.exists(self.output_folder_path_) == False:
                raise ValueError
            
        except ValueError:
            # red border 
            self.output_folder_path.setStyleSheet("border: 2px solid red;")
            return

        self.output_folder_path_ = self.output_folder_path.text()
        # print("img_path: ", self.img_path_)
        # print("output_folder: ", self.output_folder_path_)

        try:
            img = Image.open(self.img_path_)
            # img = self.img.convert("RGB")
            #set size of the image to 400x400
            img = img.resize((400, 400))
            #save the image to current directory
            file_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp1.png")
            img.save(file_name)
            #set the image to the label
            self.raw_image.setPixmap(QPixmap(file_name))
        
        except Exception as e:
            #add red border to the input image path
            self.input_image_path.setStyleSheet("border: 2px solid red;")
            return
        
        self.stackedWidget.setCurrentIndex(1)

    def detect_clicked(self):
        #create temp.txt and save the image_path
        with open(self.TMP_FILE, "w") as f:
            f.write(self.img_path_)

        #url
        url1 ="http://127.0.0.1:8000/show_image"

        #get the response text
        response = requests.get(url1)
        encoded_string = response.text
        #string to bytes
        self.encoded_string = encoded_string.encode('utf-8')
        #convert to image
        with open(os.path.join(self.TMP_FOLDER, "temp2.png"), "wb") as fh:
            fh.write(base64.decodebytes(self.encoded_string))

        #change the size of the image
        img = Image.open(os.path.join(self.TMP_FOLDER, "temp2.png"))
        img = img.resize((400, 400))
        img.save(os.path.join(self.TMP_FOLDER, "temp2.png"))

        #set the image to the label
        self.processed_image.setPixmap(QPixmap(os.path.join(self.TMP_FOLDER, "temp2.png")))


        #json data
        url2="http://127.0.0.1:8000/json_data"

        res = requests.get(url2)
        # print(res.text)
        #convert to json
        data = res.json()
        detection_list = data["detections"]
        self.tableWidget.setRowCount(0)
        for i in detection_list:
            x1= i["x1"]
            y1= i["y1"]
            x2= i["x2"]
            y2= i["y2"]
            class_name = i["class"]
            score = i["score"]
            # print(x1, y1, x2, y2, class_name, score)
            #table widget tableWidget
            rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPosition)
            self.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(str(class_name)))
            self.tableWidget.setItem(rowPosition, 1, QTableWidgetItem(str(score)))
            self.tableWidget.setItem(rowPosition, 2, QTableWidgetItem(str(x1)))
            self.tableWidget.setItem(rowPosition, 3, QTableWidgetItem(str(y1)))
            self.tableWidget.setItem(rowPosition, 4, QTableWidgetItem(str(x2)))
            self.tableWidget.setItem(rowPosition, 5, QTableWidgetItem(str(y2)))

        #set the table widget to the label
        # self.tableWidget.resizeColumnsToContents()
        # self.tableWidget.resizeRowsToContents()

    
    def export_clicked(self):
        #save the image
        image_name = os.path.basename(self.img_path_)
        image_name = os.path.splitext(image_name)[0]
        image_name = image_name + "_processed.png"
        image_path = os.path.join(self.output_folder_path_, image_name)

        #convert to image
        # with open("temp.png", "wb") as fh:
        #     fh.write(base64.decodebytes(encoded_string))
        with open(image_path, "wb") as fh:
            fh.write(base64.decodebytes(self.encoded_string))


def start_server():
    # activate_path = "..\project_updated_delivery\DesktopAppAPI\CRD_ENV\Scripts\activate.bat"
    # activate_cmd = f"call {activate_path} && "
    
    # # Start the Django server
    # os.system(f"{activate_cmd}python manage.py runserver")
    print('worked')
    # import django
    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eDETECT.settings')
    # django.setup()
    subprocess.call(['python', 'manage.py','runserver'])




        


if __name__ == '__main__':

    server_thread = threading.Thread(target=start_server)
    server_thread.start()
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    #apply qdarktheme stylesheet to the application
    # apply_stylesheet(app, theme='light_teal.xml')
    sys.exit(app.exec_())
