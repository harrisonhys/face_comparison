import psycopg2
import json
import ast
import datetime
import pandas as pd
from ftplib import FTP
import os
import uuid
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.controller.environment_config import EnvironmentConfig
from app.controller.lib.ftp_downloader import FTPDownloader
from fastapi import HTTPException
from app.controller.lib.deep_face_recognition import DeepFaceMethode
from app.controller.lib.logger import DailyLogger


class Recognition:
    db_host         = EnvironmentConfig.get_env_value('DB_HOST', default='localhost')
    db_port         = EnvironmentConfig.get_env_value('DB_PORT', default=5432)
    db_user         = EnvironmentConfig.get_env_value('DB_USER', default='postgres')
    db_name         = EnvironmentConfig.get_env_value('DB_NAME', default='test')
    db_pass         = EnvironmentConfig.get_env_value('DB_PASS', default=12345)
    ftp_host        = EnvironmentConfig.get_env_value('FTP_DO_HOST', default='localhost')
    ftp_username    = EnvironmentConfig.get_env_value('FTP_DO_USERNAME', default='username')
    ftp_password    = EnvironmentConfig.get_env_value('FTP_DO_PASSWORD', default='')
    
    def __init__(self,val = None):
        self.val=val
        
    def connect(self):
        try:
            conn = psycopg2.connect(host=self.db_host, user=self.db_user, password=self.db_pass, database=self.db_name)
            return conn
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            return None
        
    def select(self, query, values=None):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                if values:
                    cursor.execute(query, values)
                else:
                    cursor.execute(query)
                data = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                result = [dict(zip(columns, row)) for row in data]
                return result
            except Exception as e:
                print(f"Error executing query: {e}")
            finally:
                cursor.close()
                conn.close()
        return None
        
    def serialize_datetime(self,obj): 
        if isinstance(obj, datetime.datetime): 
            return obj.isoformat() 
        raise TypeError("Type not serializable") 
    
    def save_file(local_path, file):
        try:
            file_path = local_path / file.filename
            with open(file_path, "wb") as local_file:
                local_file.write(file.file.read())
            print(f"Downloaded {file.file_name} to {local_path}")
        except Exception as e:
            print(f"Error saving file: {e}")
            
    def processFaceRecognition(self, no_pensiun, file, method = 'FaceNet'):
        
        log             = DailyLogger()
        
        # Find last otentikasi record
        query_skd       = "SELECT * FROM data_skd WHERE no_pensiun = %s AND status=2 order by id desc LIMIT 1"
        result_skd      = self.select(query_skd, (no_pensiun,))
        
        if(len(result_skd) == 0) :
            raise HTTPException(status_code=404, detail={"message" : "SKD Tidak ditemukan"})
        
        # Retrieve photos on the file server
        query_files     = "SELECT * FROM files WHERE model_id = %s AND type='photo' order by id desc LIMIT 1"
        result_files    = self.select(query_files, (result_skd[0]['id'],))
        
        if(len(result_files) == 0) :
            raise HTTPException(status_code=404, detail={"message" : "Foto Tidak ditemukan"})
        
        result          = {
            'skd'  : result_skd[0],
            'file' : result_files[0],
            'result' : None
        }
        
        unique_id       = uuid.uuid4()
        
        # Save photos to local path
        file_path = 'app/photos_compare/'+str(unique_id)+'.'+file.filename.split('.')[1]
        with open(file_path, "wb") as local_file:
            local_file.write(file.file.read())
        
        remote_path     = "files/"+result_files[0]['attachment']
        local_path      = "app/photos/"+str(unique_id)+".png"
        
        ftp_downloader  = FTPDownloader(self.ftp_host, self.ftp_username, self.ftp_password)
        ftp_downloader.connect()
        ftp_downloader.download_file(remote_path, local_path)
        ftp_downloader.disconnect()
        
        # Comparing between two images
        try:
            fr  = DeepFaceMethode(local_path, file_path, method)  
            res = fr.process()  
        except Exception as e:
            self.delete_file(local_path)
            self.delete_file(file_path)
            raise HTTPException(status_code=422, detail={"message" : "Gambar tidak valid, resolusi terlalu rendah atau tidak ada objek wajah terdeteksi", "errors" : str(e)})
        
        result.update({'result' : res})
        
        self.delete_file(local_path)
        self.delete_file(file_path)
        
        res_data = {
            'no_pensiun' : no_pensiun,  
            'penerima_mp' : result_skd[0]['nama_penerima'], 
            'data_pembanding' : 'skd', 
            'data_tahun' : result_skd[0]['tahun_pelaporan'], 
            'data_id' : result_skd[0]['id'], 
            'accuracy' : 100-(res['distance']*100),
            'result' : res
        }
        
        log.make_log(res_data)
        
        return res_data
 
    def delete_file(self, file):
        if os.path.exists(file):
            os.remove(file)
            
    def clearLog(self, tanggal):
        file = "app/log/log_"+tanggal+".log"
        if os.path.exists(file):
            os.remove(file)
    
    def getLog(self):
        try:
            # Get the list of files in the specified path
            file_names = [f for f in os.listdir('app/log/') if os.path.isfile(os.path.join('app/log/', f))]
            return {
                'count' : len(file_names),
                'log' : file_names
            }
        except Exception as e:
            print(f"Error retrieving file names: {e}")
            return []
    
    def geDetailLog(self, tanggal):
        file_path = "app/log/log_"+tanggal+".log"
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                # Convert each line to a list array
                data_list = [self.parse_line(line) for line in lines]
            return {
                'log' : data_list,
                'count' : len(data_list)
            }
        except Exception as e:
            print(f"Error reading file: {e}")
            return []
    
    def parse_line(self, line):
        try:
            # Parse the string representation of the dictionary into a dictionary
            data_dict = ast.literal_eval(line.split(' ', 2)[2])
            return data_dict
        except Exception as e:
            print(f"Error parsing line: {e}")
            return None
        
    def compareTwoFace(self, img1, img2, method = "SFace"):
        img1_path = 'app/photos/'+str(uuid.uuid4())+'.'+img1.filename.split('.')[1]
        img2_path = 'app/photos_compare/'+str(uuid.uuid4())+'.'+img2.filename.split('.')[1]
        
        with open(img1_path, "wb") as local_file:
            local_file.write(img1.file.read())
        with open(img2_path, "wb") as local_file:
            local_file.write(img2.file.read())
            
        # Comparing between two images
        try:
            fr  = DeepFaceMethode(img1_path, img2_path, method)  
            res = fr.process() 
            res["accuracy"] = 100-(res['distance']*100)
            return res
        except Exception as e:
            self.delete_file(img1_path)
            self.delete_file(img2_path)
            raise HTTPException(status_code=422, detail={"message" : "Gambar tidak valid, resolusi terlalu rendah atau tidak ada objek wajah terdeteksi", "errors" : str(e)})
        
        self.delete_file(img1_path)
        self.delete_file(img2_path)