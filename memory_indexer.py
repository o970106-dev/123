#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo 17 之前記憶索引器
用於分析、索引和壓縮 Odoo 17 之前的專案記憶和歷史資訊
"""

import os
import json
import zipfile
import hashlib
import datetime
from pathlib import Path
from typing import Dict, List, Any
import re

class MemoryIndexer:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.index_data = {
            "metadata": {
                "created_at": datetime.datetime.now().isoformat(),
                "version": "1.0",
                "description": "Odoo 17 之前的記憶索引",
                "total_files": 0,
                "total_size": 0
            },
            "odoo17_files": [],
            "related_files": [],
            "scripts": [],
            "configs": [],
            "documentation": []
        }
    
    def scan_files(self) -> None:
        """掃描並分類檔案"""
        print("開始掃描檔案...")
        
        for file_path in self.base_path.rglob("*"):
            if file_path.is_file() and not self._should_ignore(file_path):
                file_info = self._analyze_file(file_path)
                if file_info:
                    self._categorize_file(file_info)
                    self.index_data["metadata"]["total_files"] += 1
                    self.index_data["metadata"]["total_size"] += file_info["size"]
    
    def _should_ignore(self, file_path: Path) -> bool:
        """判斷是否應該忽略的檔案"""
        ignore_patterns = [
            r"\.git",
            r"\.vscode",
            r"__pycache__",
            r"\.pyc$",
            r"\.tmp$",
            r"node_modules",
            r"\.venv"
        ]
        
        path_str = str(file_path)
        return any(re.search(pattern, path_str) for pattern in ignore_patterns)
    
    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """分析單個檔案"""
        try:
            stat = file_path.stat()
            
            # 讀取檔案內容（限制大小）
            content = ""
            if stat.st_size < 1024 * 1024:  # 1MB 限制
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except:
                    content = "[二進制檔案或讀取失敗]"
            
            # 計算檔案雜湊
            file_hash = self._calculate_hash(file_path)
            
            return {
                "path": str(file_path.relative_to(self.base_path)),
                "name": file_path.name,
                "size": stat.st_size,
                "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": file_path.suffix,
                "hash": file_hash,
                "content_preview": content[:500] if content else "",
                "full_content": content if len(content) < 10000 else content[:10000] + "...[截斷]",
                "odoo17_related": self._is_odoo17_related(content, file_path.name),
                "keywords": self._extract_keywords(content, file_path.name)
            }
        except Exception as e:
            print(f"分析檔案失敗 {file_path}: {e}")
            return None
    
    def _calculate_hash(self, file_path: Path) -> str:
        """計算檔案 MD5 雜湊"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return "unknown"
    
    def _is_odoo17_related(self, content: str, filename: str) -> bool:
        """判斷是否與 Odoo 17 相關"""
        odoo17_patterns = [
            r"odoo.*17",
            r"17.*odoo",
            r"pos_beverage_modifier",
            r"/opt/odoo17",
            r"odoo17",
            r"version.*17"
        ]
        
        text = (content + " " + filename).lower()
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in odoo17_patterns)
    
    def _extract_keywords(self, content: str, filename: str) -> List[str]:
        """提取關鍵字"""
        keywords = set()
        
        # 檔案名關鍵字
        keywords.add(filename.lower())
        
        # 內容關鍵字
        keyword_patterns = [
            r"odoo",
            r"pos",
            r"beverage",
            r"modifier",
            r"docker",
            r"compose",
            r"python",
            r"ssh",
            r"server",
            r"ubuntu",
            r"deploy",
            r"addon",
            r"module"
        ]
        
        text = content.lower()
        for pattern in keyword_patterns:
            if re.search(pattern, text):
                keywords.add(pattern)
        
        return list(keywords)
    
    def _categorize_file(self, file_info: Dict[str, Any]) -> None:
        """將檔案分類"""
        path = file_info["path"]
        extension = file_info["extension"].lower()
        
        if file_info["odoo17_related"]:
            self.index_data["odoo17_files"].append(file_info)
        elif extension in [".py"]:
            self.index_data["scripts"].append(file_info)
        elif extension in [".json", ".yml", ".yaml", ".conf", ".cfg"]:
            self.index_data["configs"].append(file_info)
        elif extension in [".md", ".txt", ".rst"]:
            self.index_data["documentation"].append(file_info)
        else:
            self.index_data["related_files"].append(file_info)
    
    def generate_index(self, output_path: str = "odoo17_memory_index.json") -> str:
        """生成索引檔案"""
        print("生成索引檔案...")
        
        # 排序檔案
        for category in ["odoo17_files", "related_files", "scripts", "configs", "documentation"]:
            self.index_data[category].sort(key=lambda x: x["path"])
        
        # 寫入索引檔案
        index_path = self.base_path / output_path
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(self.index_data, f, ensure_ascii=False, indent=2)
        
        print(f"索引檔案已生成：{index_path}")
        return str(index_path)
    
    def create_archive(self, index_path: str, archive_path: str = "odoo17_memory_archive.zip") -> str:
        """創建壓縮檔案"""
        print("創建壓縮檔案...")
        
        archive_full_path = self.base_path / archive_path
        
        with zipfile.ZipFile(archive_full_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 添加索引檔案
            zipf.write(index_path, "index.json")
            
            # 添加 Odoo 17 相關檔案
            for file_info in self.index_data["odoo17_files"]:
                file_path = self.base_path / file_info["path"]
                if file_path.exists():
                    zipf.write(file_path, f"odoo17_files/{file_info['path']}")
            
            # 添加重要的配置和腳本檔案
            important_files = []
            important_files.extend(self.index_data["configs"][:10])  # 最多10個配置檔案
            important_files.extend([f for f in self.index_data["scripts"] if "deploy" in f["name"].lower() or "manage" in f["name"].lower()])
            
            for file_info in important_files:
                file_path = self.base_path / file_info["path"]
                if file_path.exists():
                    zipf.write(file_path, f"important_files/{file_info['path']}")
        
        print(f"壓縮檔案已創建：{archive_full_path}")
        return str(archive_full_path)
    
    def print_summary(self) -> None:
        """打印摘要資訊"""
        print("\n=== Odoo 17 記憶索引摘要 ===")
        print(f"總檔案數：{self.index_data['metadata']['total_files']}")
        print(f"總大小：{self.index_data['metadata']['total_size']:,} bytes")
        print(f"Odoo 17 相關檔案：{len(self.index_data['odoo17_files'])}")
        print(f"腳本檔案：{len(self.index_data['scripts'])}")
        print(f"配置檔案：{len(self.index_data['configs'])}")
        print(f"文檔檔案：{len(self.index_data['documentation'])}")
        print(f"其他相關檔案：{len(self.index_data['related_files'])}")
        
        if self.index_data['odoo17_files']:
            print("\nOdoo 17 相關檔案：")
            for file_info in self.index_data['odoo17_files']:
                print(f"  - {file_info['path']} ({file_info['size']} bytes)")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Odoo 17 記憶索引器")
    parser.add_argument("--path", default=".", help="要掃描的路徑（預設：當前目錄）")
    parser.add_argument("--output", default="odoo17_memory_index.json", help="索引檔案名稱")
    parser.add_argument("--archive", default="odoo17_memory_archive.zip", help="壓縮檔案名稱")
    parser.add_argument("--no-archive", action="store_true", help="不創建壓縮檔案")
    
    args = parser.parse_args()
    
    # 創建索引器
    indexer = MemoryIndexer(args.path)
    
    # 掃描檔案
    indexer.scan_files()
    
    # 生成索引
    index_path = indexer.generate_index(args.output)
    
    # 創建壓縮檔案
    if not args.no_archive:
        archive_path = indexer.create_archive(index_path, args.archive)
        print(f"\n壓縮檔案已創建：{archive_path}")
    
    # 打印摘要
    indexer.print_summary()

if __name__ == "__main__":
    main()