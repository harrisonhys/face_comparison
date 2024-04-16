from deepface import DeepFace

"""

2024-04-16
Hari
Get information about age, gender, race and emotion from photos

"""

class DeepFaceAnalyse:
    def __init__(self, image = None):
        self.image=image
        
    def analyze(self):
        return DeepFace.analyze(img_path = self.image, actions = ['age', 'gender', 'race', 'emotion'])
    