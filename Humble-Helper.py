'''
Libraries that we need to import: 
1. Selenium+Webdriver_manager to simulate browser usage, needs: pip install selenium  , pip install webderiver_manager
2. OS to read and write in directories on our computer, no need to install
3. Pandas to read/write datasets (this is one way to do it), needs: pip install pandas
4. Pickle to save and load uncertain data types in bytes, no need to install
5. Datetime , pretty self explanatory, to access date and time
6. Cryptography, so that we can encrypt and decrypt the login cookie 
7. Json, so that we may convert cookies into bytes and vice-versa
8. Rich, testing to make a more beautiful console print outs
'''

import os
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from cryptography.fernet import Fernet

from datetime import datetime
import pandas as pd
import pickle
import json
from rich import print as rprint


url_purchases = 'https://www.humblebundle.com/login?goto=%2Fhome%2Fpurchases&qs=hmb_source%3Dnavbar'
redeem_list = []
purchase_list = []
purchase_hdr =  ['Title','Date of Purchase', 'Price', 'Link']

#Defining functions here

# making a simple timestamp function
def stamp(str):
    return rprint(f'[{datetime.now().time().replace(microsecond=0)}]',f' {str}')

#Humble Account Handler
'''
This function will check if a cookie was previously created and prompt the user if they want to reuse it (to reuse login sessions).
It will also check if headless option is enabled, and ask the user if they want to disable it to login in the browser on their own.
They can login to steam and humble bundle, keep the tabs open and the press any key in the console to continue saving cookies for all open tabs.

If the user wishes to keep the headless browser enabled, they will get to sign in to humblebundle only through the console.
'''
def humble_login(options):
    global driver
    print(any( a.__contains__('_login_cookie.pkl') for a in os.listdir()))
    if any( a.__contains__('_login_cookie.pkl') for a in os.listdir()):
        cookie_exists = True
        use_key = input('\n+++++++++++++++++++++++++++\nAn encrypted cookie was found, do you want to use it? (Y/N) ')
        if use_key.lower() in ('y' , 'yes'):
            tries = 0
            while tries < 3:
                
                
                try:
                    keygen = input('\nPlease provide the safe key: ')
                    fernet = Fernet(keygen)
                    break
                except:
                    print('\nInvalid key!\nHint: If you lost your key, please restart and choose No when prompted about the encrypted cookie.')
                    tries += 1
                    if tries == 3:
                        print('failed 3 times. defaulting to no cookies.')
                        cookie_exists = False
                        break
                    continue
            
            
            if cookie_exists:
                # options.add_argument("user-data-dir=/Chrome/")
                driver = webdriver.Chrome(service=Service(ChromeDriverManager(log_level=1).install()), options=options)
                driver.execute_cdp_cmd('Network.enable', {})
                cookie_names = [f for f in os.listdir() if f.__contains__('_login_cookie.pkl')]
                for coo in cookie_names:
                    with open(f'{coo}','rb') as hcook:
                        encrypted_cookie =  pickle.load(hcook)
                        cookies = json.loads(fernet.decrypt(encrypted_cookie).decode())

                        for c in cookies:
                            #if c['domain'].startswith('.'):
                            #   c['domain'] = 'https://www.'+c['domain'][1:]

                            driver.execute_cdp_cmd('Network.setCookie',c)
                            #if driver.current_url.__contains__('.') and driver.current_url.split('.')[1] != c['domain'].split('.')[1] :
                            #    driver.get(c['domain'])

                        print('Successfully decrypted and loaded cookie!')
                    

                    # purchase_page = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.CLASS_NAME, 'results')))
                    print('\n**Loading Purchased Bundles Page Successful**\n**Login Check: Passed!**\n\n')
 
                return driver.get(url_purchases)

        elif use_key in ('n','no'):
            print('Ignoring cookie...')
            cookie_exists = False
        else:
            pass
    else:
        cookie_exists = False
    

    ask_ = ''

    while ask_.lower() not in ('y','n','yes','no') and cookie_exists == False:    
        ask_ = input(
            '\n########################\nYou are about to be required to input your username and password for HumbleBundle.'
            +'\n'+'If you have 2FA enabled, you will be required to input it every time you try to login (Once only per run).'
            +'\n'+ 'Do you want to save login information and generate a safe key upon login? (Y/N)'
            +'\n\n'+'(Y)es: Save a login cookie after logging in, encrypt it, and give you a key for next time to unlock the cookie. [Next run, just use the safe key!]'
            +'\n'+'(N)o: Will not save anything, next time you login you will be asked this again. [You will have to input login details everytime you choose this]'
            +'\n'+'Answer:>> '
        )
        print('\n########################\nLoading...\n\n')

    if options.headless:

        confirm_headless = input("Headless browsing will be disabled, you'll have to login through website(s) instead of console, continue (Y/N)?")
        if confirm_headless.lower() in ('y','yes'):
            options.headless = False
            driver = webdriver.Chrome(service=Service(ChromeDriverManager(log_level=0).install()), options=options)
            driver.execute_cdp_cmd('Network.enable', {})
    else:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager(log_level=0).install()), options=options)
        driver.execute_cdp_cmd('Network.enable', {})
    
    driver.get(url=url_purchases)

    if options.headless:

        login_page = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, 'login-form-view')))
        username = login_page.find_element(By.CLASS_NAME, 'email-field').find_element(By.TAG_NAME, 'input')
        password = login_page.find_element(By.CLASS_NAME, 'password-field').find_element(By.TAG_NAME, 'input')

        username.send_keys(input('HB Email: '))
        password.send_keys(input('HB Password: '))
        password.send_keys(u'\ue007')

        auth_page = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, 'code-field')))
        auth_code = auth_page.find_element(By.TAG_NAME, 'input')
        auth_code.send_keys(input('Authenticator Code (google Auth): '))
        auth_button = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.TAG_NAME, 'button')))
        auth_button.click()
        #auth_code.send_keys(u'\ue007')

    input("When you're done logging in, press any key to save encrypted cookies and get the safe key...")
    if ask_ in ('y','yes'):
        keygen = Fernet.generate_key()
        fernet = Fernet(keygen)
        print(f'\n\n***Your safe key is: {str(keygen)[2:-1]}','\nPlease save it somewhere safe.')

        purchase_page = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.CLASS_NAME, 'results')))
        print('\n**Loading Purchased Bundles Page Successful**\n**Login Check: Passed!**\n')
        for i in driver.window_handles:
            driver.switch_to.window(i)
            filename = driver.current_url.split('.')[1]
            with open(f'{filename}_login_cookie.pkl','wb') as hcook:
                plain_cookies = json.dumps(driver.get_cookies()).encode()
                encrypted_cookies = fernet.encrypt(plain_cookies)
                pickle.dump(encrypted_cookies,hcook) 

        print(f'Encrypted cookie has been saved.\n\n')


        return driver.get(url_purchases)

    if ask_ in ('n','no'):
        purchase_page = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.CLASS_NAME, 'results')))
        result = driver
        print('\n**Loading Purchased Bundles Page Successful**\n**Login Check: Passed!**\n+++++++++++++++++++++++++++\n')
        return driver.get(url_purchases)
    
    return driver.get(url_purchases)
    

