class Borg: 
  
    # state shared by each instance 
    __shared_state = dict() 
  
    # constructor method 
    def __init__(self): 
  
        self.__dict__ = self.__shared_state 
  
    def __str__(self): 
  
        return self.state 