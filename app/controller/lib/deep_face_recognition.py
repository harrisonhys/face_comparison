import os
os.environ["CUDA_VISIBLE_DEVICES"]=""
from deepface import DeepFace

class DeepFaceMethode:
    def __init__(self, image1 = None, image2 = None):
        self.image1=image1
        self.image2=image2
        
    def process(self):
        return DeepFace.verify(img1_path = self.image1, img2_path = self.image2, model_name="SFace")