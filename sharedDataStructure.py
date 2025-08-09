# messaging.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Set, Any, Optional, List
from uuid import uuid4
from datetime import datetime

@dataclass
class Person:
    id: str
    name: str
    friends: Set[str] = field(default_factory=set)
    public_key_pem: Optional[bytes] = None
    private_key_pem: Optional[bytes] = None
    inbox: List["Message"] = field(default_factory=list)
    outbox: List["Message"] = field(default_factory=list)

@dataclass
class Message:
    id: str
    sender_id: str
    receiver_id: str
    body: bytes                 # payload after any codec/crypto
    metadata: Dict[str, Any]    # flexible; method/pipeline/etc.
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())

class Graph:
    def __init__(self):
        self.people: Dict[str, Person] = {}
        self.adj: Dict[str, Set[str]] = {}

    def add_person(self, name: str) -> Person:
        pid = str(uuid4())
        p = Person(id=pid, name=name)
        self.people[pid] = p
        self.adj[pid] = set()
        return p

    def connect(self, a: str, b: str):
        self.adj[a].add(b)
        self.adj[b].add(a)

    def get(self, pid: str) -> Person:
        return self.people[pid]
