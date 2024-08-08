from plugin_base import PluginBase
import logging
import time
import json
import psutil
import os
import threading

class MonitoringLoggingPlugin(PluginBase):
    def initialize(self, context):
        self.log_file = 'whitematter.log'
        logging.basicConfig(filename=self.log_file, level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('WhiteMatter')
        
        self.start_time = time.time()
        self.query_count = 0
        self.error_count = 0
        self.lock = threading.Lock()

        # Start background monitoring
        self.stop_monitoring = False
        self.monitor_thread = threading.Thread(target=self._background_monitor)
        self.monitor_thread.start()

    def get_lua_interface(self):
        return {
            'monitor_log': self.lua_callable(self.log),
            'monitor_get_stats': self.lua_callable(self.get_stats),
            'monitor_get_log_tail': self.lua_callable(self.get_log_tail)
        }

    def log(self, level, message):
        if level not in ['debug', 'info', 'warning', 'error', 'critical']:
            return json.dumps({"status": "error", "message": "Invalid log level"})
        
        getattr(self.logger, level)(message)
        with self.lock:
            if level == 'error':
                self.error_count += 1
        return json.dumps({"status": "success", "message": "Log entry created"})

    def get_stats(self):
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        with self.lock:
            stats = {
                "uptime": time.time() - self.start_time,
                "query_count": self.query_count,
                "error_count": self.error_count,
                "cpu_usage": f"{cpu_percent}%",
                "memory_usage": f"{memory.percent}%",
                "disk_usage": f"{disk.percent}%",
                "active_threads": threading.active_count()
            }
        
        return json.dumps(stats)

    def get_log_tail(self, lines=50):
        try:
            with open(self.log_file, 'r') as f:
                return json.dumps({"status": "success", "logs": f.readlines()[-lines:]})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def _background_monitor(self):
        while not self.stop_monitoring:
            cpu_percent = psutil.cpu_percent(interval=5)
            memory = psutil.virtual_memory()
            
            if cpu_percent > 80:
                self.logger.warning(f"High CPU usage: {cpu_percent}%")
            if memory.percent > 80:
                self.logger.warning(f"High memory usage: {memory.percent}%")
            
            time.sleep(60)  # Check every minute

    def increment_query_count(self):
        with self.lock:
            self.query_count += 1

    def shutdown(self):
        self.stop_monitoring = True
        self.monitor_thread.join()

    @property
    def name(self):
        return "monitor"