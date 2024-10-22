import os
import shutil
import json
from datetime import datetime
from plugin_base import PluginBase

class BackupRestorePlugin(PluginBase):
    def initialize(self, context):
        self.data_dir = os.path.join('data', context['namespace'])
        self.backup_dir = os.path.join('backups', context['namespace'])
        os.makedirs(self.backup_dir, exist_ok=True)

    def get_lua_interface(self):
        return {
            'create_backup': self.lua_callable(self.create_backup),
            'list_backups': self.lua_callable(self.list_backups),
            'restore_backup': self.lua_callable(self.restore_backup)
        }

    def create_backup(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}")
        shutil.copytree(self.data_dir, backup_path)
        return {"status": "success", "backup_path": backup_path}

    def list_backups(self):
        backups = [d for d in os.listdir(self.backup_dir) if os.path.isdir(os.path.join(self.backup_dir, d))]
        return {"backups": backups}

    def restore_backup(self, backup_name):
        backup_path = os.path.join(self.backup_dir, backup_name)
        if not os.path.exists(backup_path):
            return {"status": "error", "message": "Backup not found"}
        shutil.rmtree(self.data_dir)
        shutil.copytree(backup_path, self.data_dir)
        return {"status": "success", "message": f"Restored backup: {backup_name}"}

    @property
    def name(self):
        return "backup"