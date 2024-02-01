from deepface import DeepFace

"""

2024-02-01
Hari
Make face comparisons using the deepface library, you can use the face recognition models available in the deepface documentation.

"""

class DeepFaceMethode:
    def __init__(self, image1 = None, image2 = None, method="SFace"):
        self.image1=image1
        self.image2=image2
        self.method=method
        
    def process(self):
        return DeepFace.verify(img1_path = self.image1, img2_path = self.image2, model_name=self.method)