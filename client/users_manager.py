import json
import os
import sys
from pathlib import Path
from typing import Dict


def get_data_dir() -> Path:
    """获取存储用户数据的目录路径"""
    # 优先使用环境变量指定的路径
    if "USER_DATA_DIR" in os.environ:
        return Path(os.environ["USER_DATA_DIR"])

    # 在打包后的应用中，使用应用数据目录
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件所在目录
        base_path = Path(sys.executable).parent
    else:
        # 开发环境中使用项目根目录
        base_path = Path(__file__).parent.parent

    # 创建数据目录
    data_dir = base_path / "user_data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_users_file() -> Path:
    """获取用户数据文件路径"""
    return get_data_dir() / "users.json"


def load_users() -> Dict[str, str]:
    """加载用户数据，文件不存在时创建默认数据"""
    users_file = get_users_file()

    if not users_file.exists():
        default_data = {"admin": "admin123"}
        save_users(default_data)
        return default_data

    try:
        with open(users_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        # 文件损坏或读取错误时返回默认数据
        return {"让三颗心免于哀伤": "114514"}


def save_users(users: Dict[str, str]) -> None:
    """保存用户数据到文件"""
    users_file = get_users_file()
    try:
        with open(users_file, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"保存用户数据失败: {e}")


# 初始化加载数据
users = load_users()