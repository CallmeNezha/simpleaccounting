"""
    Copyright 2024- ZiJian Jiang @ https://github.com/CallmeNezha

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import configparser
import os


class INIConfig:
    _instance = None
    _config = None
    _file_path = None

    def __new__(cls, file_path):
        # 确保只有一个实例
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._file_path = file_path
            cls._instance._config = configparser.ConfigParser()

            # 如果文件不存在，创建一个新的空 INI 文件
            if not os.path.exists(file_path):
                with open(file_path, 'w') as configfile:
                    cls._instance._config.write(configfile)
            else:
                cls._instance._config.read(file_path)
        return cls._instance

    def get(self, section, option, fallback=None):
        """获取某个节中的值"""
        return self._config.get(section, option, fallback=fallback)

    def options(self, section):
        """获取节中所有选项"""
        if not self._config.has_section(section):
            return []
        return self._config.options(section)

    def set(self, section, option, value):
        """设置某个节中的值"""
        if not self._config.has_section(section):
            self._config.add_section(section)
        self._config.set(section, option, value)
        self._save()

    def remove_option(self, section, option):
        """删除某个节中的选项"""
        if self._config.has_option(section, option):
            self._config.remove_option(section, option)
            self._save()

    def remove_section(self, section):
        """删除某个节"""
        if self._config.has_section(section):
            self._config.remove_section(section)
            self._save()

    def _save(self):
        """保存到文件"""
        with open(self._file_path, 'w') as configfile:
            self._config.write(configfile)


USER_DIR = os.path.expanduser("~")
SIMPLEACCOUNTING_DIR = os.path.join(USER_DIR, ".simpleaccounting")


if not os.path.exists(SIMPLEACCOUNTING_DIR):
    os.makedirs(SIMPLEACCOUNTING_DIR)


ini = INIConfig(os.path.join(SIMPLEACCOUNTING_DIR, 'settings.ini'))