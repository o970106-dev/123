#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
from pms_base.pms_coordination import engine, STAPS_MULTIPLIER

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("=" * 70)
    print("       物業管理系統 (PMS) - 神之視角 (God View) 儀表板")
    print("       AI 物管小J 驅動 - 仁義住宅區 專屬版本")
    print("=" * 70)
    print(f"系統時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"STAPS 效率倍率: {STAPS_MULTIPLIER}x | CNS 廣播狀態: 正常")
    print("-" * 70)

def show_nodes():
    nodes = [
        ('PM', '主物業管理', '運行中'),
        ('PF', '住戶入口', '運行中'),
        ('SC', '智能控制', '運行中'),
        ('CM', '社區互動', '運行中'),
        ('AIJ', 'AI 物管小J', '運行中'),
        ('ER', '能源報告', '運行中'),
        ('AX1', '擴展節點 1', '待命'),
        ('AX2', '擴展節點 2', '待命'),
    ]

    print(f"{'節點':<8} {'描述':<20} {'狀態':<12} {'延遲 (ms)':<15}")
    print("-" * 70)

    for code, desc, status in nodes:
        # Simulate O(1) latency check
        start = time.perf_counter()
        engine.get_absolute_coordinate(code)
        latency = (time.perf_counter() - start) * 1000

        status_str = f"\033[92m{status}\033[0m" if status == '運行中' else status
        print(f"{code:<10} {desc:<20} {status_str:<17} {latency:.4f}ms")

def show_recent_events():
    print("\n[近期 CNS 廣播事件 - 仁義住宅區]")
    print("-" * 70)
    # Simulate some events
    events = [
        ("AIJ", "AI 知識庫檢索: 「電梯維護標準」"),
        ("CM", "聊天室新訊息: 「住戶 3F-A：大家午安！」"),
        ("SC", "Google Home 同步: 15 個智能設備已聯結"),
        ("PF", "流量遙測: 首頁加載延遲 0.02ms"),
    ]
    for source, msg in events:
        print(f"[{time.strftime('%H:%M:%S')}] [{source}] {msg}")

def main():
    try:
        while True:
            clear_screen()
            print_header()
            show_nodes()
            show_recent_events()
            print("\n" + "=" * 70)
            print("按 Ctrl+C 退出管理儀表板...")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n正在退出儀表板...")

if __name__ == "__main__":
    # Ensure correct PYTHONPATH for local testing
    sys.path.append(os.path.join(os.path.dirname(__file__), 'odoo19-shadow/addons'))

    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        print_header()
        show_nodes()
        show_recent_events()
    else:
        main()
