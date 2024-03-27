import cv2
from ultralytics import YOLO
import threading
import time
from datetime import datetime
import logging
import os
import numpy as np
import requests
import mysql.connector
import sys
import ast
import argparse
from pathlib import Path


## ARGUMENT PARSER PARAMETER
##--------------------------------------------------------------------------------------------------##

ap = argparse.ArgumentParser()
ap.add_argument("-r", "--rtsp", type=str,required=True,
	help="name of the user")
ap.add_argument("-d", "--delay",type=int, required=True,
	help="delay detection")
ap.add_argument("-n", "--nocctv", type=str,required=True,
	help="no cctv")
ap.add_argument("-i", "--input_titik", type=str,required=True,
	help="input_titik")
ap.add_argument("-m", "--masking", type=str,required=True,
	help="masking")
ap.add_argument("-e", "--endpoint", type=str,required=True,
	help="endpoint")

args = vars(ap.parse_args())


# ERROR HANDLING RTSP
RTSP_CCTV  = args["rtsp"]
print(RTSP_CCTV)
if "null" in RTSP_CCTV:
    RTSP_CCTV= args["rtsp"]

DELAY_DETECTION = args["delay"]
nocctv = args["nocctv"]
masking  = args["masking"]
endpoint = args["endpoint"]
input_titik = args["input_titik"]


## Masking
try:
    masking = ast.literal_eval(masking)
except (SyntaxError, ValueError) as e:
    print(f"Error: {e}")


#GET DATA FROM ENV####
# import ast
# f = open('./config.txt', 'r')
# api=f.read()
# dictapi = ast.literal_eval(api)
# nocctv=str(dictapi['nocctv'])
# database_db=str(dictapi["DATABASE"])
# host_db=str(dictapi["HOST_DB"])
# password_db=str(dictapi["PASSWORD_DB"])
# user_db=str(dictapi["USER_DB"])


user_db = os.getenv("USER_DB", "aicctv")
password_db = os.getenv("PASSWORD_DB", "jmt02022!")
host_db  = os.getenv("HOST_DB", "127.0.0.1")
database_db  = os.getenv("DATABASE", "deteksi_motor")
database_db = database_db+"_0"+input_titik

##--------------------------------------------------------------------------------------------------

## FUNGSI UNTUK READ LOG
def write_log(lokasi_log, datalog):
    waktulog = datetime.now()
    dirpathlog = f"Log/{lokasi_log}"
    os.makedirs(dirpathlog, exist_ok=True)
    pathlog = f"{waktulog.strftime('%d%m%Y')}.log"
    file_path = Path(f"{dirpathlog}/{pathlog}")
    datalog = "[INFO] - " + datalog
    if not file_path.is_file():
        file_path.write_text(f"{waktulog.strftime('%d-%m-%Y %H:%M:%S')} - {datalog}\n")
    else :
        fb = open(f"{dirpathlog}/{pathlog}", "a")
        fb.write(f"{waktulog.strftime('%d-%m-%Y %H:%M:%S')} - {datalog}\n")
        fb.close
    
    print(f"{waktulog.strftime('%d-%m-%Y %H:%M:%S')} - {datalog}")

def write_log_error(lokasi_log, datalog):
    waktulog = datetime.now()
    dirpathlog = f"Log/{lokasi_log}"
    os.makedirs(dirpathlog, exist_ok=True)
    pathlog = f"{waktulog.strftime('%d%m%Y')}.log"
    file_path = Path(f"{dirpathlog}/{pathlog}")
    datalog = "[ERROR] - " + datalog
    if not file_path.is_file():
        file_path.write_text(f"{waktulog.strftime('%d-%m-%Y %H:%M:%S')} - {datalog}\n")
    else :
        fb = open(f"{dirpathlog}/{pathlog}", "a")
        fb.write(f"{waktulog.strftime('%d-%m-%Y %H:%M:%S')} - {datalog}\n")
        fb.close
    
    print(f"{waktulog.strftime('%d-%m-%Y %H:%M:%S')} - {datalog}")


#### Fungsi saved image
##lokasi_image titik cctv
##frame 

