import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.models import Model
from tensorflow.keras.layers import GlobalAveragePooling2D
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
from PIL import Image
import io

class SkinLesionValidator:
    def __init__(self, reference_dataset_path=None):
        # Load pretrained model without classification layer
        base_model = ResNet50(weights="imagenet", include_top=False, input_shape=(128, 128, 3))
        x = GlobalAveragePooling2D()(base_model.output)
        self.feature_extractor = Model(inputs=base_model.input, outputs=x)
        
        # Initialize reference features
        self.reference_features = None
        if reference_dataset_path:
            self.load_reference_dataset(reference_dataset_path)
    
    def load_reference_dataset(self, folder_paths):
        """
        Load a sample of reference HAM10000 images and extract their features.
        
        Args:
            folder_paths: List of paths to folders containing HAM10000 images.
        """
        if not isinstance(folder_paths, list):
            folder_paths = [folder_paths]
        
        reference_features = []
        sample_count = 0
        max_samples = 100  # Adjust the maximum number of samples if needed
        
        # Process images from each provided folder
        for folder in folder_paths:
            if not os.path.exists(folder):
                print(f"Warning: Folder {folder} does not exist")
                continue
                
            files = [f for f in os.listdir(folder) if f.endswith('.jpg')]
            # Take a sample of files from each folder
            sample_files = files[:min(len(files), max_samples // len(folder_paths))]
            
            for file in sample_files:
                try:
                    image_path = os.path.join(folder, file)
                    features = self.extract_features(image_path)
                    reference_features.append(features)
                    sample_count += 1
                except Exception as e:
                    print(f"Error processing {file}: {e}")
        
        if reference_features:
            self.reference_features = np.vstack(reference_features)
            print(f"Loaded {sample_count} reference images")
        else:
            print("No reference features could be loaded")
    
    def extract_features(self, image_path_or_data):
        """
        Extract features from an image using the pretrained model.
        
        Args:
            image_path_or_data: Either a path to an image file or image data (PIL Image or bytes).
        
        Returns:
            np.array: Feature vector for the image.
        """
        # Handle different input types
        if isinstance(image_path_or_data, str):
            # Input is a file path
            img = load_img(image_path_or_data, target_size=(128, 128))
        elif isinstance(image_path_or_data, Image.Image):
            # Input is a PIL Image
            img = image_path_or_data.resize((128, 128))
        elif isinstance(image_path_or_data, bytes):
            # Input is bytes data
            img = Image.open(io.BytesIO(image_path_or_data))
            img = img.resize((128, 128))
        else:
            raise ValueError("Unsupported image input type")
        
        # Convert image to array and preprocess it
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        # Extract features using the feature extractor model
        features = self.feature_extractor.predict(img_array, verbose=0)
        return features
    
    def is_skin_lesion(self, image_path_or_data, similarity_threshold=0.4):
        """
        Check if an image is likely to be a skin lesion by comparing it to reference images.
        
        Args:
            image_path_or_data: Path to image file or image data.
            similarity_threshold: Threshold for considering an image relevant (0-1).
            
        Returns:
            tuple: (is_relevant, similarity_score, message)
        """
        if self.reference_features is None:
            return False, 0, "Reference dataset not loaded"
        
        try:
            # Extract features from the test image
            test_features = self.extract_features(image_path_or_data)
            
            # Calculate cosine similarities to all reference images
            similarities = cosine_similarity(test_features, self.reference_features)[0]
            
            # Get the maximum similarity
            max_similarity = np.max(similarities)
            
            # Determine if the image is relevant based on the threshold
            is_relevant = max_similarity >= similarity_threshold
            
            if is_relevant:
                message = f"Image appears to be a skin lesion (similarity: {max_similarity:.2f})"
            else:
                message = f"Image does not appear to be a skin lesion (similarity: {max_similarity:.2f})"
                
            return is_relevant, max_similarity, message
            
        except Exception as e:
            return False, 0, f"Error processing image: {str(e)}"
    
    def visualize_comparison(self, image_path_or_data, output_path=None):
        """
        Visualize the test image alongside the most similar reference images.
        
        Args:
            image_path_or_data: Path to test image or image data.
            output_path: Optional path to save the visualization.
            
        Returns:
            PIL.Image: Visualization image.
        """
        if self.reference_features is None:
            print("Reference dataset not loaded")
            return None
        
        try:
            # Extract features from the test image
            test_features = self.extract_features(image_path_or_data)
            
            # Calculate similarities to all reference images
            similarities = cosine_similarity(test_features, self.reference_features)[0]
            
            # Get indices of the top 5 most similar images
            top_indices = np.argsort(similarities)[-5:][::-1]
            
            # Load the test image
            if isinstance(image_path_or_data, str):
                test_img = Image.open(image_path_or_data)
            elif isinstance(image_path_or_data, Image.Image):
                test_img = image_path_or_data
            elif isinstance(image_path_or_data, bytes):
                test_img = Image.open(io.BytesIO(image_path_or_data))
            
            # TODO: Implement detailed visualization (requires storing reference image paths)
            return test_img, similarities[top_indices], top_indices
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return None

# Example usage (for testing purposes)
if __name__ == "__main__":
    folder1 = r"C:\Users\Emrehan\Desktop\ham10000_dataset\HAM10000_images_part_1"
    folder2 = r"C:\Users\Emrehan\Desktop\ham10000_dataset\HAM10000_images_part_2"
    
    validator = SkinLesionValidator()
    validator.load_reference_dataset([folder1, folder2])
    
    test_image_path = r"C:\Users\Emrehan\Desktop\ham10000_dataset\HAM10000_images_part_1\ISIC_0024306.jpg"  # Update with an actual image path
    is_relevant, similarity, message = validator.is_skin_lesion(test_image_path)
    print(message)
