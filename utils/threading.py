import os
import shutil
from threading import Thread

import numpy as np
import undetected_chromedriver as webdriver
from selenium.webdriver import Chrome


class ThreadWithReturnValue(Thread):
    
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        a = Thread.join(self, *args)
        #print("return: ",self._return, a)
        return self._return
    

def quit_drivers(drivers):
    if type(drivers) == Chrome:
        drivers.quit()
    if type(drivers) == list:
        for driver in drivers:
            quit_drivers(driver)
    del drivers

def init_drivers_instances(nb_pages=1, *args): # args = (Func, number_drivers) and pages
    t = []
    drivers_types = []
    processes = []
    for arg in args:
        t.append(ThreadWithReturnValue(target = init_drivers, 
                                       args = [arg[1], arg[0], arg[2], [], nb_pages] ))
    for thread in t:
        thread.start()
    for thread in t:
        drivers_types.append(thread.join())
    
    print("drivers_types", drivers_types)
    
    for i in range(nb_pages):
        processes.append([driver for drivers in drivers_types for driver in drivers[i]])
    
    print("processes", processes)
    
    return processes
        

  
def init_drivers(number=1, func=Chrome, args=[], drivers_: list = [], nb_pages=1):
    drivers_ = list(np.array(drivers_).flat)
    for driver in drivers_:
        try:
            driver.quit()
        except:
            pass
    drivers_=None
    if drivers_ is None :
        # List of parallel processes. Each process is a list of drivers.
        drivers_ = [[] for i in range(nb_pages)]
    else:
    # get list of number of drivers to launch per list_of_drivers:
    # launch number of threads of the sum of the list 
    # according to the list, add the number of drivers correctly
    
    # for drivers_list in drivers and in range pages:
        # check if list
            # drivers[:number]
            # else append
        
        pass
    
    #for driver in drivers:
    #    try:
    #        a = driver.find_elements(By.ID, "a")
    #        new_drivers.append(driver)
    #    except Exception as e:
    #       print("can't find shit") 
    #drivers= new_drivers
    
    l_ = len(list(np.array(drivers_).flat))
    
    # Number of drivers to create
    range_ = (number*nb_pages)-l_
    
    print("range:",range_)
    t=[0]*range_
    if range_ >= 0:
        for i in range(range_):
            t[i] = (ThreadWithReturnValue(target=func, args=args, Verbose=False))
        for i in t:
            i.start()
        for ind, i in enumerate(t):
            a = i.join()
            drivers_[ind//number].append(a)
    else:
        for driver in driver[number:]:
            driver.quit()
            del driver
        drivers_ = drivers_[:number] 
    #list_drivers = []
    #for i in range(nb_pages):
    #    list_drivers.append(drivers_[i*nb_pages:(i+1)*nb_pages])
    return drivers_


def force_patcher_to_use(directory):
    # copy the chromedriver in directory
    exe = webdriver.Patcher.exe_name.replace("%s",".exe")
    #exe = r'C:\Users\sever\AppData\Roaming\undetected_chromedriver\undetected\chromedriver-win32\chromedriver.exe'
    src = os.path.join(webdriver.Patcher.data_path, exe)
    executable_path = os.path.join(directory, exe)
    shutil.copyfile(src, executable_path)

    # monkey patch the Patcher class
    class PatcherWithForcedExecutablePath(webdriver.Patcher):
        def __init__(self, *args, **kwargs):
            kwargs["executable_path"] = executable_path
            super().__init__(*args, **kwargs)

    webdriver.Patcher = PatcherWithForcedExecutablePath

    return executable_path
