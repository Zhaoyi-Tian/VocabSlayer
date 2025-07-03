import sys
import os
from pathlib import Path


def get_resource_path(relative_path):
    """获取绝对路径，解决打包后路径问题"""
    try:
        # 打包后资源目录
        base_path = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else Path(__file__).parent
    except Exception:
        base_path = Path(__file__).parent

    return base_path / relative_path