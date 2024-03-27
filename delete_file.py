from pathlib import Path
import datetime as dt
from time import ctime
import mysql.connector
import os



#GET DATA FROM ENV####
import ast
f = open('./config.txt', 'r')
api=f.read()
dictapi = ast.literal_eval(api)
nocctv=str(dictapi['nocctv'])
print(nocctv)

remove_before = dt.datetime.now()-dt.timedelta(days=10) #files older than 10 days
print(remove_before.strftime("%d%m%Y"))
waktufile=remove_before.strftime("%d%m%Y")


try:
    sintax="rm -r /home/aicctv/Project/Motor/video_mp4/"+ nocctv +"/"+ waktufile
    sintax2="rm -r /home/aicctv/Project/Motor/image_storage/"+nocctv +"/"+ waktufile
except:
    pass

print(sintax)
print(sintax2)
os.system(sintax+";")
os.system(sintax2+";")








