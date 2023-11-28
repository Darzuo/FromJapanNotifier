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
from deep_translator import GoogleTranslator

# initialize tkinter window
def tk_root():
    root = Tk()
    root.resizable(False, False)
    root.title("FJN")
    root.iconbitmap(default='OneMap.ico')
    root.geometry('250x325')
    root.attributes('-topmost', True)
    root.bind("<Tab>", focus_next_widget)
    return root

def focus_next_widget(event):
    event.widget.tk_focusNext().focus()
    return("break")

# start the programs setup screen
def setup():

    def goto_notifier(e=None):
        global refresh_freq
        global search_url
        global translate
        refresh_freq = int(freq_box.get())
        search_url = "http://www.fromjapan.co.jp/japan/en/mercari/search/{}/-/?sort_order=new".format(input_box.get().strip().lower().replace(' ', '+'))
        translate = True if var.get() == 1 else False
        for widget in root.winfo_children():
            widget.destroy()
        start_notifier()

    init_driver()
    input_text = Label(root, text="Enter your search term:")
    input_text.pack()
    input_box = Entry(root)
    input_box.pack()
    freq_text = Label(root, text="Refresh frequency (seconds)")
    freq_text.pack()
    freq_box = Entry(root)
    freq_box.insert(0, "3")
    freq_box.pack()
    var = IntVar()
    translate_box = Checkbutton(root, text="Translate descriptions?", variable=var, onvalue=1, offvalue=0)
    translate_box.select()
    translate_box.pack()
    start_button = Button(root, text="Start!", command=goto_notifier)
    start_button.bind('<Return>',goto_notifier)
    start_button.pack()
    root.mainloop()

# initialize selenium web driver
def init_driver():
    global driver
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

# start the notification screen
def start_notifier():
    image_button = Button(root)
    image_button.place(x=0,y=0)
    price_label = Label(root, text="temp", font=("Arial", 14), wraplength=250, justify="center")
    price_label.place(x=0,y=0)
    desc_label = Label(root, text="temp", font=("Arial", 12), wraplength=250, justify="left")
    desc_label.place(x=0, y=250)

    refresh(price_label, image_button, desc_label)
    root.mainloop()

# sets tkinter labels to given image and price. Image is a button that redirects to passed link 
def update_item(img_url, price, link, desc, price_label, image_button, desc_label):
    page=urllib.request.Request(img_url,headers={'User-Agent': 'Mozilla/5.0'}) 
    raw_data=urllib.request.urlopen(page).read()
    PILImage = PIL.Image.open(io.BytesIO(raw_data))
    PILImage.thumbnail((250, 250))
    image = ImageTk.PhotoImage(PILImage)
    image_button.config(text="temp", image=image, command=lambda: webbrowser.open(link))
    image_button.image = image
    price_label.config(text=price)
    desc_label.config(text=desc)
    notif_sound.play()
    
# reload the page and refresh app frame
def refresh(price_label, image_button, desc_label):
    driver.get(search_url)
    shop_items_xpath = "//div[@class='shop-item flex lg:block lg:w-1/4 mb-6 lg:px-3 justify-center w-full']" # xpath for one item
    try:
        elem = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, shop_items_xpath))) # waits for element to exist, i.e. page to be loaded
        item = driver.find_element(By.XPATH, shop_items_xpath) # gets first (most recent) item on the page
        img = item.find_element(By.TAG_NAME, "img").get_attribute('src')
        price_xpath = "//span[@class='w-full text-black truncate text-xs text-grey mb-2']" # xpath for price label
        price = item.find_element(By.XPATH, price_xpath).get_attribute('innerHTML')
        # print(item.get_attribute('outerHTML'))
        desc_xpath = "//a[@class='inline-block w-full text-black truncate text-sm']"
        desc = item.find_element(By.XPATH, desc_xpath).get_attribute('innerHTML')
        if (translate):
            desc = GoogleTranslator(source='auto', target='english').translate(desc)
        if price not in prev_prices: # make sure item was not recently displayed; necessary as FromJapan display order is not consistent
            prev_prices.append(price)
            prev_prices.pop(0)
            item_link_xpath = "//a[@class='h-full flex']" 
            item_link = item.find_element(By.XPATH, item_link_xpath).get_attribute('href')
            update_item(img, price, item_link, desc, price_label, image_button, desc_label)
    except:
        pass
    
    root.after(1000 * refresh_freq, lambda: refresh(price_label, image_button, desc_label)) # rerun refresh page every 3000 ms

prev_prices = ['','','','',''] # stores the last several prices of items to prevent repetition due to FromJapan inconsistency

root = tk_root()
translate = None
# import notification sound
mixer.init()
notif_sound = mixer.Sound('notification.mp3')
setup()
print("done")