"""
文件工具 - 负责文件操作
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional


class FileUtils:
    """
    文件工具类

    职责：
    1. 文件读写
    2. 目录操作
    3. 文件搜索
    4. 备份管理
    """

    @staticmethod
    def read_file(file_path: str) -> Optional[str]:
        """
        读取文件内容

        Args:
            file_path: 文件路径

        Returns:
            Optional[str]: 文件内容
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"读取文件失败 {file_path}: {e}")
            return None

    @staticmethod
    def write_file(file_path: str, content: str) -> bool:
        """
        写入文件内容

        Args:
            file_path: 文件路径
            content: 文件内容

        Returns:
            bool: 是否成功
        """
        try:
            # 确保目录存在
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"写入文件失败 {file_path}: {e}")
            return False

    @staticmethod
    def list_files(directory: str, extensions: Optional[List[str]] = None, recursive: bool = True) -> List[str]:
        """
        列出目录中的文件

        Args:
            directory: 目录路径
            extensions: 文件扩展名过滤
            recursive: 是否递归搜索

        Returns:
            List[str]: 文件路径列表
        """
        files = []
        directory = Path(directory)

        if not directory.exists():
            return files

        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"

        for file_path in directory.glob(pattern):
            if file_path.is_file():
                if extensions is None or file_path.suffix in extensions:
                    files.append(str(file_path))

        return files

    @staticmethod
    def create_backup(file_path: str, backup_dir: str = ".backup") -> Optional[str]:
        """
        创建文件备份

        Args:
            file_path: 文件路径
            backup_dir: 备份目录

        Returns:
            Optional[str]: 备份文件路径
        """
        try:
            source = Path(file_path)
            if not source.exists():
                return None

            # 创建备份目录
            backup_path = Path(backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)

            # 生成备份文件名
            import time
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_file = backup_path / f"{source.stem}_{timestamp}{source.suffix}"

            # 复制文件
            shutil.copy2(source, backup_file)

            return str(backup_file)

        except Exception as e:
            print(f"创建备份失败 {file_path}: {e}")
            return None

    @staticmethod
    def restore_backup(backup_file: str, target_file: str) -> bool:
        """
        恢复备份

        Args:
            backup_file: 备份文件路径
            target_file: 目标文件路径

        Returns:
            bool: 是否成功
        """
        try:
            backup = Path(backup_file)
            target = Path(target_file)

            if not backup.exists():
                print(f"备份文件不存在: {backup_file}")
                return False

            # 确保目标目录存在
            target.parent.mkdir(parents=True, exist_ok=True)

            # 复制备份到目标位置
            shutil.copy2(backup, target)

            return True

        except Exception as e:
            print(f"恢复备份失败: {e}")
            return False

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """
        获取文件大小（字节）

        Args:
            file_path: 文件路径

        Returns:
            int: 文件大小
        """
        try:
            return os.path.getsize(file_path)
        except Exception:
            return 0

    @staticmethod
    def get_file_lines(file_path: str) -> int:
        """
        获取文件行数

        Args:
            file_path: 文件路径

        Returns:
            int: 文件行数
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return sum(1 for _ in f)
        except Exception:
            return 0

    @staticmethod
    def ensure_directory(directory: str) -> bool:
        """
        确保目录存在

        Args:
            directory: 目录路径

        Returns:
            bool: 是否成功
        """
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"创建目录失败 {directory}: {e}")
            return False

    @staticmethod
    def clean_directory(directory: str) -> bool:
        """
        清空目录

        Args:
            directory: 目录路径

        Returns:
            bool: 是否成功
        """
        try:
            directory = Path(directory)
            if directory.exists():
                shutil.rmtree(directory)
                directory.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"清空目录失败 {directory}: {e}")
            return False