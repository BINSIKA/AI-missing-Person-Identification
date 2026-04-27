import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np

class ReIDModel:
    def __init__(self, device=None):
        """
        Initialize Re-ID model using ResNet50
        """
       self.device = 'cpu'

        
        # Load pre-trained ResNet50
        self.model = models.resnet50(pretrained=True)
        self.model.fc = nn.Identity()  # remove the classification head
        self.model = self.model.to(self.device)
        self.model.eval()
        
        # Define preprocessing steps
        self.transform = transforms.Compose([
            transforms.Resize((256, 128)),  # Standard input size for Re-ID
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])
    
    def extract_features(self, image_path):
        """
        Extract feature vector from an image
        """
        image = Image.open(image_path).convert('RGB')
        image = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            features = self.model(image).cpu().numpy().flatten()
        return features

    def compute_similarity(self, feature1, feature2):
        """
        Compute Euclidean distance between two feature vectors
        """
        return np.linalg.norm(feature1 - feature2)

    def match_person(self, query_path, gallery_paths, threshold=50.0):
        """
        Match a query image against a list of gallery images.

        :param query_path: Path to the query image
        :param gallery_paths: List of image paths in the database
        :param threshold: Maximum distance to consider a match
        :return: (best_match_path, distance) or (None, None)
        """
        query_features = self.extract_features(query_path)
        best_match = None
        min_distance = float('inf')

        for g_path in gallery_paths:
            gallery_features = self.extract_features(g_path)
            distance = self.compute_similarity(query_features, gallery_features)
            
            if distance < min_distance:
                min_distance = distance
                best_match = g_path

        if min_distance <= threshold:
            return best_match, min_distance
        else:
            return None, None

# Example Usage
if __name__ == "__main__":
    reid = ReIDModel()
    
    query_img = "static/uploads/query.jpg"
    gallery = [
        "static/uploads/person1.jpg",
        "static/uploads/person2.jpg",
        "static/uploads/person3.jpg"
    ]
    
    match, dist = reid.match_person(query_img, gallery)
    
    if match:
        print(f"[MATCH FOUND] Closest person: {match}, Distance: {dist:.2f}")
    else:
        print("[NO MATCH] Person not found in gallery")
