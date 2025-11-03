import requests
from typing import Any, Dict, List, Optional


class OdooRPCError(Exception):
    pass


class OdooClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.uid: Optional[int] = None

    def list_databases(self) -> Any:
        url = f"{self.base_url}/web/database/list"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {},
        }
        resp = self.session.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if 'error' in data:
            raise OdooRPCError(str(data['error']))
        return data.get('result')

    def authenticate(self, db: str, login: str, password: str) -> int:
        url = f"{self.base_url}/web/session/authenticate"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": db,
                "login": login,
                "password": password,
            },
        }
        resp = self.session.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if 'error' in data:
            raise OdooRPCError(str(data['error']))
        result = data.get('result') or {}
        uid = result.get('uid')
        if not uid:
            raise OdooRPCError("Authentication failed: no uid returned")
        self.uid = uid
        return uid

    def call_kw(self, model: str, method: str, args: List[Any], kwargs: Dict[str, Any]) -> Any:
        url = f"{self.base_url}/web/dataset/call_kw/{model}/{method}"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": model,
                "method": method,
                "args": args,
                "kwargs": kwargs,
            },
        }
        resp = self.session.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if 'error' in data:
            raise OdooRPCError(str(data['error']))
        return data.get('result')

    def search_read(self, model: str, domain: List[Any], fields: List[str], limit: int = 0) -> List[Dict[str, Any]]:
        kwargs: Dict[str, Any] = {"domain": domain, "fields": fields}
        if limit:
            kwargs["limit"] = limit
        return self.call_kw(model, "search_read", [], kwargs)

    def create(self, model: str, vals: Dict[str, Any]) -> int:
        return self.call_kw(model, "create", [vals], {})

    def write(self, model: str, ids: List[int], vals: Dict[str, Any]) -> bool:
        return self.call_kw(model, "write", [ids, vals], {})
