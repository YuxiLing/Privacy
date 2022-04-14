from logging import StringTemplateStyle
import os
import shutil
import json
import random
import subprocess
import signal
import time
import tkinter
from tkinter import *
from bs4 import BeautifulSoup
from matplotlib.pyplot import close
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from multiprocessing.dummy import Pool as ThreadPool
import timeout_decorator
import time

DATE="5_19"

current_index = 0
crx_folder_name='../chrome_ext/install_test'
log_file_path='../chrome_ext/log.txt'
finished_file_path='../chrome_ext/finished_list.txt'

def handle_extension(extension_driver):
    # do sth like pressing buttons
    return True
def get_default_page_path(path_to_extension):
    manifest_path=path_to_extension+'manifest.json'
    with open(manifest_path,'r') as f:
        settings=json.load(f)
    try:
        default_path=settings["browser_action"]["default_popup"]
    except:
        print("there is no initial popup page")
        print("there is no initial popup page",file=open(log_file_path,'a'))
        default_path=""
    return default_path

def reset_dir(path):
    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)
    os.mkdir(path)

def save_page(origin_id,page_content):
    random_file_name=str(random.randint(0,10000))
    file_path=crx_folder_name+'/'+origin_id+'_pages/'+random_file_name+'.html'
    with open(file_path,'w') as f:
        f.write(page_content)
        
@timeout_decorator.timeout(20)
def start_extension(foldername):
    extension_folder=crx_folder_name
    path_to_extension = extension_folder+'/'+foldername+'/'
    origin_id=foldername
    chrome_options = Options()
    chrome_options.add_argument('load-extension=' + path_to_extension)
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation']) 

    driver = webdriver.Chrome(options=chrome_options)

    driver.create_options()
    # open the manager page of the chrome extension
    driver.get("chrome://extensions/")
    driver.switch_to.window(driver.window_handles[0])
    
    # get the real id of the extension
    element=driver.find_element(By.CSS_SELECTOR,"extensions-manager")
    #print(element.get_attribute('innerHTML'))
    shadow_root1 = driver.execute_script('return arguments[0].shadowRoot', element)
    # element1=shadow_root1.find_element_by_css_selector("cr-view-manager")
    element2=shadow_root1.find_element(By.CSS_SELECTOR,"extensions-item-list")
    shadow_root2 = driver.execute_script('return arguments[0].shadowRoot', element2)
    # print(str(shadow_root2))
    element3=shadow_root2.find_element(By.CSS_SELECTOR,"#container")
    element4=element3.find_element(By.ID,"content-wrapper")
    element5=element4.find_element(By.CLASS_NAME,"items-container")
    element6=element5.find_element(By.CSS_SELECTOR,'extensions-item')
     
    extension_id=element6.get_attribute('id')
    print(extension_id)
    print(extension_id,file=open(log_file_path,'a'))
    print(extension_id,file=open(finished_file_path,'a'))
    # get the initial page of the extension
    # extension_id="***"
    popup_page=get_default_page_path(path_to_extension)
    if popup_page=="":
        print("there is no popup page")
        print("there is no popup page",file=open(log_file_path,'a'))
        driver.quit()
        return

    initial_page="chrome-extension://"+extension_id+'/'+popup_page
    
    # start the mitmproxy
    # the script for the mitmproxy mitm_req_res.py should be in the same path as the current file
    # mitm=subprocess.run('mitmproxy -s mitm_req_res.py' + ' ' + DATE + ' ' + extension_id, shell=True)
    
    # driver.close()
    
    # trigger all the button and collect page element
    # start the test automatically
    driver.get(initial_page)
    current_windows = driver.window_handles
    driver.switch_to.window(current_windows[-1]) 
    while len(current_windows)>1:
        driver.close()
        current_windows = driver.window_handles
        driver.switch_to.window(current_windows[-1]) 
    # wait the page to be loaded
    time.sleep(1)

    reset_dir(crx_folder_name+'/'+origin_id+'_pages/')
    save_page(origin_id,driver.execute_script("return document.body.innerHTML"))
    # print("=============")
    # print(driver.page_source)
    # print("=============")
    buttons=driver.find_elements(By.XPATH,"//*")
    button_count=len(buttons)
    print("number of available buttons",button_count)
    print("number of available buttons",file=open(log_file_path,'a'))
    for i in range(button_count):
        try:
            current_page=driver.current_window_handle
            buttons=driver.find_elements(By.XPATH,"//*")
            button=buttons[i]
            button.click()
            time.sleep(0.5) # wait the page loading
            print('click on one button')
            print('click on one button',file=open(log_file_path,'a'))
            save_page(origin_id,driver.execute_script("return document.body.innerHTML"))
            # need to check is there a new tab loaded
            new_page=driver.window_handles
            if len(new_page)>1:
                print("open a new page")
                print("open a new page",file=open(log_file_path,'a'))
                driver.switch_to.window(new_page[-1])
                save_page(origin_id,driver.execute_script("return document.body.innerHTML"))
                driver.close()
                print("return to old page")
                print("return to old page",file=open(log_file_path,'a'))
            
            # for new_handle in new_handles:
            #     if new_handle!=current_page:
            #         # This is a new page
            #         # switch to this page and save the content
            #         driver.switch_to.window(new_handle)
            #         time.sleep(0.5)
            #         save_page(origin_id,driver.page_source)
            #         driver.close()
            # driver.switch_to.window(new_handle[0])
            driver.refresh()
            time.sleep(0.5)

        except Exception as e:
            # print(e)
            # time.sleep(0.5)
            pass

    driver.quit()
    # close the mitmproxy by CTL_C signal
    # mitm.send_signal(signal.SIGINT)

