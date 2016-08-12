#!/usr/bin/python

import pypresenter.slide

class slide10(pypresenter.slide):
    def __init__(self):
        super(self.__class__, self).__init__('center')
    def content(self, window=None):
        return "Example of how this can enhance your development process"
    def draw(self, window):
        self.displayText(window, self.content(window))