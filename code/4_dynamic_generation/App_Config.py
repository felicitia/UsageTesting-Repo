
class Etsy:
    def __init__(self):
        self.appname = 'etsy'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 10000,
            "appPackage": "com.etsy.android",
            "appActivity": "com.etsy.android.ui.homescreen.HomescreenTabsActivity"
        }

class Abc:
    def __init__(self):
        self.appname = 'abc'
        self.desiredCapabilities = {
            "platformName": "Android",
            "deviceName": "emulator-5554",  # adb devices
            "newCommandTimeout": 10000,
            "appPackage": "com.abc.abcnews",
            "appActivity": "com.abc.abcnews.ui.StartActivity"
        }