#HumbleBundle current bundles: Book, Software, Game.
'''
This function will simply visit the main page, collect bundles' names, bundles' items, and store them in a separate spreadsheet.
If bundle exists in spreadsheet, it will simply ignore, if new bundle pops up, it adds it under the respective category (book, game, software).
''' 
bundle_tiers = {}
def humble_curr():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager(log_level=1).install()), options=options)
    driver.get('https://www.humblebundle.com/bundles?hmb_source=navbar')
    bundle_elements = driver.find_elements(By.CLASS_NAME, 'tile-holder')
    main_window = driver.current_window_handle
    for bundle in bundle_elements:
        action = ActionChains(driver)
        action.key_down(Keys.CONTROL).click(bundle).key_up(Keys.CONTROL).perform()
    
        driver.switch_to.window(main_window)

    if driver.current_window_handle == main_window:
        driver.implicitly_wait(5)
        driver.close()

    while len(driver.window_handles) >= 1:   
        for tab in driver.window_handles:
            driver.switch_to.window(tab)
            stamp(f'Current bundle: {driver.title}')
            bundle_title  =  driver.find_element(By.CLASS_NAME, 'bundle-logo').get_attribute('alt')
            bundle_tiers[f'{bundle_title}'] = {}
            tier_filters = driver.find_elements(By.CLASS_NAME, 'js-tier-filter')
            if len(tier_filters) != 0:
                if  tier_filters[0].text.lower().__contains__('entire'):
                    tier_filters.reverse()
                for tier in tier_filters:
                    tier.click()
                    tier_price = [price for price in driver.find_element(By.CLASS_NAME, 'tier-header').text.split(' ') if price.__contains__('$')][0]

                    if len(driver.find_elements(By.CLASS_NAME, 'item-title')) != 0:
                        driver.execute_script("window.stop();")
                    while True:
                        try:
                            bundle_items = [bundle_tiers[f'{bundle_title}'][y] for y in bundle_tiers[f'{bundle_title}']]
                            bundle_main_pack = [i.text for i in driver.find_elements(By.CLASS_NAME, 'item-title') if i.text not in  [x for l in bundle_items for x in l]]
                            break
                        except StaleElementReferenceException:
                            continue
                    
                    bundle_tiers[f'{bundle_title}'][f'Tier {tier_price}'] = bundle_main_pack
            else:
                tier_price = driver.find_element(By.CLASS_NAME, 'tier-header').text.split(' ')[3]
                driver.implicitly_wait(10)
                bundle_items = [bundle_tiers[f'{bundle_title}'][y] for y in bundle_tiers[f'{bundle_title}']]
                bundle_main_pack = [i.text for i in driver.find_elements(By.CLASS_NAME, 'item-title') if i.text not in  [x for l in bundle_items for x in l]]

                bundle_tiers[f'{bundle_title}'][f'Tier {tier_price}'] = bundle_main_pack
            driver.close()
        return bundle_tiers


