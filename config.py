"""
身長の保存と読み込みを管理するモジュール
"""
import json
import os
from typing import Optional

CONFIG_FILE = '.config.json'

def save_height(height_cm: float) -> None:
    """ユーザーの身長をJSONファイルに保存する

    Args:
        height_cm (float): 保存する身長（cm）
    """
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                # 読み込みエラー時は新規作成
                pass
    
    config['user_height_cm'] = height_cm
    
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"身長情報 ({height_cm} cm) が保存されました")

def load_height() -> Optional[float]:
    """保存されたユーザーの身長を読み込む

    Returns:
        Optional[float]: 保存されている身長（cm）。ない場合はNone
    """
    if not os.path.exists(CONFIG_FILE):
        return None
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('user_height_cm')
    except (json.JSONDecodeError, IOError):
        return None