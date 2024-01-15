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
from Item import Item

class FromJapanNotifier:
    # initialize tkinter window
    def tk_root(self):
        root = Tk()
        root.resizable(True, True)
        root.title("FJN")
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)
        root.iconbitmap(default='OneMap.ico')
        root.geometry('250x325')
        root.attributes('-topmost', True)
        root.bind("<Tab>", self.focus_next_widget)
        return root

    def focus_next_widget(self, event):
        event.widget.tk_focusNext().focus()
        return("break")

    # start the programs setup screen
    def setup(self):

        def goto_notifier(e=None):
            self.refresh_freq = int(freq_box.get())
            self.search_url = "http://www.fromjapan.co.jp/japan/en/mercari/search/{}/-/?sort_order=new".format(input_box.get().strip().lower().replace(' ', '+'))
            self.translate = True if var.get() == 1 else False
            for widget in self.root.winfo_children():
                widget.destroy()
            self.start_notifier()

        self.init_driver()
        input_text = Label(self.root, text="Enter your search term:")
        input_text.pack()
        input_box = Entry(self.root)
        input_box.pack()
        freq_text = Label(self.root, text="Refresh frequency (seconds)")
        freq_text.pack()
        freq_box = Entry(self.root)
        freq_box.insert(0, "3")
        freq_box.pack()
        var = IntVar()
        translate_box = Checkbutton(self.root, text="Translate descriptions?", variable=var, onvalue=1, offvalue=0)
        translate_box.select()
        translate_box.pack()
        start_button = Button(self.root, text="Start!", command=goto_notifier)
        start_button.bind('<Return>',goto_notifier)
        start_button.pack()
        self.root.mainloop()

    # initialize selenium web driver
    def init_driver(self):
        chrome_options = webdriver.ChromeOptions() 
        chrome_options.page_load_strategy = "none"
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        chrome_options.add_argument(f'user-agent={user_agent}')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--allow-running-insecure-content')
        self.driver = webdriver.Chrome(options=chrome_options)

    # start the notification screen
    def start_notifier(self):
        self.image_button = Button(self.root)
        self.image_button.place(x=0,y=0)
        self.price_label = Label(self.root, text="temp", font=("Arial", 14), wraplength=250, justify="center")
        self.price_label.grid(row=0, column=0, sticky=NW)
        self.desc_label = Label(self.root, text="temp", font=("Arial", 12), wraplength=250, justify="left")
        self.desc_label.grid(row=1, column=0, sticky=SW)
        self.reset_button = Button(self.root, text="R", command=self.refresh)
        self.reset_button.grid(row=0, column=1, sticky=NE)
        
        self.driver.get(self.search_url)
        self.refresh()
        self.root.mainloop()

    def get_resized(self, PILImage):
        w, h = PILImage.size
        width_ratio = self.root.winfo_width() / w
        height_ratio = self.root.winfo_height() / h
        scalar = min(width_ratio, height_ratio)
        return PILImage.resize((int(w*scalar), int(h*scalar)))

    # sets tkinter labels to given image and price. Image is a button that redirects to passed link 
    def update_item(self, item):
        page=urllib.request.Request(item.img,headers={'User-Agent': 'Mozilla/5.0'}) 
        raw_data=urllib.request.urlopen(page).read()
        PILImage = PIL.Image.open(io.BytesIO(raw_data))
        PILImage = self.get_resized(PILImage)
        image = ImageTk.PhotoImage(PILImage)
        self.image_button.config(text="temp", image=image, command=lambda: webbrowser.open(item.link))
        self.image_button.image = image
        self.price_label.config(text=item.price)
        self.desc_label.config(text=item.desc)
        self.notif_sound.play()
        
    # reload the page and refresh app frame
    def refresh(self):
        
        shop_items_xpath = "//div[@class='shop-item flex lg:block lg:w-1/4 mb-6 lg:px-3 justify-center w-full']" # xpath for one item
        try:
            elem = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, shop_items_xpath))) # waits for element to exist, i.e. page to be loaded
            item = self.driver.find_element(By.XPATH, shop_items_xpath) # get most recent item on the page
            desc_xpath = "//a[@class='inline-block w-full text-black truncate text-sm']"
            desc = item.find_element(By.XPATH, desc_xpath).get_attribute('innerHTML')
            if (self.translate):
                    desc = GoogleTranslator(source='auto', target='english').translate(desc)
            if desc not in self.prev_items: # make sure item was not recently displayed; necessary as FromJapan display order is not consistent
                print("Found new item: " + desc)
                img = item.find_element(By.TAG_NAME, "img").get_attribute('src')
                price_xpath = "//span[@class='w-full text-black truncate text-xs text-grey mb-2']" # xpath for price label
                price = item.find_element(By.XPATH, price_xpath).get_attribute('innerHTML')
                self.prev_items.append(desc)
                self.prev_items.pop(0)
                link_xpath = "//a[@class='h-full flex']" 
                link = item.find_element(By.XPATH, link_xpath).get_attribute('href')
                self.update_item(Item(desc, img, price, link))
            
        except:
            pass
        self.driver.refresh()
        self.root.after(1000 * self.refresh_freq, lambda: self.refresh()) # rerun refresh page every 3000 ms

    def __init__(self):
        self.prev_items = ['','','','',''] # stores the last several prices of items to prevent repetition due to FromJapan inconsistency
        self.queue = []
        self.root = self.tk_root()
        self.translate = None
        # import notification sound
        mixer.init()
        self.notif_sound = mixer.Sound('notification.mp3')
        self.setup()

        self.driver.quit()
        print("done")

FromJapanNotifier()