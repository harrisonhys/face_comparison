from ftplib import FTP
class FTPDownloader:
    
    def __init__(self, host, username, password ):
        self.host = host
        self.username = username
        self.password = password
        self.ftp = None

    def connect(self):
        try:
            self.ftp = FTP(self.host)
            self.ftp.login(self.username, self.password)
        except Exception as e:
            print(f"Error connecting to FTP server: {e}")

    def download_file(self, remote_path, local_path):
        try:
            with open(local_path, 'wb') as file:
                self.ftp.retrbinary(f"RETR {remote_path}", file.write)
        except Exception as e:
            print(f"Error downloading file: {e}")

    def disconnect(self):
        try:
            self.ftp.quit()
        except Exception as e:
            print(f"Error disconnecting from FTP server: {e}")