#Humble Purchased bundles prepation.
'''
This function will go through the bundles pages and aggregates all the data to be placed in a datasheet.
'''
def humble_prep(opt):
    while True:    
        tab_bars = WebDriverWait(driver,20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'tabbar-tab')))
        for k in tab_bars:
            k.click()        
        redeem_tab = tab_bars[2]
        purchase_tab = tab_bars[1]
        
        if opt == '2':
            print('Collecting: Purchases Tab')
            purchase_tab.click()
            
            purchase_page = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.CLASS_NAME, 'js-purchase-holder')))
            paginate = purchase_page.find_element(By.CLASS_NAME, 'pagination').find_elements(By.CLASS_NAME, 'js-jump-to-page')
            
            if len(paginate) >1:
                for num,pg in enumerate(paginate):
                    if len(paginate) == num+1:
                        break
                    try:
                        while True:
                                while True:
                                    try:
                                        WebDriverWait(driver,20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'order-placed')))
                                        break
                                    except NoSuchElementException:
                                        continue
                                purchase_list_p = []
                                while len(purchase_list_p) == 0:
                                    purchase_page = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.CLASS_NAME, 'js-purchase-holder')))
                                    table_rows = [p for p in purchase_page.find_elements(By.CSS_SELECTOR, 'div.row.js-row')]
                                    purchase_list_p = [ [' '.join(h.text.split(' ')[:-4]), ' '.join(h.text.split(' ')[-4:-1]), (' '.join(h.text.split(' ')[-1]).replace(' ',"")), f'https://www.humblebundle.com/downloads?key='+ table_rows[j].get_attribute('data-hb-gamekey')]  for j,h in enumerate(table_rows)]
                                    if len(purchase_list_p) == 0:
                                        continue
                                    else:
                                        purchase_list.extend(purchase_list_p)
                                        break
                                break
                        while True:
                            try:
                                purchase_page = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.CLASS_NAME, 'js-purchase-holder')))
                                paginate = purchase_page.find_element(By.CLASS_NAME, 'pagination').find_elements(By.CLASS_NAME, 'js-jump-to-page')
                                
                                if paginate[-1].text != purchase_page.find_element(By.CLASS_NAME, 'current').text:
                                    paginate[-1].find_element(By.CLASS_NAME, 'hb-chevron-right')
                                    print('Purchase Page:', paginate[num].text,f'/{paginate[-2].text}')
                                    paginate[-1].click()
                                    break
                                else:
                                    print(f'Purchase page: {paginate[-1].text}/{purchase_page.find_element(By.CLASS_NAME, "current").text}')
                                    break
                            except StaleElementReferenceException:
                                continue
                    except NoSuchElementException:
                        break
                return purchase_list
        elif opt == '1':
            print('\nCollecting: Key and Entitlements Tab.')
            redeem_tab.click()
            try:
                WebDriverWait(driver,20).until(EC.presence_of_element_located((By.CLASS_NAME, 'game-name')))
                redeem_page = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.CLASS_NAME, 'js-key-manager-holder')))
                paginate = redeem_page.find_element(By.CLASS_NAME, 'pagination').find_elements(By.CLASS_NAME, 'js-jump-to-page')
                last_page=paginate[-2].text
                for q in paginate:    
                    
                    try:
                        next_button = paginate[-1] 
                    except NoSuchElementException:
                        pass
                    redeem_table = WebDriverWait(driver,60).until(EC.presence_of_element_located((By.TAG_NAME, 'tbody')))
                    redeem_elements = [k for k in redeem_table.text.split('\n')]
                    if len(redeem_elements) > 8 :
                        redeem_rows = driver.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
                        redeem_list_part = []
                        try:
                            for i,r in enumerate(redeem_rows):
                                redeem_list_part.append([r.find_element(By.CLASS_NAME, 'game-name').find_element(By.TAG_NAME, 'h4').text,
                                r.find_element(By.TAG_NAME, 'p').text, r.find_element(By.CLASS_NAME, 'keyfield-value').text
                                ])
                                try:
                                    redeem_list_part[i].extend([r.find_element(By.CLASS_NAME, 'disclaimer').text])
                                except NoSuchElementException:
                                    pass
                                try:
                                    redeem_list_part[i].extend([r.find_element(By.CLASS_NAME, 'custom-instruction').text])
                                except NoSuchElementException:
                                    pass
                                try:
                                    redeem_list_part[i].extend( [r.find_element(By.CLASS_NAME, 'expiration-messaging').text] )
                                except NoSuchElementException:
                                    pass
                                try:
                                    redeem_list_part[i].extend([r.find_element(By.LINK_TEXT, 'Redemption Instructions').get_attribute('href')])
                                except NoSuchElementException:
                                    pass
                            if len(redeem_list_part) !=0 :
                                redeem_list.extend(redeem_list_part)
                            print(f'Redeem page: {redeem_page.find_element(By.CLASS_NAME, "current").text}/{last_page}')
                            if redeem_page.find_element(By.CLASS_NAME, 'current').text != last_page:
                                try:
                                    next_button.click()
                                except StaleElementReferenceException:
                                    next_button = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.CLASS_NAME, 'js-key-manager-holder'))).find_elements(By.CLASS_NAME, 'js-jump-to-page')[-1]
                                    next_button.click()
                            else:
                                break
                        except NoSuchElementException:
                            break
                return redeem_list
            except NoSuchElementException:       
                break
        elif opt == '4':
            pass
        
            
    

