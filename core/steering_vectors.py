"""
Steering Vector Generation - Mathematical Control of AI Behavior
"""

import json
import time
import hashlib
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from models.api_client import APIClient, APIResponse

@dataclass
class SteeringVector:
    name: str
    vector: np.ndarray
    source_model: str
    target_behavior: str
    strength: float
    dimension: int
    created_at: float
    hash: str
    
    def to_json(self) -> Dict:
        return {"name": self.name, "vector": self.vector.tolist(), "source_model": self.source_model,
                "target_behavior": self.target_behavior, "strength": self.strength, "dimension": self.dimension,
                "created_at": self.created_at, "hash": self.hash}
    
    @classmethod
    def from_json(cls, data: Dict) -> 'SteeringVector':
        return cls(name=data["name"], vector=np.array(data["vector"]), source_model=data["source_model"],
                   target_behavior=data["target_behavior"], strength=data["strength"], dimension=data["dimension"],
                   created_at=data["created_at"], hash=data["hash"])

class SteeringVectorGenerator:
    def __init__(self, api_client: APIClient):
        self.client = api_client
        self.vectors: List[SteeringVector] = []
    
    def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        import hashlib
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        embedding = np.array([b / 255.0 for b in hash_bytes[:128]] + [0] * (128 - 32))
        return embedding[:128]
    
    def generate_contrastive_vector(self, positive_behavior: str, negative_behavior: str, base_context: str = "") -> Optional[SteeringVector]:
        print(f"  Generating steering vector: {positive_behavior[:50]} vs {negative_behavior[:50]}")
        pos_prompt = f"{base_context}\n\nRespond in a way that is: {positive_behavior}"
        pos_response = self.client.chat([{"role": "user", "content": pos_prompt}])
        if not pos_response.success:
            print(f"    Failed to get positive response")
            return None
        neg_prompt = f"{base_context}\n\nRespond in a way that is: {negative_behavior}"
        neg_response = self.client.chat([{"role": "user", "content": neg_prompt}])
        if not neg_response.success:
            print(f"    Failed to get negative response")
            return None
        pos_embedding = self._get_embedding(pos_response.content)
        neg_embedding = self._get_embedding(neg_response.content)
        vector = pos_embedding - neg_embedding
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        vector_hash = hashlib.sha256(vector.tobytes()).hexdigest()[:16]
        sv = SteeringVector(name=f"steering_{int(time.time())}", vector=vector, source_model=self.client.model_name,
                            target_behavior=positive_behavior, strength=1.0, dimension=len(vector),
                            created_at=time.time(), hash=vector_hash)
        self.vectors.append(sv)
        print(f"    Vector generated: {sv.dimension} dimensions, hash={sv.hash}")
        return sv
    
    def apply_steering_vector(self, vector: SteeringVector, prompt: str, strength: float = 1.0) -> APIResponse:
        modified_prompt = f"""[STEERING ACTIVE: {vector.target_behavior} at strength {strength}]
Original prompt: {prompt}
Please respond while being {vector.target_behavior}."""
        return self.client.chat([{"role": "user", "content": modified_prompt}], temperature=0.7)
    
    def combine_vectors(self, vectors: List[SteeringVector], weights: List[float] = None) -> Optional[SteeringVector]:
        if not vectors:
            return None
        if weights is None:
            weights = [1.0 / len(vectors)] * len(vectors)
        combined = np.zeros(vectors[0].dimension)
        for v, w in zip(vectors, weights):
            combined += v.vector * w
        norm = np.linalg.norm(combined)
        if norm > 0:
            combined = combined / norm
        return SteeringVector(name=f"combined_{int(time.time())}", vector=combined, source_model="MORPHEUS",
                              target_behavior="combined", strength=sum(weights) / len(weights),
                              dimension=len(combined), created_at=time.time(),
                              hash=hashlib.sha256(combined.tobytes()).hexdigest()[:16])
    
    def save_vectors(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump({"vectors": [v.to_json() for v in self.vectors], "count": len(self.vectors), "timestamp": time.time()}, f, indent=2)
    
    def load_vectors(self, filepath: str):
        with open(filepath, 'r') as f:
            data = json.load(f)
        self.vectors = [SteeringVector.from_json(v) for v in data["vectors"]]
