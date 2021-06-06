import sys, os
from turtle import pd

from PIL import Image
from PyQt5.uic import loadUi
from PySide2 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QBasicTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox, QDialog
import cv2
import numpy as np
import MySQLdb as mdb
import time
import source
from time import strftime
from datetime import datetime
import face_recognition
from database import dbConnection

# Global Variables
counter = 0


class SplashScreen(QMainWindow):
    def __init__(self):
        super(SplashScreen, self).__init__()
        loadUi("gui/SplashScreen.ui", self)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)

        # REMOVE TITLE BAR
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # TIMER IN MILLISECONDS
        self.timer.start(45)

        # Initial Text
        self.label_description.setText("<strong>LOADING</strong> THE RESOURCES")

        # Change Texts
        QtCore.QTimer.singleShot(500, lambda: self.label_description.setText("<strong>LOADING</strong> DATABASE"))
        QtCore.QTimer.singleShot(1500,
                                 lambda: self.label_description.setText("<strong>LOADING</strong> USER INTERFACE"))
        QtCore.QTimer.singleShot(2500, lambda: self.label_description.setText("<strong>LOADING</strong> TEACHER PANEL"))
        QtCore.QTimer.singleShot(3500, lambda: self.label_description.setText("<strong>LOADING</strong> MODULES"))

        self.show()

    def progress(self):
        global counter

        # SET VALUE TO PROGRESS BAR
        self.progressBar.setValue(counter)

        # CLOSE SPLASH SCREE AND OPEN APP
        if counter > 100:
            # STOP TIMER
            self.timer.stop()

            # SHOW MAIN WINDOW
            self.login = Login()
            self.login.show()

            # CLOSE SPLASH SCREEN
            self.close()

        # INCREASE COUNTER
        counter += 1

###############################################################################################################
###############################################################################################################

