import datetime
import inspect
import time


class Trace:

    TAB = '   |'  # string used to build the indent
    indent = 0    # indent level
    filterset = ''
    
    def __init__(self, func):
        self.func = func
        
    def __call__(self, *args, **kwargs):
        try:
            # Print when entering a function
            Trace.indent += 1
            print(self.__prefix() + "\b> " + f"{self.func.__name__} args={args}")
            result = self.func(*args, **kwargs)
            # Print when exiting a function
            print(self.__prefix() + "\b< " + f"{self.func.__name__} returned {result}")
            Trace.indent -= 1
            return result
        except Exception as e:
            # Print when an exception happens
            print(self.__prefix() + "\b! " + f"{self.func.__name__} exception: {e}")
            Trace.indent -= 1
            
    def __prefix(self):
        now = datetime.datetime.now()
        return(now.strftime("%H:%M:%S") + Trace.TAB * Trace.indent)

    def all(filter = '*'):
        # Print variables
        if (filter in Trace.filterset) | (filter == '*'):
            now = datetime.datetime.now()
            print(now.strftime("%H:%M:%S") + Trace.TAB * Trace.indent + " vars: " + f"{inspect.stack()[1].frame.f_locals}")
  
    def var(s, filter = '*'):
        # Print variables:
        # Trace(f"x = {x} y = {y}")
        if (filter in Trace.filterset) | (filter == '*'):
            if len(s) > 0:
                now = datetime.datetime.now()
                print(now.strftime("%H:%M:%S") + Trace.TAB * Trace.indent + " vars:" + " " f"{s}")
 
    def filter(f):
        filterset = f
                   

