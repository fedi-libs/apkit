from __future__ import annotations
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Link:
    rel: str
    type: Optional[str] = None
    href: Optional[str] = None
    titles: Optional[dict] = None
    properties: Optional[dict] = None

@dataclass
class WebFinger:
    subject: str
    aliases: Optional[List[str]] = None
    properties: Optional[dict] = None
    links: Optional[List[Link]] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'WebFinger':
        links = [Link(**link) for link in data.get('links', [])] if data.get('links') else None
        return cls(
            subject=data['subject'],
            aliases=data.get('aliases'),
            properties=data.get('properties'),
            links=links
        )
    
    def to_dict(self) -> dict:
        result: dict[str, str] = {'subject': self.subject}
        if self.aliases:
            result['aliases'] = self.aliases # type: ignore
        if self.properties:
            result['properties'] = self.properties # type: ignore
        if self.links:
            result['links'] = [vars(link) for link in self.links] # type: ignore
        return result
    
class Resource:
    username: str
    host: str

    def to_string(self) -> str:
        return f"acct:{self.username}@{self.host}"

    def parse(self, resource: str) -> Resource:
        if resource.startswith("acct:"):
            username_split = resource.split(":")[1].split("@")
            self.username = username_split[0]
            self.host = username_split[1]
            return self
        else:
            raise ValueError("Invalid resource format. Expected 'acct:username@host'.")