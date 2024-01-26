import psycopg2
import json
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
from app.controller.lib.face_recognition import FaceRecognitionMethode


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
            
    def processFaceRecognition(self, no_pensiun, file):
        
        log             = DailyLogger()
        
        query_skd       = "SELECT * FROM data_skd WHERE no_pensiun = %s order by id desc LIMIT 1"
        result_skd      = self.select(query_skd, (no_pensiun,))
        
        if(len(result_skd) == 0) :
            raise HTTPException(status_code=404, detail="SKD Tidak ditemukan")
        
        query_files     = "SELECT * FROM files WHERE model_id = %s AND type='photo' order by id desc LIMIT 1"
        result_files    = self.select(query_files, (result_skd[0]['id'],))
        
        if(len(result_files) == 0) :
            raise HTTPException(status_code=404, detail="Photo Tidak ditemukan")
        
        result          = {
            'skd'  : result_skd[0],
            'file' : result_files[0],
            'result' : None
        }
        
        unique_id       = uuid.uuid4()
        
        file_path = 'app/photos_compare/'+str(unique_id)+'.'+file.filename.split('.')[1]
        with open(file_path, "wb") as local_file:
            local_file.write(file.file.read())
        
        remote_path     = "files/"+result_files[0]['attachment']
        local_path      = "app/photos/"+str(unique_id)+".png"
        
        ftp_downloader  = FTPDownloader(self.ftp_host, self.ftp_username, self.ftp_password)
        ftp_downloader.connect()
        ftp_downloader.download_file(remote_path, local_path)
        ftp_downloader.disconnect()
        
        fr  = DeepFaceMethode(local_path, file_path)  
        res = fr.process()  
        
        # frc = FaceRecognitionMethode(local_path, file_path)
        # res = frc.process()
        
        result.update({'result' : res})
        
        self.delete_file(local_path)
        self.delete_file(file_path)
        
        res_data = {
            'no_pensiun' : no_pensiun,  
            'penerima_mp' : result_skd[0]['nama_penerima'], 
            'data_pembanding' : 'skd', 
            'data_tahun' : result_skd[0]['tahun_pelaporan'], 
            'data_id' : result_skd[0]['id'], 
            'result' : res
            }
        
        log.make_log(res_data)
        
        return res_data
 
    def delete_file(self, file):
        if os.path.exists(file):
            os.remove(file)