def mainGUIinterface(folder_list):
    global current_index
    # current_index = folder_list.index('hcfhemgkgbfonoagglgjcjhaolkacoec')
    current_index=1
    extension_folder = crx_folder_name
    foldername = folder_list[current_index]
    path_to_extension = extension_folder+'/'+foldername+'/'
    start_extension(path_to_extension=path_to_extension,origin_id=foldername)
    def prev():
        print('prev')
        global current_index
        current_index = current_index - 1
        foldername1 = folder_list[current_index]
        path_to_extension1 = extension_folder+'/'+foldername1+'/'
        start_extension(path_to_extension=path_to_extension1,origin_id=foldername1)
    def next():
        print('next')
        global current_index
        current_index += 1
        foldername1 = folder_list[current_index]
        path_to_extension1 = extension_folder+'/'+foldername1+'/'
        start_extension(path_to_extension=path_to_extension1,origin_id=foldername1)
        current_number.set(str(current_index))
        current_name.set(foldername1)
    mainUserInterfaceWindow = tkinter.Tk()
    mainUserInterfaceWindow.title("selection tool")
    mainUserInterfaceWindow.geometry("500x200")

    current_number = tkinter.StringVar()
    current_name = tkinter.StringVar()
    selectioncountmainlabel = tkinter.Label(mainUserInterfaceWindow, text="count: ")
    selectioncountcurrentnumber = tkinter.Label(mainUserInterfaceWindow,textvariable=current_number)
    selectioncounttotalnumber = tkinter.Label(mainUserInterfaceWindow,text="")
    currentnamemainlable = tkinter.Label(mainUserInterfaceWindow,text="current name: ")
    currentnamedispalylabel = tkinter.Label(mainUserInterfaceWindow,textvariable=current_name)

    selectioncountmainlabel.pack()
    selectioncountcurrentnumber.pack()
    selectioncounttotalnumber.pack()
    currentnamemainlable.pack()
    currentnamedispalylabel.pack()

    ###Buttoms
    prevbuttom = tkinter.Button(mainUserInterfaceWindow,text="prev",command=prev)
    nextbuttom = tkinter.Button(mainUserInterfaceWindow,text="next",command=next)

    prevbuttom.pack()
    nextbuttom.pack()

    mainUserInterfaceWindow.mainloop()

def mainWithoutGUIAuto(folder_list):
    # global current_index
    # current_index = folder_list.index('hcfhemgkgbfonoagglgjcjhaolkacoec')
    # current_index=1
    extension_folder = crx_folder_name
    # foldername = folder_list[current_index]
    print("========start extension analysis========")
    print("========start extension analysis========",file=open(log_file_path,'a'))
    '''
    pool=ThreadPool(1)
    pool.map(start_extension,folder_list)
    pool.close()
    pool.join()
    '''
    for foldername in folder_list:
        path_to_extension = extension_folder+'/'+foldername+'/'
        try:
            start_extension(foldername)
        except:
            print(foldername,"timeout")
            print(foldername+" timeout",file=open(log_file_path,'a'))
    
def init():
    extension_folder = crx_folder_name
    print("============start===========")
    f_list = os.listdir(extension_folder)
    print(str(len(f_list)) + ' folders found')
    print(str(len(f_list)) + ' folders found',file=open(log_file_path,'a'))
    f_list.sort()
    return f_list

if __name__=='__main__':
    #mainGUIinterface()
    flist = init()
    #mainGUIinterface(flist)
    mainWithoutGUIAuto(flist)
