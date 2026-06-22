import logging
import os
import time

from cop_thief.shared.config_loader import ConfigLoader


class ApiGatekeeper:
    def __init__(self, config: ConfigLoader):
        self.max_rpm = 30
        self.call_timestamps = []
        os.makedirs("results", exist_ok=True)
        self.logger = logging.getLogger("ApiGatekeeper")
        self.logger.propagate = False
        if not self.logger.handlers:
            fh = logging.FileHandler("results/api_calls.log")
            formatter = logging.Formatter('%(asctime)s - %(message)s')
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
            self.logger.setLevel(logging.INFO)

    def _check_rate_limit(self) -> None:
        now = time.time()
        self.call_timestamps = [t for t in self.call_timestamps if now - t < 60]
        if len(self.call_timestamps) >= self.max_rpm:
            sleep_time = 60 - (now - self.call_timestamps[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
            self._check_rate_limit()

    def _log_call(self, call_name: str, success: bool) -> None:
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"{call_name} - {status}")

    def execute(self, api_call, *args, **kwargs):
        max_retries = 3
        for attempt in range(max_retries + 1):
            self._check_rate_limit()
            self.call_timestamps.append(time.time())
            try:
                result = api_call(*args, **kwargs)
                name = api_call.__name__ if hasattr(api_call, "__name__") else "api_call"
                self._log_call(name, True)
                return result
            except Exception:
                name = api_call.__name__ if hasattr(api_call, "__name__") else "api_call"
                self._log_call(name, False)
                if attempt == max_retries:
                    raise
                time.sleep(1)
