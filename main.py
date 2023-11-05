import time 
import re
from selenium import webdriver 
from selenium.webdriver import Chrome 
from selenium.webdriver.common.by import By 
import webbrowser
import PIL.Image
from PIL import ImageTk
from tkinter import *
import urllib
import io
from pygame import mixer

chrome_options = webdriver.ChromeOptions() 
chrome_options.page_load_strategy = "none"
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--allow-running-insecure-content')
driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(5)

url = "http://www.fromjapan.co.jp/japan/en/mercari/search/yohji/-/?sort_order=new"

root = Toplevel()
root.title("app")
root.geometry('250x250')
root.attributes('-topmost', True)

image_button = Button(root)
image_label = Label(root)
price_label = Label(root, text="temp")
price_label.place(x=0,y=0)
image_button.place(x=0,y=0)

mixer.init()
notif_sound = mixer.Sound('notification.mp3')

prev_prices = ['','','','','']

def draw(img_url, price, link):
    page=urllib.request.Request(img_url,headers={'User-Agent': 'Mozilla/5.0'}) 
    raw_data=urllib.request.urlopen(page).read()
    image = ImageTk.PhotoImage(PIL.Image.open(io.BytesIO(raw_data)))
    image_button.config(text="temp", image=image, command=lambda: webbrowser.open(link))
    image_button.image = image
    price_label.config(text=price)
    notif_sound.play()
    

def refresh():
    driver.get(url)
    shop_items_xpath = "//div[@class='shop-item flex lg:block lg:w-1/4 mb-6 lg:px-3 justify-center w-full']"
    shop_items = driver.find_elements(By.XPATH, shop_items_xpath)

    item = shop_items[0]
    # print(item.get_attribute('outerHTML'))
    img = item.find_element(By.TAG_NAME, "img").get_attribute('src')
    price_xpath = "//span[@class='w-full text-black truncate text-xs text-grey mb-2']"
    price = item.find_element(By.XPATH, price_xpath).get_attribute('innerHTML')
    if price not in prev_prices:
        prev_prices.append(price)
        prev_prices.pop(0)
        item_link_xpath = "//a[@class='h-full flex']"
        item_link = item.find_element(By.XPATH, item_link_xpath).get_attribute('href')
        draw(img_url=img, price=price, link=item_link)

    root.after(5000, refresh)

refresh()
root.mainloop()
print("done")