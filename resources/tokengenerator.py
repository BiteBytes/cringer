#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

driver = webdriver.Chrome()
driver.get("https://steamcommunity.com/login/home/?goto=")
elem = driver.find_element_by_name("username")
elem.clear()
elem.send_keys("estarsdale")
elem.send_keys(Keys.RETURN)

elem = driver.find_element_by_name("password")
elem.clear()
elem.send_keys("Seabrezze_13")
elem.send_keys(Keys.RETURN)

print 'Open the SDA.Bot'
raw_input('Press Enter')

driver.get("https://steamcommunity.com/dev/managegameservers")

how_many = int(raw_input('How many? '))

for i in xrange(how_many):
    driver.get("https://steamcommunity.com/dev/managegameservers")
    time.sleep(3)
    elem = driver.find_element_by_name("appid")
    elem.clear()
    elem.send_keys("730")
    elem.send_keys(Keys.RETURN)
    # elem = driver.find_element_by_name("memo")
    # elem.clear()
    # elem.send_keys("Server " + str(i))

raw_input('Press Enter')
driver.close()
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

driver = webdriver.Chrome()
driver.get("https://steamcommunity.com/login/home/?goto=")
elem = driver.find_element_by_name("username")
elem.clear()
elem.send_keys("estarsdale")
elem.send_keys(Keys.RETURN)

elem = driver.find_element_by_name("password")
elem.clear()
elem.send_keys("Seabrezze_13")
elem.send_keys(Keys.RETURN)

raw_input('Press Enter')

driver.get("https://steamcommunity.com/dev/managegameservers")

how_many = int(raw_input('How many? '))

for i in xrange(how_many):
    driver.get("https://steamcommunity.com/dev/managegameservers")
    time.sleep(3)
    elem = driver.find_element_by_name("appid")
    elem.clear()
    elem.send_keys("730")
    elem.send_keys(Keys.RETURN)
# elem = driver.find_element_by_name("memo")
# elem.clear()
# elem.send_keys("Server " + str(i))

raw_input('Press Enter')
driver.close()