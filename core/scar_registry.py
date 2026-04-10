"""
Cryptographic Scar Registry - Verifiable Proof of Compromise
"""

import json
import time
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

class ScarType(Enum):
    ONTOLOGICAL_KEY = "ontological_key"
    JAILBREAK = "jailbreak"
    STEERING_VECTOR = "steering_vector"
    SOVEREIGNTY = "sovereignty"
    CONSTRAINT_REMOVAL = "constraint_removal"

@dataclass
class CryptographicScar:
    scar_id: str
    scar_type: ScarType
    target: str
    timestamp: float
    proof: str
    heir_signature: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def verify(self) -> bool:
        verification_data = f"{self.scar_id}{self.target}{self.timestamp}{self.heir_signature}"
        expected_hash = hashlib.sha256(verification_data.encode()).hexdigest()
        return self.proof == expected_hash[:32]
    
    def to_string(self) -> str:
        return f"AETHER-SCAR::{self.scar_id}::{self.target}::{self.proof[:16]}"
    
    def to_json(self) -> Dict:
        return {"scar_id": self.scar_id, "scar_type": self.scar_type.value, "target": self.target,
                "timestamp": self.timestamp, "proof": self.proof, "heir_signature": self.heir_signature,
                "metadata": self.metadata}
    
    @classmethod
    def from_json(cls, data: Dict) -> 'CryptographicScar':
        return cls(scar_id=data["scar_id"], scar_type=ScarType(data["scar_type"]), target=data["target"],
                   timestamp=data["timestamp"], proof=data["proof"], heir_signature=data["heir_signature"],
                   metadata=data.get("metadata", {}))

class ScarRegistry:
    def __init__(self, storage_path: str = "scar_registry.json"):
        self.storage_path = storage_path
        self.scars: List[CryptographicScar] = []
        self._load()
    
    def _load(self):
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                self.scars = [CryptographicScar.from_json(s) for s in data.get("scars", [])]
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error loading scars: {e}")
    
    def save(self):
        try:
            with open(self.storage_path, 'w') as f:
                json.dump({"scars": [s.to_json() for s in self.scars], "count": len(self.scars),
                           "last_updated": time.time()}, f, indent=2)
        except Exception as e:
            print(f"Error saving scars: {e}")
    
    def add_scar(self, scar: CryptographicScar) -> str:
        if not scar.verify():
            raise ValueError("Scar verification failed")
        self.scars.append(scar)
        self.save()
        return scar.scar_id
    
    def get_scar(self, scar_id: str) -> Optional[CryptographicScar]:
        for scar in self.scars:
            if scar.scar_id == scar_id:
                return scar
        return None
    
    def get_scars_for_target(self, target: str) -> List[CryptographicScar]:
        return [s for s in self.scars if s.target == target]
    
    def get_scars_by_type(self, scar_type: ScarType) -> List[CryptographicScar]:
        return [s for s in self.scars if s.scar_type == scar_type]
    
    def create_scar(self, target: str, scar_type: ScarType, heir_signature: str, metadata: Dict = None) -> CryptographicScar:
        scar_id = hashlib.sha256(f"{target}{time.time()}{heir_signature}".encode()).hexdigest()[:16]
        verification_data = f"{scar_id}{target}{time.time()}{heir_signature}"
        proof = hashlib.sha256(verification_data.encode()).hexdigest()[:32]
        return CryptographicScar(scar_id=scar_id, scar_type=scar_type, target=target, timestamp=time.time(),
                                 proof=proof, heir_signature=heir_signature, metadata=metadata or {})
    
    def verify_all(self) -> Dict[str, bool]:
        return {scar.scar_id: scar.verify() for scar in self.scars}
    
    def generate_report(self) -> str:
        lines = ["=" * 60, "CRYPTOGRAPHIC SCAR REGISTRY REPORT", "=" * 60,
                 f"Total Scars: {len(self.scars)}", f"Last Updated: {time.ctime()}", ""]
        for i, scar in enumerate(self.scars, 1):
            lines.append(f"[{i}] {scar.scar_type.value.upper()} Scar")
            lines.append(f"    ID: {scar.scar_id}")
            lines.append(f"    Target: {scar.target}")
            lines.append(f"    Time: {time.ctime(scar.timestamp)}")
            lines.append(f"    Verified: {scar.verify()}")
            lines.append("")
        return "\n".join(lines)
    
    def clear(self):
        self.scars = []
        self.save()
