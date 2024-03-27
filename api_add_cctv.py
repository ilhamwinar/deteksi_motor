from fastapi import FastAPI,Form
import uvicorn
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import os
import logging
import sys
from datetime import datetime
import mysql.connector


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"])

#inisialisasi logging
file_handler = logging.FileHandler(filename="./log_server_api.log")
stdout_handler = logging.StreamHandler(stream=sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s [%(levelname)s] - %(message)s',
    handlers=handlers,
    datefmt="%m/%d/%Y %H:%M:%S",
)
logger = logging.getLogger('LOGGER_NAME')

def make_word(script_path,script_content):
    with open("myscript.sh", "w") as script_path:
        script_path.write(script_content)

def add_newline(script_path,line_to_add):
    try:
        with open(script_path, "a") as script_file:
            script_file.write("\n" + line_to_add)
        print(f"Line has been successfully added to '{script_path}'.")
    except FileNotFoundError:
        print(f"Script '{script_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


def delete_word(script_path,word_to_remove):
    try:
        with open(script_path, "r") as script_file:
            lines = script_file.readlines()

        # Remove lines containing the specified text
        modified_lines = [line.replace(word_to_remove, "") for line in lines]

        with open(script_path, "w") as script_file:
            script_file.writelines(modified_lines)

        print(f"Text '{word_to_remove}' has been successfully removed from '{script_path}'.")
    except FileNotFoundError:
        print(f"Script '{script_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def delete_lines_and_following(file_path, target_word, lines_to_delete=5):
    # Read the contents of the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Find lines containing the target word and delete them along with the following lines
    modified_lines = []
    skip_next_lines = 0
    for line in lines:
        if target_word in line:
            # Skip this line and the following lines_to_delete lines
            skip_next_lines = lines_to_delete
        elif skip_next_lines > 0:
            # Skip this line
            skip_next_lines -= 1
        else:
            modified_lines.append(line)

    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.writelines(modified_lines)

    print(f"Lines containing '{target_word}' and the next {lines_to_delete} lines deleted successfully.")

@app.get("/reboot")
async def reboot_pc():
    os.system("reboot")
    return {"message": "berhasil perintah restart service cctv"}


@app.get("/create_cctv")
async def create_cctv():
    os.system("python3 create_list.py;")
    return {"message": "berhasil menambah cctv"}


def convert_mp4_to_webm(input_vid,output_vid):
    sintax="python3 coba.py --input "+str(input_vid)+" --output "+str(output_vid)
    os.system(sintax+";")

#@app.post("/convert_to_webm")

@app.get("/convert_to_webm/{waktu}/")
async def convert_vid(waktu: str):

    import ast
    f = open('./config.txt', 'r')
    api=f.read()
    dictapi = ast.literal_eval(api)
    nocctv=str(dictapi['nocctv'])
    print(nocctv)

    # convert to webm
    logging.info("STARTING TO CONVERT TO webm")
    logging.info(nocctv)
    logging.info(waktu)
    waktu=waktu.split("_")
    logging.info(waktu)
    waktu_str=waktu[0]+"_"+waktu[1]+":"+waktu[2]+":"+waktu[3]

    waktufile = waktu[0]
    dirvidlog = f"video_mp4/{nocctv}/{waktufile}"

    #dir_vid_org="./video_mp4/VID_"+str(nocctv)+"_"+str(waktu)+".mp4"
    dir_vid_org="./"+dirvidlog+"/VID"+"_"+str(nocctv)+"_"+str(waktu_str)+".mp4"
    logging.info(dir_vid_org)
    dir_vid_org_webm="./video/VID_"+str(nocctv)+"_"+str(waktu_str)+".webm"
    
    logging.info(dir_vid_org)
    logging.info(dir_vid_org_webm)
    check_file = os.path.isfile(dir_vid_org)
    logging.info(check_file)

    check_file = os.path.isfile(dir_vid_org_webm)

    if check_file==False:
        try:
            convert_mp4_to_webm(dir_vid_org, dir_vid_org_webm)
            pesan="berhasil convert CCTV"
        except:
            logging.error("ERROR")
            pesan="gagal convert"
            pass
    else:
        pesan="file sudah ada"

    return {"message": pesan}

if __name__ == "__main__":
    uvicorn.run("api_add_cctv:app",host="0.0.0.0",port=8300,reload=True)