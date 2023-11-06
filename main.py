from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import Chrome 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support import expected_conditions as EC
import webbrowser
import PIL.Image
from PIL import ImageTk
from tkinter import *
import urllib
import io
from pygame import mixer

url = "http://www.fromjapan.co.jp/japan/en/mercari/search/yohji/-/?sort_order=new"

# initialize selenium web driver
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

# initialize tkinter frame layout
root = Tk()
root.title("FromJapan Scraper")
root.geometry('250x250')
root.attributes('-topmost', True)
image_button = Button(root)
image_label = Label(root)
price_label = Label(root, text="temp", font=("Arial", 14))
price_label.place(x=0,y=0)
image_button.place(x=0,y=0)

# import notification sound
mixer.init()
notif_sound = mixer.Sound('notification.mp3')

prev_prices = ['','','','',''] # stores the last several prices of items to prevent repetition

# sets tkinter labels to given image and price. Image is a button that redirects to passed link 
def update_item(img_url, price, link):
    page=urllib.request.Request(img_url,headers={'User-Agent': 'Mozilla/5.0'}) 
    raw_data=urllib.request.urlopen(page).read()
    PILImage = PIL.Image.open(io.BytesIO(raw_data))
    PILImage.thumbnail((250, 250))
    image = ImageTk.PhotoImage(PILImage)
    image_button.config(text="temp", image=image, command=lambda: webbrowser.open(link))
    image_button.image = image
    price_label.config(text=price)
    notif_sound.play()
    
# load the page and refresh app frame
def refresh():
    driver.get(url)
    shop_items_xpath = "//div[@class='shop-item flex lg:block lg:w-1/4 mb-6 lg:px-3 justify-center w-full']" # xpath for one item
    elem = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, shop_items_xpath))) # waits for element to exist, i.e. page to be loaded
    item = driver.find_element(By.XPATH, shop_items_xpath) # gets first (most recent) item on the page
    img = item.find_element(By.TAG_NAME, "img").get_attribute('src')
    price_xpath = "//span[@class='w-full text-black truncate text-xs text-grey mb-2']" # xpath for price label
    price = item.find_element(By.XPATH, price_xpath).get_attribute('innerHTML')
    if price not in prev_prices: # make sure item was not recently displayed; necessary as FromJapan display order is not consistent
        prev_prices.append(price)
        prev_prices.pop(0)
        item_link_xpath = "//a[@class='h-full flex']" 
        item_link = item.find_element(By.XPATH, item_link_xpath).get_attribute('href')
        update_item(img_url=img, price=price, link=item_link)

    root.after(3000, refresh) # rerun refresh page every 3000 ms

refresh()
root.mainloop()
print("done")