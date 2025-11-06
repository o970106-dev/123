#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
驗證 Odoo 17 記憶索引檔案的完整性和可讀性
"""

import json
import zipfile
import os
from pathlib import Path
from typing import Dict, Any

def verify_index_file(index_path: str) -> bool:
    """驗證索引檔案的完整性"""
    print(f"驗證索引檔案：{index_path}")
    
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 檢查必要的欄位
        required_fields = ["metadata", "odoo17_files", "related_files", "scripts", "configs", "documentation"]
        for field in required_fields:
            if field not in data:
                print(f"❌ 缺少必要欄位：{field}")
                return False
        
        # 檢查 metadata
        metadata = data["metadata"]
        required_metadata = ["created_at", "version", "description", "total_files", "total_size"]
        for field in required_metadata:
            if field not in metadata:
                print(f"❌ metadata 缺少欄位：{field}")
                return False
        
        # 統計檔案數量
        total_files = (len(data["odoo17_files"]) + 
                      len(data["related_files"]) + 
                      len(data["scripts"]) + 
                      len(data["configs"]) + 
                      len(data["documentation"]))
        
        if total_files != metadata["total_files"]:
            print(f"❌ 檔案數量不符：索引顯示 {metadata['total_files']}，實際統計 {total_files}")
            return False
        
        # 檢查每個檔案記錄的完整性
        all_files = []
        all_files.extend(data["odoo17_files"])
        all_files.extend(data["related_files"])
        all_files.extend(data["scripts"])
        all_files.extend(data["configs"])
        all_files.extend(data["documentation"])
        
        required_file_fields = ["path", "name", "size", "modified", "extension", "hash", "keywords"]
        for i, file_info in enumerate(all_files):
            for field in required_file_fields:
                if field not in file_info:
                    print(f"❌ 檔案記錄 {i} 缺少欄位：{field}")
                    return False
        
        print(f"✅ 索引檔案驗證通過")
        print(f"   - 總檔案數：{metadata['total_files']}")
        print(f"   - Odoo 17 相關檔案：{len(data['odoo17_files'])}")
        print(f"   - 腳本檔案：{len(data['scripts'])}")
        print(f"   - 配置檔案：{len(data['configs'])}")
        print(f"   - 文檔檔案：{len(data['documentation'])}")
        print(f"   - 其他檔案：{len(data['related_files'])}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON 格式錯誤：{e}")
        return False
    except Exception as e:
        print(f"❌ 驗證失敗：{e}")
        return False

def verify_archive_file(archive_path: str) -> bool:
    """驗證壓縮檔案的完整性"""
    print(f"\n驗證壓縮檔案：{archive_path}")
    
    try:
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            # 檢查是否包含索引檔案
            if "index.json" not in zipf.namelist():
                print("❌ 壓縮檔案中缺少 index.json")
                return False
            
            # 測試所有檔案是否可以正常讀取
            for file_info in zipf.infolist():
                try:
                    with zipf.open(file_info) as f:
                        # 嘗試讀取前100字節
                        f.read(100)
                except Exception as e:
                    print(f"❌ 無法讀取檔案 {file_info.filename}：{e}")
                    return False
            
            # 讀取並驗證索引檔案
            with zipf.open("index.json") as f:
                try:
                    index_data = json.load(f)
                    print(f"✅ 壓縮檔案中的索引檔案可正常讀取")
                except json.JSONDecodeError as e:
                    print(f"❌ 壓縮檔案中的索引檔案 JSON 格式錯誤：{e}")
                    return False
            
            print(f"✅ 壓縮檔案驗證通過")
            print(f"   - 總檔案數：{len(zipf.namelist())}")
            print(f"   - 壓縮檔案大小：{os.path.getsize(archive_path):,} bytes")
            
            # 列出檔案結構
            print("   - 檔案結構：")
            for name in sorted(zipf.namelist()):
                info = zipf.getinfo(name)
                print(f"     {name} ({info.file_size} bytes)")
            
            return True
            
    except zipfile.BadZipFile:
        print("❌ 壓縮檔案損壞")
        return False
    except Exception as e:
        print(f"❌ 驗證失敗：{e}")
        return False

def generate_summary_report(index_path: str) -> None:
    """生成摘要報告"""
    print(f"\n=== Odoo 17 記憶索引摘要報告 ===")
    
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        metadata = data["metadata"]
        print(f"創建時間：{metadata['created_at']}")
        print(f"版本：{metadata['version']}")
        print(f"描述：{metadata['description']}")
        print(f"總檔案數：{metadata['total_files']}")
        print(f"總大小：{metadata['total_size']:,} bytes")
        
        print(f"\n=== Odoo 17 相關檔案詳情 ===")
        for file_info in data["odoo17_files"]:
            print(f"📁 {file_info['path']}")
            print(f"   大小：{file_info['size']} bytes")
            print(f"   修改時間：{file_info['modified']}")
            print(f"   關鍵字：{', '.join(file_info['keywords'])}")
            if file_info.get('content_preview'):
                preview = file_info['content_preview'][:100].replace('\n', ' ')
                print(f"   預覽：{preview}...")
            print()
        
        print(f"=== 重要腳本檔案 ===")
        important_scripts = [f for f in data["scripts"] if any(keyword in f["name"].lower() for keyword in ["deploy", "install", "manage", "upgrade"])]
        for file_info in important_scripts[:5]:  # 只顯示前5個
            print(f"🐍 {file_info['path']} ({file_info['size']} bytes)")
        
        print(f"\n=== 配置檔案 ===")
        for file_info in data["configs"]:
            print(f"⚙️ {file_info['path']} ({file_info['size']} bytes)")
        
    except Exception as e:
        print(f"❌ 生成報告失敗：{e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="驗證 Odoo 17 記憶索引檔案")
    parser.add_argument("--index", default="odoo17_memory_index.json", help="索引檔案路徑")
    parser.add_argument("--archive", default="odoo17_memory_archive.zip", help="壓縮檔案路徑")
    parser.add_argument("--report", action="store_true", help="生成詳細報告")
    
    args = parser.parse_args()
    
    success = True
    
    # 驗證索引檔案
    if os.path.exists(args.index):
        if not verify_index_file(args.index):
            success = False
    else:
        print(f"❌ 索引檔案不存在：{args.index}")
        success = False
    
    # 驗證壓縮檔案
    if os.path.exists(args.archive):
        if not verify_archive_file(args.archive):
            success = False
    else:
        print(f"❌ 壓縮檔案不存在：{args.archive}")
        success = False
    
    # 生成報告
    if args.report and os.path.exists(args.index):
        generate_summary_report(args.index)
    
    if success:
        print(f"\n🎉 所有驗證通過！Odoo 17 記憶索引檔案已成功創建並可正常使用。")
        return 0
    else:
        print(f"\n❌ 驗證失敗，請檢查錯誤訊息。")
        return 1

if __name__ == "__main__":
    exit(main())