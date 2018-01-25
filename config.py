import os.path

current_path = os.path.dirname(__file__)
PROXY_EXECUTABLE = os.path.join(current_path, "browsermob-proxy-2.1.4/bin/browsermob-proxy.bat")
FIREFOX_EXECUTABLE = os.path.join(current_path, "geckodriver.exe")
CHROME_EXECUTABLE = os.path.join(current_path, "chromedriver.exe")


LOG_DIR = os.path.join(current_path, 'logs')
SELENIUM_LOGS = os.path.join(current_path, 'logs', 'firefox.log')
PROXYSERVER_LOG = os.path.join(current_path, 'logs', 'server.log')

HAR_DIR = os.path.join(current_path, 'har_files')

