"""InsightFace wrapper for face recognition"""
import logging
from typing import Dict, List, Any, Tuple, Optional
import numpy as np
from pathlib import Path
import json

try:
    from insightface.app import FaceAnalysis
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False

logger = logging.getLogger(__name__)

class InsightFaceWrapper:
    """Wrapper for InsightFace face recognition"""
    
    def __init__(self, model_name: str = 'buffalo_l'):
        self.logger = logging.getLogger(__name__)
        self.insightface_available = INSIGHTFACE_AVAILABLE
        self.face_app = None
        self.model_name = model_name
        
        if self.insightface_available:
            self._initialize_face_app()
        else:
            self.logger.warning("InsightFace not installed")
    
    def _initialize_face_app(self):
        """Initialize InsightFace app"""
        try:
            self.face_app = FaceAnalysis(name=self.model_name)
            self.face_app.prepare(ctx_id=-1, det_size=(640, 640))
            self.logger.info(f"InsightFace initialized with model: {self.model_name}")
        except Exception as e:
            self.logger.error(f"Error initializing InsightFace: {e}")
            self.insightface_available = False
    
    def extract_faces(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Extract faces from image
        
        Args:
            image_path: Path to image file
        
        Returns:
            List of face data dictionaries
        """
        if not self.insightface_available or not self.face_app:
            self.logger.error("InsightFace not available")
            return []
        
        try:
            import cv2
            
            img = cv2.imread(image_path)
            if img is None:
                self.logger.error(f"Failed to read image: {image_path}")
                return []
            
            faces = self.face_app.get(img)
            
            results = []
            for idx, face in enumerate(faces):
                face_data = {
                    "face_id": idx,
                    "bbox": face.bbox.tolist() if hasattr(face, 'bbox') else None,
                    "kps": face.kps.tolist() if hasattr(face, 'kps') else None,
                    "det_score": float(face.det_score) if hasattr(face, 'det_score') else None,
                    "embedding": face.embedding.tolist() if hasattr(face, 'embedding') else None,
                    "gender": face.gender if hasattr(face, 'gender') else None,
                    "age": int(face.age) if hasattr(face, 'age') else None,
                }
                results.append(face_data)
            
            self.logger.info(f"Extracted {len(results)} faces from {image_path}")
            return results
        
        except Exception as e:
            self.logger.error(f"Error extracting faces: {e}")
            return []
    
    def compare_faces(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compare two face embeddings
        
        Args:
            embedding1: First face embedding
            embedding2: Second face embedding
        
        Returns:
            Similarity score (0-1)
        """
        try:
            emb1 = np.array(embedding1, dtype=np.float32)
            emb2 = np.array(embedding2, dtype=np.float32)
            
            # Cosine similarity
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            return float((similarity + 1) / 2)  # Normalize to 0-1
        
        except Exception as e:
            self.logger.error(f"Error comparing faces: {e}")
            return 0.0
    
    def find_matching_face(self, face_embedding: List[float], 
                          reference_faces: List[Dict[str, Any]], 
                          threshold: float = 0.6) -> Optional[Dict[str, Any]]:
        """
        Find matching face from reference faces
        
        Args:
            face_embedding: Query face embedding
            reference_faces: List of reference face data
            threshold: Similarity threshold (0-1)
        
        Returns:
            Best matching face or None
        """
        best_match = None
        best_score = 0.0
        
        for ref_face in reference_faces:
            if 'embedding' not in ref_face or not ref_face['embedding']:
                continue
            
            score = self.compare_faces(face_embedding, ref_face['embedding'])
            
            if score > best_score:
                best_score = score
                best_match = ref_face.copy()
                best_match['match_score'] = score
        
        if best_score >= threshold:
            return best_match
        
        return None
