"""Face recognition module"""
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime
from app.sources.insightface_wrapper import InsightFaceWrapper
from app.config.settings import global_settings

logger = logging.getLogger(__name__)

class FaceRecognition:
    """Face recognition and matching"""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.insightface = InsightFaceWrapper()
        self.extracted_faces: Dict[str, List[Dict[str, Any]]] = {}
    
    def is_supported_image(self, image_path: str) -> bool:
        """
        Check if image format is supported
        
        Args:
            image_path: Path to image file
        
        Returns:
            True if supported, False otherwise
        """
        path = Path(image_path)
        return path.suffix.lower() in self.SUPPORTED_FORMATS
    
    def process_image(self, image_path: str, profile_id: str) -> Dict[str, Any]:
        """
        Process image and extract faces
        
        Args:
            image_path: Path to image file
            profile_id: Associated profile ID
        
        Returns:
            Processing result
        """
        image_path_obj = Path(image_path)
        
        if not image_path_obj.exists():
            self.logger.error(f"Image file not found: {image_path}")
            return {"success": False, "error": "File not found"}
        
        if not self.is_supported_image(image_path):
            self.logger.error(f"Unsupported image format: {image_path}")
            return {"success": False, "error": "Unsupported format"}
        
        try:
            faces = self.insightface.extract_faces(image_path)
            
            if not faces:
                self.logger.warning(f"No faces detected in {image_path}")
                return {
                    "success": True,
                    "image_path": str(image_path),
                    "faces_detected": 0,
                    "faces": []
                }
            
            self.extracted_faces[image_path] = faces
            
            result = {
                "success": True,
                "image_path": str(image_path),
                "profile_id": profile_id,
                "faces_detected": len(faces),
                "timestamp": datetime.now().isoformat(),
                "faces": [{
                    "face_id": f.get("face_id"),
                    "confidence": f.get("det_score"),
                    "age": f.get("age"),
                    "gender": f.get("gender"),
                    "bbox": f.get("bbox"),
                } for f in faces]
            }
            
            self.logger.info(f"Processed {image_path}: {len(faces)} faces found")
            return result
        
        except Exception as e:
            self.logger.error(f"Error processing image: {e}")
            return {"success": False, "error": str(e)}
    
    def match_faces(self, image_path1: str, image_path2: str, 
                   threshold: float = 0.6) -> List[Dict[str, Any]]:
        """
        Match faces between two images
        
        Args:
            image_path1: First image path
            image_path2: Second image path
            threshold: Similarity threshold
        
        Returns:
            List of matching results
        """
        if image_path1 not in self.extracted_faces:
            faces1 = self.insightface.extract_faces(image_path1)
            self.extracted_faces[image_path1] = faces1
        else:
            faces1 = self.extracted_faces[image_path1]
        
        if image_path2 not in self.extracted_faces:
            faces2 = self.insightface.extract_faces(image_path2)
            self.extracted_faces[image_path2] = faces2
        else:
            faces2 = self.extracted_faces[image_path2]
        
        if not faces1 or not faces2:
            return []
        
        matches = []
        
        for face1 in faces1:
            if 'embedding' not in face1 or not face1['embedding']:
                continue
            
            match = self.insightface.find_matching_face(
                face1['embedding'],
                faces2,
                threshold
            )
            
            if match:
                matches.append({
                    "face1_id": face1['face_id'],
                    "face2_id": match['face_id'],
                    "match_score": match['match_score'],
                    "image1": str(image_path1),
                    "image2": str(image_path2),
                })
        
        self.logger.info(f"Found {len(matches)} matching faces")
        return matches
    
    def save_face_data(self, profile_id: str, face_data: Dict[str, Any]) -> bool:
        """
        Save face data to profile
        
        Args:
            profile_id: Profile ID
            face_data: Face data to save
        
        Returns:
            True if successful, False otherwise
        """
        try:
            profiles_dir = Path(global_settings.get("data_dir"))
            face_dir = profiles_dir / profile_id / "face"
            face_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            face_file = face_dir / f"face_data_{timestamp}.json"
            
            with open(face_file, 'w', encoding='utf-8') as f:
                json.dump(face_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Face data saved: {face_file}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error saving face data: {e}")
            return False
    
    def clear_cache(self):
        """Clear extracted faces cache"""
        self.extracted_faces.clear()
        self.logger.info("Cleared face cache")