'''Requires login to steam'''
lib_items = {}
def redeem(keys):
    keys = []
    
    driver.get("https://store.steampowered.com")
    profile_link = driver.find_element(By.CLASS_NAME, 'playerAvatar').find_element(By.TAG_NAME, 'a').get_attribute('href')
    games_on_steam = profile_link+'games/?tab=all'
    driver.get(games_on_steam)
    steam_games =[name.find_element(By.CLASS_NAME, 'gameListRowItemName').text for name in driver.find_elements(By.CLASS_NAME, "gameListRow")]
    for i in library_items:
        if len(library_items[i]["Platform"]) !=0 and library_items[i]["Platform"][0] == "Steam":
            keys.extend(library_items[i]["Key"])
            if i in steam_games:
                print(f'{i} is in your steam library.')
            else:
                print(f'{i} will be added.')
        else:
            continue
    for key in keys:
        print(key)
        #driver.get(f"https://store.steampowered.com/account/registerkey?key={key}")
        #continue_button = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID, "register_btn")))
        #agree_box = driver.find_element(By.ID, "accept_ssa")

        #agree_box.click()
        #continue_button.click()
    pass


def if_exists(identifier,by="class name",multi_on=True):
    try:
        if multi_on == True and by.lower() in "class name":
            return driver.find_elements(By.CLASS_NAME, f"{identifier}")
        elif multi_on == False and by.lower() in "class name":
            return driver.find_element(By.CLASS_NAME, f"{identifier}")
        elif multi_on == False and by.lower() in "id":
            return driver.find_element(By.ID, f"{identifier}")
        elif multi_on == True and by.lower() in "id":
            return driver.find_elements(By.ID, f"{identifier}")
    except NoSuchElementException:
        class nothing():
            def __init__(self):
                text = self.text 
            text = None
            

        return nothing