# def write_pict(lokasi_image,frame)
#     global frame
#     dirpathlog = f"image/{lokasi_image}"
#     os.makedirs(dirpathlog, exist_ok=True)
#     cv2.imwrite(dir_pict_org, frame_main)


def play_sound():
    global endpoint
    write_log(input_titik,"START TO VOICE OUTPUT MOTOR")
    try:
        #ENDPOINT=os.getenv("ENDPOINT", "http://172.16.12.114:8200/status_auto")
        r = requests.get(url = endpoint)
        write_log(input_titik,"SUCCESSED TO VOICE OUTPUT MOTOR")
        data = r.json()
        pesan=data['status']
        logging.warning(pesan)
    except:
        write_log(input_titik,"NOT CONNETED RASPBERRY PI")
        pass

## -----------------------------------------MAIN PROGRAM -------------------------------------------------

if __name__ == '__main__':

        temp_id=0
        temp_id_bis=0
        flag=1
        flag_bis=1

        write_log(input_titik,"START PROGRAM CCTV SURVAILANCE MOTOR")
        write_log(input_titik,database_db)
        ## Inisialisasi cctv
        cap = cv2.VideoCapture(RTSP_CCTV)
        cur_dir = os.getcwd()
        model=YOLO("yolov8s.pt")
        get_fps = True
        get_fps_bis = True
        
        while cap.isOpened():
            success, frame_main = cap.read()
            if success:
                sound_thread = threading.Thread(target=play_sound)
                masking_frame=frame_main.copy()
                
                ## Resize File save to 640,480
                save_vid=frame_main.copy()
                cv2.resize(save_vid, (640, 480), interpolation = cv2.INTER_LINEAR)

                ## masking
                MaskCoord=np.array((masking))
                try:
                    cv2.fillPoly(masking_frame, pts=[MaskCoord], color=(0, 0, 0))
                except:
                    pass

                ## TAMPILAN UI
                cv2.imshow('CAM masking', masking_frame)
                cv2.imshow('CAM LIVE', frame_main)
                #logging.info("LIVE")
                
                ## mode max detection banyak
                results = model.track(masking_frame, persist=True, conf=0.5 , classes=[1,3], verbose=False, agnostic_nms=False)
                # #results2 = model.track(frame_main, persist=True, conf=0.60 , classes=[0,2,5], verbose=False, agnostic_nms=False)[0].plot(line_width=1, labels=True, conf=True)
                # frame = results[0].plot(line_width=1, labels=True, conf=True)

                
                if len(results[0].boxes.cls) > 0 :
                    
                    for i in results[0].boxes :
                        xyxy = i.xyxy
                        #write_log(input_titik,"ADA DETEKSI1")
                        name_clas = int(i.cls.item())
                        if name_clas == 3:
                            name_clas="Motor"
                        elif name_clas == 1:
                            name_clas="Sepeda"

                        #write_log(input_titik,"ADA DETEKSI2")
                        #name_clas= result.names[clas]
                        conf = float(i.conf.item())
                        conf = round(conf, 2)
                        print(str(xyxy[0]))
                        # print(type(xyxy[0]))
                        write_log(input_titik,"ADA DETEKSI")
                        frame_kotak = cv2.rectangle(frame_main, (int(xyxy[0][0]), int(xyxy[0][1])), (int(xyxy[0][2]), int(xyxy[0][3])), (255,255,255), 1)
                        frame_kotak = cv2.putText(frame_kotak,str(conf)+" - "+str(name_clas),(int(xyxy[0][0]), int(xyxy[0][1]) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.15, (255,255,255), 1, cv2.LINE_AA)

                    bus=1
                    person=3

                    ## DETEKSI BUS

                    if bus in results[0].boxes.cls.tolist():
                        deteksi_bis=0
                        id_box_bis=results[0].boxes.data.tolist()[0][4]

                        if flag_bis==1 and id_box_bis!= temp_id_bis:
                            write_log(input_titik,"ADA DETEKSI SEPEDA")


                            start_time_bis = time.time()
                            flag_bis=0
                            for i in results[0].boxes.cls.tolist():
                                if i == bus:
                                    deteksi_bis=deteksi_bis+1
                                

                            ntp_count=len(results[0].boxes.cls.tolist())-deteksi_bis
                            
                            ## PROSES INSERT TO DATABASE 
                            #class_deteksi="bis"
                            file_name = datetime.now().strftime("%d%m%Y_%H:%M:%S")
                            waktufile = datetime.now().strftime("%d%m%Y")
                            waktu_deteksi = datetime.now().strftime("%d%m%Y_%H_%M_%S")

                            #save pict
                            dir_pict_org=str(cur_dir)+"/image/IMG"+"_"+input_titik+"_"+file_name+".jpg"
                            cv2.imwrite(dir_pict_org, frame_kotak)

                            ## KOTAK SAVED PREDICT MOTOR
                            # result_cam=model.predict(frame_main, conf=0.6,verbose=False)
                            # frame_kotak= result_cam[0].plot(line_width=1, labels=True, conf=True)
                            #cv2.imwrite(dir_pict_org, frame_kotak)

                            ##save pict storage
                            dirpathlog = f"image_storage/{input_titik}/{waktufile}"
                            os.makedirs(dirpathlog, exist_ok=True)
                            dir_pict_org=str(cur_dir)+"/"+dirpathlog+"/IMG"+"_"+input_titik+"_"+file_name+".jpg"
                            cv2.imwrite(dir_pict_org, frame_kotak)
                            write_log(input_titik,"PICTURE SEPEDA CAPTURED")

                            #cv2.imwrite(dir_pict_org, masking_frame)
                            # cv2.imwrite(dir_pict_org, frame_kotak)
                            # write_log(input_titik,"PICTURE SEPEDA CAPTURED")

                            ## SAVE TO IMAGE DATASET
                            dir_pict_dataset=str(cur_dir)+"/image_dataset/IMG"+"_"+input_titik+"_"+file_name+".jpg"
                            cv2.imwrite(dir_pict_dataset, frame_main)
                            


                            ## directory gambar
                            dir_pict_org="/image/IMG"+"_"+str(input_titik)+"_"+file_name+".jpg"

                            ## directory video
                            dir_vid_org="/video/VID"+"_"+str(input_titik)+"_"+file_name+".webm"

                           
                            ## Inisialisasi mysql
                            try:
                                cnx=mysql.connector.connect(
                                    user=user_db,
                                    password=password_db,
                                    host=host_db,
                                    database=database_db
                                )

                                if cnx.is_connected():
                                    write_log(input_titik,"DATABASE CONNECTED TO MOTOR")

                            except:
                                write_log_error(input_titik,"DATABASE NOT CONNEDTED TO MOTOR")
                                pass

                            ## insert mysql
                            sql_insert="""INSERT INTO event (id_cctv,url_image,url_video,class,detection_object,waktu_deteksi) VALUES(%s,%s,%s,%s,%s,%s);"""
                            query_insert=(input_titik,dir_pict_org,dir_vid_org,"Sepeda/Motor",ntp_count,waktu_deteksi)
                            
                            try:
                                cursor=cnx.cursor()
                                write_log(input_titik,"START INSERTING TO MYSQL")
                                cursor.execute(sql_insert,query_insert)
                                cnx.commit()
                                write_log(input_titik,"SUCCESSED INSERTING TO MYSQL")
                            except:
                                write_log_error(input_titik,"NOT INSERTED TO DATABASE")
                                pass
                            
                            cnx.close()

                        if int(time.time() - start_time_bis) > DELAY_DETECTION:
                            flag_bis=1
                            get_fps_bis = True
                            
                            #write_log(input_titik,"END PROCESS RECORDING FRAME BIS")
                            write_log(input_titik,"FLAG SEPEDA SUDAH MENJADI 1 KEMBALI")

                        temp_id_bis=id_box_bis

                    ## DETEKSI ORANG
                    if person in results[0].boxes.cls.tolist():
                        motor=0
                        if bus in results[0].boxes.cls.tolist():
                            for i in results[0].boxes.cls.tolist():
                                if i == bus:
                                    deteksi_bis=deteksi_bis+1

                            ntp_count=len(results[0].boxes.cls.tolist())-deteksi_bis

                        elif bus not in results[0].boxes.cls.tolist():
                            ntp_count=len(results[0].boxes.cls.tolist())


                        id_box=results[0].boxes.data.tolist()[0][4]

                        if id_box!= temp_id and flag==1: 

                            write_log(input_titik,"ADA DETEKSI MOTOR")
                            
                            ## play sound untuk mode automatic
                            sound_thread.start()     

                            flag=0
                            start_time = time.time()
                            #class_deteksi="orang"
                            file_name = datetime.now().strftime("%d%m%Y_%H:%M:%S")
                            waktufile = datetime.now().strftime("%d%m%Y")
                            waktu_deteksi = datetime.now().strftime("%d%m%Y_%H_%M_%S")

                            ## save pict
                            dir_pict_org=str(cur_dir)+"/image/IMG"+"_"+input_titik+"_"+file_name+".jpg"
                            cv2.imwrite(dir_pict_org, frame_kotak)
                            #cv2.imwrite(dir_pict_org, frame_main)

                            ## KOTAK SAVED PREDICT MOTOR
                            # result_cam=model.predict(frame_main, conf=0.6,verbose=False)
                            # frame_kotak= result_cam[0].plot(line_width=1, labels=True, conf=True)
                            cv2.imwrite(dir_pict_org, frame_kotak)

                            ##save pict folder
                            dirpathlog = f"image_storage/{input_titik}/{waktufile}"
                            os.makedirs(dirpathlog, exist_ok=True)
                            dir_pict_org=str(cur_dir)+"/"+dirpathlog+"/IMG"+"_"+input_titik+"_"+file_name+".jpg"
                            cv2.imwrite(dir_pict_org, frame_kotak)
                            write_log(input_titik,"PICTURE MOTOR CAPTURED")

                            ## KOTAK SAVED PREDICT MOTOR
                            # result_cam=model.predict(frame_main, conf=0.6,verbose=False)
                            # frame_kotak= result_cam[0].plot(line_width=1, labels=True, conf=True)
                            # cv2.imwrite(dir_pict_org, frame_kotak)

                            ## SAVE TO IMAGE DATASET
                            dir_pict_dataset=str(cur_dir)+"/image_dataset/IMG"+"_"+input_titik+"_"+file_name+".jpg"
                            cv2.imwrite(dir_pict_dataset, frame_main)
                            
                            #cv2.imwrite(dir_pict_org, frame_main)
                            


                            ## Inisialisasi mysql
                            try:
                                cnx=mysql.connector.connect(
                                    user=user_db,
                                    password=password_db,
                                    host=host_db,
                                    database=database_db
                                )

                                if cnx.is_connected():
                                    write_log(input_titik,"DATABASE CONNECTED TO MOTOR")

                            except:
                                write_log_error(input_titik,"DATABASE NOT CONNEDTED TO MOTOR")
                                pass
                            
                            ## directory gambar
                            dir_pict_org="/image/IMG"+"_"+str(input_titik)+"_"+file_name+".jpg"

                            ## directory video
                            dir_vid_org="/video/VID"+"_"+str(input_titik)+"_"+file_name+".webm"

                           
                            ## insert mysql
                            sql_insert="""INSERT INTO event (id_cctv,url_image,url_video,class,detection_object,waktu_deteksi) VALUES(%s,%s,%s,%s,%s,%s);"""
                            query_insert=(input_titik,dir_pict_org,dir_vid_org,"Sepeda/Motor",ntp_count,waktu_deteksi)
                            
                            try:
                                cursor=cnx.cursor()
                                write_log(input_titik,"START INSERTING TO MYSQL")
                                cursor.execute(sql_insert,query_insert)
                                cnx.commit()
                                write_log(input_titik,"SUCCESSED INSERTING TO MYSQL")
                            except:
                                write_log_error(input_titik,"NOT INSERTED TO DATABASE")
                                pass
                            
                            cnx.close()

                            write_log(input_titik,"END TO INSERT MYSQL")


                        if int(time.time() - start_time) > DELAY_DETECTION:
                            flag=1
                            get_fps = True
                            write_log(input_titik,"FLAG MOTOR SUDAH MENJADI 1 KEMBALI")

                        temp_id=id_box

                ## RECORDING SEPEDA
                try:    
                    if flag==0 and int(time.time() - start_time) <= DELAY_DETECTION:
                        if get_fps == True:

                            ## Make folder sesuai waktu
                            waktufile = datetime.now().strftime("%d%m%Y")
                            dirvidlog = f"video_mp4/{input_titik}/{waktufile}"
                            os.makedirs(dirvidlog, exist_ok=True)

                            write_log(input_titik,"STARTING TO CAPTURE PROGRAM FRAME MOTOR")
                            get_fps = False

                            ## get fps dan resolusi video bis
                            fps = cap.get(cv2.CAP_PROP_FPS)
                            h, w, c = save_vid.shape
                            
                            ## starting to vid bener
                            #dir_vid_org="./video_mp4/VID"+"_"+str(input_titik)+"_"+file_name+".mp4"

                            dir_vid_org="./"+dirvidlog+"/VID"+"_"+str(input_titik)+"_"+file_name+".mp4"

                            ## bener
                            vid_writer = cv2.VideoWriter(dir_vid_org, cv2.VideoWriter_fourcc('D','I','V','X'), fps, (w, h))
                            write_log(input_titik,dir_vid_org)

                            write_log(input_titik,"GET RECORDING FRAME MOTOR")
                            

                        ## save vid output
                        try:
                            vid_writer.write(save_vid)
                        except:
                            write_log_error(input_titik,"FAILED GET RECORDING FRAME MOTOR")
                            pass


                        if int(time.time() - start_time) == DELAY_DETECTION:
                            flag=1
                            vid_writer.release()
                            get_fps = True

                            write_log(input_titik,"END PROCESS RECORDING FRAME MOTOR")
                            write_log(input_titik,"FLAG DETEKSI MOTOR SUDAH MENJADI 1 KEMBALI")
                except:
                    pass

                ## RECORDING BIS
                try:        
                    if flag_bis==0 and int(time.time() - start_time_bis) <= DELAY_DETECTION:
                        if get_fps_bis == True :

                            ## Make folder sesuai waktu
                            waktufile = datetime.now().strftime("%d%m%Y")
                            dirvidlog = f"video_mp4/{input_titik}/{waktufile}"
                            os.makedirs(dirvidlog, exist_ok=True)

                            write_log(input_titik,"STARTING TO CAPTURE PROGRAM FRAME SEPEDA")
                            get_fps_bis = False

                            ## get fps dan resolusi video bis
                            fps = cap.get(cv2.CAP_PROP_FPS)
                            h, w, c = save_vid.shape

                            ## starting to vid bener
                            #dir_vid_org="./video_mp4/VID"+"_"+str(input_titik)+"_"+file_name+".mp4"
                            
                            dir_vid_org="./"+dirvidlog+"/VID"+"_"+str(input_titik)+"_"+file_name+".mp4"
                            write_log(input_titik,dir_vid_org)

                            
                            ## bener
                            vid_writer_bis = cv2.VideoWriter(dir_vid_org, cv2.VideoWriter_fourcc('D','I','V','X'), fps, (w, h))

                            ##try
                            #vid_writer_bis = cv2.VideoWriter(dir_vid_org, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))

                            write_log(input_titik,"GET RECORDING FRAME SEPEDA")

                        ## output.write(frame)
                        try:
                            vid_writer_bis.write(save_vid)
                        except:
                            write_log_error(input_titik,"FAILED GET RECORDING FRAME SEPEDA")
                            pass

                        if int(time.time() - start_time_bis) == DELAY_DETECTION:
                            flag_bis=1
                            vid_writer_bis.release()
                            get_fps_bis = True

                            write_log(input_titik,"END PROCESS RECORDING FRAME SEPEDA")
                            write_log(input_titik,"FLAG SEPEDA SUDAH MENJADI 1 KEMBALI")
                except:
                    pass

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            else:
                write_log_error(input_titik,"OUT AI PROGRAM")
                break


        cap.release()
        cv2.destroyAllWindows()
        
