from sys import argv
import os
import re
import explorer
import time
import json
import selenium
from test_generator import TestGenerator, DestEvent
from explorer import Explorer
import pickle

if __name__ == '__main__':
    desiredCapabilities = {
        "platformName": "Android",
        "deviceName": "emulator-5554",
        "newCommandTimeout": 10000,
        "appPackage": "com.etsy.android",
        "appActivity": "com.etsy.android.ui.homescreen.HomescreenTabsActivity"
    }
    start = time.time()
    explorer = Explorer(desiredCapabilities)
    explorer.execute_test('/Users/yixue/Documents/Research/UsageTesting/UsageTesting-Repo/video_data_examples/dynamic_output/etsy/generated_tests/test_executable2.pickle')
    end = time.time()
    print("test running time " + str(end - start) + " seconds")