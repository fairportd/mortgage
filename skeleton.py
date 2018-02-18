# -*- coding: utf-8 -*-
"""
this is a skeleton template
"""

class Demo:
    def __init__(self):
        self.my_var = 42
        
    def my_func(self):
        print(self.my_var)
        
    def main(self):
        self.my_func()
        
        
def test():
    demo = Demo()
    demo.main()
    
if __name__ == '__main__':
    test()
    