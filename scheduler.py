import time
import threading
from datetime import datetime, timedelta
from .config_manager import ConfigManager

class Scheduler:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.schedules = config_manager.get_setting('schedules', [])
        self.running = False
        self.thread = None

    def add_schedule(self, url, interval, start_time=None):
        """Add a new scraping schedule"""
        schedule = {
            'url': url,
            'interval': interval,
            'next_run': start_time or datetime.now(),
            'enabled': True
        }
        self.schedules.append(schedule)
        self.config_manager.update_setting('schedules', self.schedules)

    def remove_schedule(self, url):
        """Remove a schedule by URL"""
        self.schedules = [s for s in self.schedules if s['url'] != url]
        self.config_manager.update_setting('schedules', self.schedules)

    def start(self, callback):
        """Start the scheduler"""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, args=(callback,))
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join()

    def _run_scheduler(self, callback):
        """Main scheduler loop"""
        while self.running:
            now = datetime.now()
            for schedule in self.schedules:
                if schedule['enabled'] and now >= schedule['next_run']:
                    try:
                        callback(schedule['url'])
                    except Exception as e:
                        print(f"Error executing schedule: {e}")
                    finally:
                        schedule['next_run'] = now + timedelta(seconds=schedule['interval'])
                        self.config_manager.update_setting('schedules', self.schedules)
            
            time.sleep(1)

    def get_upcoming_schedules(self):
        """Get list of upcoming schedules"""
        now = datetime.now()
        upcoming = []
        for schedule in self.schedules:
            if schedule['enabled']:
                time_until = (schedule['next_run'] - now).total_seconds()
                if time_until > 0:
                    upcoming.append({
                        'url': schedule['url'],
                        'time_until': time_until
                    })
        return sorted(upcoming, key=lambda x: x['time_until'])

    def enable_schedule(self, url, enabled=True):
        """Enable or disable a schedule"""
        for schedule in self.schedules:
            if schedule['url'] == url:
                schedule['enabled'] = enabled
                self.config_manager.update_setting('schedules', self.schedules)
                return True
        return False