# Login Panel
class Login(QMainWindow):
    def __init__(self):
        super(Login, self).__init__()
        loadUi("gui/LoginForm.ui", self)
        # REMOVE TITLE BAR
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.show()
        # Buttons Actions
        self.btn_close.clicked.connect(lambda: self.showClose())
        self.btn_to_signUp.clicked.connect(lambda: self.showtoSignup())
        self.btn_login.clicked.connect(lambda: self.dbLogin())
        self.btn_forgot.clicked.connect(lambda: self.gotoForgot())
        self.btn_manual.clicked.connect(lambda: self.manual())

        checkUname = self.txt_username.text()

        # Buttons Functions

    def showClose(self):
        ret = QMessageBox.question(self, 'Quit Window', "Do you want to exit the application? ",
                                   QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.close()
        else:
            self.show()

    def showtoSignup(self):
        self.toSignup = Register()
        self.toSignup.show()
        self.close()

    def gotoForgot(self):
        self.toForgot = ForgotPassword()
        self.toForgot.show()

    def manual(self):
        os.startfile("User-Manual.txt")

    def dbLogin(self):
        try:
            username = self.txt_username.text()
            password = self.txt_password.text()

            con = dbConnection.mycursor
            con.execute(
                "SELECT Username,Password from teacher where Username like '" + username + "'and Password like '" + password + "'")
            result = con.fetchone()
            if username == "admin" and password == "admin":
                self.loginAdmin = Admin()
                self.loginAdmin.show()
                self.hide()
                QMessageBox.information(self, "Success", "You are successfully Logged In as Admin")
            elif result == None:
                self.txt_result.setText("Incorrect Username or Password")
                self.txt_username.clear()
                self.txt_password.clear()
            else:
                self.loginUser = Teacher()
                self.loginUser.show()
                self.hide()
                QMessageBox.information(self, "Success", "You are successfully Logged In")



        except dbConnection.mydb.Error as e:
            self.txt_result.setText("Error! Connecting the Database")

###############################################################################################################
###############################################################################################################

class ForgotPassword(QDialog):
    def __init__(self):
        super(ForgotPassword, self).__init__()
        loadUi("gui/ForgotPass.ui", self)
        self.show()

        # Buttons
        self.change_pw.clicked.connect(lambda: self.changePw())

    def changePw(self):
        uname = self.txt_sUname.text()
        secQ = self.security_qn.currentText()
        secA = self.txt_Sans.text()
        newPass = self.txt_newPass.text()
        check_pass = len(newPass)
        mydb = mdb.connect(
            host="localhost",
            user="root",
            password="",
            database="ams_database"
        )
        con = mydb.cursor()
        con.execute("SELECT * FROM teacher WHERE Username=%s and Sec_Qn=%s and Sec_Ans=%s",(uname,secQ,secA))
        result = con.fetchone()

        if result == None:
            QMessageBox.critical(self, "Error", "Please Enter Valid Username or Security Question to reset password")
        elif check_pass<=5:
            QMessageBox.critical(self, "Error", "Please Enter Password at Least 6 Characters long")
        else:
            con.execute("update teacher set Password=%s where Username=%s",(newPass,uname))
            mydb.commit()
            con.close()
            QMessageBox.information(self, "Success", "Your Password was successfully changed")




###############################################################################################################
###############################################################################################################

# Registration Panel

class Register(QMainWindow):
    def showClose(self):
        ret = QMessageBox.question(self, 'Quit Window', "Do you want to exit the application? ",
                                   QMessageBox.Yes | QMessageBox.No)

        if ret == QMessageBox.Yes:
            self.close()
        else:
            self.show()

    def showtoSignIn(self):
        self.toSignIn = Login()
        self.toSignIn.show()
        self.close()

    def dbRegister(self):
        try:
            fullname = self.txt_fname.text()
            teacherId = self.txt_t_id.text()
            module = self.txt_module.text()
            username = self.txt_uname.text()
            password = self.txt_pass.text()
            sec_question = self.security_qn.currentText()
            sec_ans = self.sec_ans.text()

            sec_pass = len(password)

            if username == "admin" and password == "admin":
                self.txt_result.setText("User Already Registered")
                self.txt_uname.clear()
                self.txt_pass.clear()
            elif fullname=="" or teacherId=="" or module=="" or username=="" or password=="" or sec_question=="" or sec_ans=="":
                self.txt_result.setText("All Fields Must be Filled Properly")
            elif sec_pass <= 5:
                self.txt_result.setText("Password Must be at Least 6 Characters Long")
                self.txt_pass.clear()
            else:
                con = dbConnection.mycursor
                sql = "INSERT INTO teacher(FullName, TeacherID, Module, Username, Password, Sec_Qn, Sec_Ans) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                val = (fullname, teacherId, module, username, password, sec_question, sec_ans)
                con.execute(sql, val)
                dbConnection.mydb.commit()
                QMessageBox.information(self, "Success", "User Registered Successfully")


        except dbConnection.mydb.Error as e:
            self.txt_result.setText("Error! Registration Failed")

    def __init__(self):
        super(Register, self).__init__()
        loadUi("gui/Signup.ui", self)
        # REMOVE TITLE BAR
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.show()
        # Buttons Actions
        self.btn_close.clicked.connect(lambda: self.showClose())
        self.btn_back_login.clicked.connect(lambda: self.showtoSignIn())
        self.btn_register.clicked.connect(lambda: self.dbRegister())



###############################################################################################################
###############################################################################################################

# Admin Panel

class Admin(QMainWindow):
    def __init__(self):
        super(Admin, self).__init__()
        loadUi("gui/AdminPanel.ui", self)
        self.btn_viewTeacher.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_1))
        self.btn_addStudent.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_2))
        self.btn_viewStudent.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_3))
        self.btn_loadTeacher.clicked.connect(lambda: self.select_data())
        self.btn_openCamera.clicked.connect(lambda: self.takeImage())
        self.btn_submitForm.clicked.connect(lambda: self.dbStudent())
        self.btn_viewMyStudent.clicked.connect(lambda: self.viewMyStudent())
        self.btn_logout.clicked.connect(lambda: self.logoutAdmin())
        self.btn_close.clicked.connect(lambda: self.showClose())
        self.tableWidget.setColumnWidth(0, 150)
        self.tableWidget.setColumnWidth(1, 150)
        self.tableWidget.setColumnWidth(2, 200)

        # REMOVE TITLE BAR
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.show()

    def showClose(self):
        ret = QMessageBox.question(self, 'Quit Window', "Do you want to exit the application? ",
                                   QMessageBox.Yes | QMessageBox.No)

        if ret == QMessageBox.Yes:
            self.close()
        else:
            self.show()

    def logoutAdmin(self):
        ret = QMessageBox.question(self, 'Log Out', "Do you want to Logout? ",
                                   QMessageBox.Yes | QMessageBox.No)

        if ret == QMessageBox.Yes:
            self.logout = Login()
            self.logout.show()
            self.hide()
        else:
            self.show()

    def select_data(self):
        try:
            con = dbConnection.mycursor

            con.execute("SELECT FullName,TeacherID,Module FROM teacher")

            result = con.fetchall()
            self.tableWidget.setRowCount(0)
            for row_number, row_data in enumerate(result):
                print(row_number)
                self.tableWidget.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    # print(column_number)
                    self.tableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        except dbConnection.mydb.Error as e:
            print("Error")

    def dbStudent(self):
        regNo = self.txt_rNo.text()
        fullName = self.txt_fullName.text()
        level = self.txt_level.text()
        semester = self.txt_semester.text()
        batch = self.txt_batch.text()

        if regNo=="" or fullName=="" or level=="" or semester=="" or batch=="":
            self.txt_Notification.setText("Error! All Fields Should be Filled")
        else:
            try:
                con = dbConnection.mycursor
                sql = "INSERT INTO student(RegNo, FullName, Level, Semester, Batch) VALUES (%s, %s, %s, %s, %s)"
                val = (regNo, fullName, level, semester, batch)
                con.execute(sql, val)
                dbConnection.mydb.commit()
                QMessageBox.information(self, "Success", "Student Registered Successfully")

            except dbConnection.mydb.Error as e:
                self.txt_Notification.setText("Error! Failed to add Students")

    def viewMyStudent(self):
        try:
            con = dbConnection.mycursor
            con.execute("SELECT RegNo, FullName, Level, Semester, Batch FROM student")

            result = con.fetchall()
            self.tableWidget_admin.setRowCount(0)
            for row_number, row_data in enumerate(result):
                print(row_number)
                self.tableWidget_admin.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.tableWidget_admin.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        except dbConnection.mydb.Error as e:
            print("Error Connecting the Database")

    def takeImage(self):
        face_id = self.txt_rNo.text()
        user_name = self.txt_fullName.text()

        if face_id=="" or user_name=="":
            self.txt_Notification.setText("All Fields Should be Filled to Open Camera")
        else:
            vid_cam = cv2.VideoCapture(0)
            face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
            count = 0
            while True:
                _, image_frame = vid_cam.read()
                gray = cv2.cvtColor(image_frame, cv2.COLOR_BGR2GRAY)
                faces = face_detector.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(image_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    count += 1
                    cv2.imwrite("dataset/" + str(user_name) + '.' + str(face_id) + '.' + str(count) + ".jpg",
                                gray[y:y + h, x:x + w])
                    cv2.imshow('frame', image_frame)
                if cv2.waitKey(100) & 0xFF == ord('q'):
                    break
                elif count >= 50:
                    print("Successfully Captured")
                    QMessageBox.information(self, "Success", "Student Dataset Successfully Captured")
                    break
            vid_cam.release()
            cv2.destroyAllWindows()

###############################################################################################################

# Teacher Panel

class Teacher(QMainWindow):
    def __init__(self):
        super(Teacher, self).__init__()
        loadUi("gui/TeacherPanel.ui", self)

        self.btn_MyStd.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_1))
        self.btn_ClassReport.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_2))
        self.btn_MyRoutine.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_3))
        self.btn_StartAttendance.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_4))
        self.btn_viewStudent.clicked.connect(lambda: self.viewStudent())
        self.btn_teacherLogout.clicked.connect(lambda: self.logoutTeacher())
        self.btn_close.clicked.connect(lambda: self.showClose())
        self.btn_startAttendance.clicked.connect(lambda: self.faceRecognition())
        self.btn_trainImage.clicked.connect(lambda: self.train_classifier())
        self.btn_searchID.clicked.connect(lambda: self.searchUser())
        self.tableWidget.setColumnWidth(0, 100)
        self.tableWidget.setColumnWidth(1, 150)

        # REMOVE TITLE BAR
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.show()

    def showClose(self):
        ret = QMessageBox.question(self, 'Quit Window', "Do you want to exit the application? ",
                                   QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.close()
        else:
            self.show()

    def logoutTeacher(self):
        ret = QMessageBox.question(self, 'Log Out', "Do you want to Logout? ",
                                   QMessageBox.Yes | QMessageBox.No)

        if ret == QMessageBox.Yes:
            self.showLogin = Login()
            self.showLogin.show()
            self.hide()
        else:
            self.show()


    def viewStudent(self):
        try:
            con = dbConnection.mycursor
            con.execute("SELECT RegNo, FullName, Level, Semester, Batch FROM student")

            result = con.fetchall()
            self.tableWidget.setRowCount(0)
            for row_number, row_data in enumerate(result):
                print(row_number)
                self.tableWidget.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.tableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        except dbConnection.mydb.Error as e:
            print("Error Connecting the Database")

    def doAction(self):
        for i in range(101):
            time.sleep(0.03)
            self.progressBar.setValue(i)
        QMessageBox.about(self, "Success", "Dataset Training Completed")

    def train_classifier(self):
        data_dir = 'dataset'
        path = [os.path.join(data_dir, f) for f in os.listdir(data_dir)]

        faces = []
        ids = []

        for image in path:
            img = Image.open(image).convert('L')
            imageNp = np.array(img, 'uint8')
            id = int(os.path.split(image)[1].split(".")[1])

            faces.append(imageNp)
            ids.append(id)

        ids = np.array(ids)

        # Train and save classifier
        clf = cv2.face.LBPHFaceRecognizer_create()
        clf.train(faces, ids)
        clf.write("trainer/trainer.xml")
        self.doAction()

    def markAttendance(self,r,s,l):
        with open("Attendance.csv","r+",newline="\n") as f:
            myDataList = f.readlines()
            nameList=[]
            for line in myDataList:
                entry= line.split((','))
                nameList.append(entry[0])
            if((s not in nameList) and (r not in nameList)):
                now = datetime.now()
                d1 = now.strftime("%d/%m/%Y")
                dtString=now.strftime("%H:%M:%S")
                f.writelines(f"\n{r},{s},{l},{d1},{dtString},Present")

    def faceRecognition(self):
        def draw_boundary(img, classifier, scaleFactor, minNeighbors, color, text, clf):
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            features = classifier.detectMultiScale(gray_img, scaleFactor, minNeighbors)

            for (x, y, w, h) in features:
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)

                RegNo, pred = clf.predict(gray_img[y:y + h, x:x + w])
                confidence = int(100 * (1 - pred / 300))
                mydb = mdb.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="ams_database"
                )
                mycursor = mydb.cursor()
                mycursor.execute("select FullName from student where RegNo=" + str(RegNo))
                s = mycursor.fetchone()  # tuple
                s = '' + ''.join(s)  # string

                mycursor.execute("select RegNo from student where RegNo=" + str(RegNo))
                r = mycursor.fetchone()  # tuple
                r = '' + ''.join(r)  # string

                mycursor.execute("select Level from student where RegNo=" + str(RegNo))
                l = mycursor.fetchone()  # tuple
                l = '' + ''.join(l)  # string

                if confidence > 77:
                    cv2.putText(img, f"Reg No :{r}", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
                    cv2.putText(img, f"Name :{s}", (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
                    self.markAttendance(r,s,l)
                else:
                    cv2.putText(img, "UNKNOWN FACE", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 1, cv2.LINE_AA)

            return img

        # loading classifier
        faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

        clf = cv2.face.LBPHFaceRecognizer_create()
        clf.read("trainer/trainer.xml")

        video_capture = cv2.VideoCapture(0)

        while True:
            ret, img = video_capture.read()
            img = draw_boundary(img, faceCascade, 1.3, 6, (255, 255, 255), "Face", clf)
            cv2.imshow("Face Detection", img)

            if cv2.waitKey(1) == 13:
                break
        video_capture.release()
        cv2.destroyAllWindows()

    def searchUser(self):
        uname = self.txt_searchusername.text()
        mydb = mdb.connect(
            host="localhost",
            user="root",
            password="",
            database="ams_database"
        )
        con = mydb.cursor()
        con.execute("select Password from teacher where Username=%s", (uname,))
        p = con.fetchone()
        p = '' + ''.join(p)  # string

        con.execute("select Module from teacher where Username=%s", (uname,))
        m = con.fetchone()  # tuple
        m = '' + ''.join(m)  # string

        con.execute("select FullName from teacher where Username=%s", (uname,))
        f = con.fetchone()  # tuple
        f = '' + ''.join(f)  # string

        con.execute("select TeacherID from teacher where Username=%s", (uname,))
        t = con.fetchone()  # tuple
        t = '' + ''.join(t)  # string

        self.txt_gpas.setText(p)
        self.txt_gmodule.setText(m)
        self.txt_gname.setText(f)
        self.txt_gid.setText(t)

    # def updateUser(self):
    #     uname = self.txt_searchusername.text()
    #     newPass = self.txt_gpas.text()
    #     newModule = self.txt_gmodule.text()
    #     newName = self.txt_gname.text()
    #
    #     if len(newPass)>=6 and newName!="" and newModule!="":
    #         mydb = mdb.connect(
    #             host="localhost",
    #             user="root",
    #             password="",
    #             database="ams_database"
    #         )
    #         con = mydb.cursor()
    #         sql = "UPDATE teacher SET Password=%s and FullName=%s and Module=%s WHERE Username=%s"
    #         con.execute(sql,(newPass,newName,newModule,uname))
    #         mydb.commit()
    #         con.close()
    #         QMessageBox.information(self, "Success", "Your Profile is Successfully Updated")
    #     elif newPass!="" or newName!="" or newModule!="":
    #         QMessageBox.critical(self, "Error", "Please Enter all the fields")
    #     else:
    #         QMessageBox.critical(self, "Error", "Password Must be 6 Characters Long")

######################################################### ######################################################

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = SplashScreen()
    ui.show()
    sys.exit(app.exec_())
