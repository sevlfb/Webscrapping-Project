from threading import Thread

import numpy as np
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


#from threading import Thread
#class ThreadWithReturnValue(Thread):
#    def __init__(self, group=None, target=None, name=None,
#                 args=(), kwargs={}, Verbose=None):
#        Thread.__init__(self, group, target, name, args, kwargs, Verbose)
#        self._return = None
#    def run(self):
#        if self._Thread__target is not None:
#            self._return = self._Thread__target(*self._Thread__args,
#                                                **self._Thread__kwargs)
#    def join(self):
#        Thread.join(self)
#        return self._return




  
def init_drivers(number=1, func=Chrome, args=[], drivers_: list = [], nb_pages=1):
    drivers_ = list(np.array(drivers_).flat)
    for driver in drivers_:
        try:
            driver.quit()
        except:
            pass
    drivers_=None
    if drivers_ is None : 
        drivers_ = [[] for i in range(nb_pages)]
        print("len_driver", len(drivers_), drivers_)
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
    print(l_)
    range_ = (number*nb_pages)-l_
    print("range:",range_)
    t=[0]*range_
    if range_ >= 0:
        for i in range(range_):
            t[i] = (ThreadWithReturnValue(target=func, args=args, Verbose=False))
        for i in t:
            print(i)
            i.start()
            print("return", i._return)
        for ind, i in enumerate(t):
            a = i.join()
            print(a)

            drivers_[ind//number].append(a)
    else:
        print("fuck")
        for driver in driver[number:]:
            driver.quit()
            del driver
        drivers_ = drivers_[:number] 
    #list_drivers = []
    #for i in range(nb_pages):
    #    print(f"fuck {i}")
    #    list_drivers.append(drivers_[i*nb_pages:(i+1)*nb_pages])
    return drivers_

import os
import shutil
import tempfile

import undetected_chromedriver as webdriver


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
