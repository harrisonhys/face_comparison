import app.controller.lib.face_recognition as face_recognition
import cv2

class FaceRecognitionMethode:
    def __init__(self, image1 = None, image2 = None):
        self.image1=image1
        self.image2=image2
        
    def find_face_encodings(image_path):
        image = cv2.imread(image_path)
        face_enc = face_recognition.face_encodings(image)
        return face_enc[0]
        
    def process(self):
        image_1 = self.find_face_encodings(self.image1)
        image_2  = self.find_face_encodings(self.image2)
        result = {
            'is_same_person' : False,
            'accuracy' : 0
        }
        try:
            is_same = face_recognition.compare_faces([image_1], image_2)[0]
            result.update({'is_same_person' : is_same})
            if is_same:
                distance = face_recognition.face_distance([image_1], image_2)
                distance = round(distance[0] * 100)
                accuracy = 100 - round(distance)
                result.update({'accuracy' : accuracy})
            else:
                print("The images are not same")
        except Exception as error:
            print("An exception occurred:", error)
            
        return result