library_items = {}
def expiry():
    global library_items
    tab_bars = WebDriverWait(driver,20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'tabbar-tab')))
    library_tab = tab_bars[0]
    library_tab.click()
    products = WebDriverWait(driver,20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "subproduct-selector")))

    for product in products:
        product.click()
        item_name = ": ".join(product.text.split("\n"))
        folder_name = product.text.split("\n")[-1]
        if os.path.isdir('/Humble Downloads') is False:
            os.mkdir('/Humble Downloads')
        prefs = {'download.default_directory' : f'/Humble Downloads/{folder_name}'}
        options.add_experimental_option('prefs', prefs)
        if if_exists("keyfield-value") != None:

            library_items[item_name] = {
            "Key"           : [red_key.text for red_key in if_exists("keyfield-value") if not red_key.text.__contains__('expir')],
            "Expiration"    : [expiry.text for expiry in if_exists("expiration-messaging") ],
            "Tab"           : product,
            "Platform"      : [p.text.split("\n")[0] for p in if_exists("platform")]
        }
        if if_exists("js-download-button") != None:
            downloads = if_exists("js-download-button")
            for i in downloads:
                if i.text == "":
                    continue
                library_items[item_name][i.text.split("\n")[0]] =  i 
    return library_items
    
if __name__ == "__main__":

    #declaring some global variables that will be used all over the place
    options = Options()                             #Declaring a variable with 'Options()' method from selenium. will allow us to add custom options to our chrome simulator
    options.add_argument('--disable-logging')       #Disabling simulator logs, we don't need to read it's status reports.
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    opt = ''
    headless = 'Enable'

    while True:
 
        print('###########[Humble+Helper]###########')
        opt = input(f'[1] Check Keys for Expiry. \n[2] Redeem Keys. \n[3] View Duplicate Keys. \n[4] Save a local spreadsheet. \n[5] Log current bundles.\n[6] {headless} Headless Browser (--headless)  \n====== \nChoose a number: ')
        if opt in '6':
            print(f'###{headless}d headless browser.\n')
            if headless =='Enable':
                options.headless = True
                headless = 'Disable'
            elif headless == 'Disable':
                options.headless = False
                headless ='Enable'
            continue
        elif opt not in '12345':
            print('Please input a valid number...')
            continue
        else:
            break
    


    if opt in '5':
        tiers = humble_curr()
        df = pd.DataFrame(tiers)
        df.to_csv(f'[{datetime.today().date()}]Humble_Bundles.csv')
    elif opt not in '5':
        humble_login(options)
    elif opt in '1':
        humble_prep(opt)
        print(redeem_list)
        pd.DataFrame(redeem_list).to_csv(f'[{datetime.today().date()}] Humble Bundle Key info.csv')
    
    elif opt in '2':
        redeem(library_items)
    elif opt in '3':
        humble_prep(opt='1')
        print(redeem_list)
    elif opt in '4':
        p_list = humble_prep(opt)

        pd.DataFrame(purchase_list, columns=purchase_hdr).to_csv(f'[{datetime.today().date()}] Humble Bundle Purchase info.csv')



    print(f'\nScript Finished.\n######################\nSummary:\n~Total purchases: {len(purchase_list)} items @ ${sum([float(k[-2][3:]) for k in purchase_list if not k[-2].__contains__("-")])}\n~Total Keys: {len(redeem_list)}, {len(redeem_list)-len(set([k[0] for k in redeem_list]))} duplicate(s)\n')




