import os
import subprocess
import json
import logging
from typing import Dict, List, Optional

class AppManager:
    """应用管理类，负责应用的列表、配置、启动、停止和日志管理"""
    def __init__(self):
        """初始化应用管理器
        - 设置应用根目录为工程下的apps目录
        - 初始化进程管理字典
        - 配置日志
        """
        self.apps_root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'apps')
        self.running_apps: Dict[str, subprocess.Popen] = {}
        self._init_logging()

    def _init_logging(self):
        """初始化日志配置"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler('app_manager.log'), logging.StreamHandler()]
        )
        self.logger = logging.getLogger('AppManager')

    def get_app_list(self) -> List[str]:
        """获取所有应用列表
        Returns:
            List[str]: 应用ID列表
        """
        if not os.path.exists(self.apps_root):
            self.logger.warning(f"应用根目录不存在: {self.apps_root}")
            return []

        app_list = []
        for item in os.listdir(self.apps_root):
            item_path = os.path.join(self.apps_root, item)
            if os.path.isdir(item_path):
                app_list.append(item)
        return app_list

    def get_app_config(self, app_id: str) -> Optional[Dict]:
        """获取指定应用的配置
        Args:
            app_id: 应用ID
        Returns:
            Optional[Dict]: 应用配置字典，如果配置文件不存在则返回None
        """
        app_dir = os.path.join(self.apps_root, app_id)
        config_path = os.path.join(app_dir, 'config.json')

        if not os.path.exists(config_path):
            self.logger.error(f"应用配置文件不存在: {config_path}")
            return None

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            self.logger.error(f"解析配置文件失败: {e}")
            return None

    def start_app(self, app_id: str) -> bool:
        """启动指定应用
        Args:
            app_id: 应用ID
        Returns:
            bool: 启动成功返回True，否则返回False
        """
        if app_id in self.running_apps and self.running_apps[app_id].poll() is None:
            self.logger.warning(f"应用{app_id}已经在运行中")
            return True

        app_dir = os.path.join(self.apps_root, app_id)
        if not os.path.exists(app_dir):
            self.logger.error(f"应用目录不存在: {app_dir}")
            return False

        # 获取应用配置，确定入口文件
        config = self.get_app_config(app_id)
        entry_file = config.get('entry_file', 'main.py') if config else 'main.py'
        entry_path = os.path.join(app_dir, entry_file)

        if not os.path.exists(entry_path):
            self.logger.error(f"应用入口文件不存在: {entry_path}")
            return False

        # 创建日志目录
        log_dir = os.path.join(app_dir, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, 'app.log')

        try:
            # 启动独立进程运行应用，并将输出重定向到日志文件
            with open(log_path, 'a', encoding='utf-8') as log_file:
                process = subprocess.Popen(
                    ['python', entry_path],
                    cwd=app_dir,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    text=True
                )
            self.running_apps[app_id] = process
            self.logger.info(f"应用{app_id}启动成功，进程ID: {process.pid}")
            return True
        except Exception as e:
            self.logger.error(f"应用{app_id}启动失败: {str(e)}")
            return False

    def get_app_log(self, app_id: str, lines: int = 100) -> str:
        """获取应用运行日志
        Args:
            app_id: 应用ID
            lines: 要获取的日志行数，默认100行
        Returns:
            str: 日志内容
        """
        app_dir = os.path.join(self.apps_root, app_id)
        log_path = os.path.join(app_dir, 'logs', 'app.log')

        if not os.path.exists(log_path):
            return f"日志文件不存在: {log_path}"

        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                return ''.join(f.readlines()[-lines:])
        except Exception as e:
            return f"读取日志失败: {str(e)}"

    def stop_app(self, app_id: str) -> bool:
        """停止指定应用
        Args:
            app_id: 应用ID
        Returns:
            bool: 停止成功返回True，否则返回False
        """
        if app_id not in self.running_apps:
            self.logger.warning(f"应用{app_id}未在运行中")
            return True

        process = self.running_apps[app_id]
        if process.poll() is not None:
            # 进程已经结束
            del self.running_apps[app_id]
            self.logger.info(f"应用{app_id}进程已结束")
            return True

        try:
            # 尝试优雅终止进程
            process.terminate()
            # 等待进程结束
            process.wait(timeout=5)
            del self.running_apps[app_id]
            self.logger.info(f"应用{app_id}已成功停止")
            return True
        except subprocess.TimeoutExpired:
            # 超时则强制终止
            process.kill()
            del self.running_apps[app_id]
            self.logger.warning(f"应用{app_id}强制终止")
            return True
        except Exception as e:
            self.logger.error(f"停止应用{app_id}失败: {str(e)}")
            return False

    def get_running_apps(self) -> Dict[str, int]:
        """获取当前运行中的应用
        Returns:
            Dict[str, int]: 应用ID到进程ID的映射
        """
        # 清理已结束的进程
        to_remove = []
        for app_id, process in self.running_apps.items():
            if process.poll() is not None:
                to_remove.append(app_id)
        for app_id in to_remove:
            del self.running_apps[app_id]

        return {app_id: process.pid for app_id, process in self.running_apps.items()}