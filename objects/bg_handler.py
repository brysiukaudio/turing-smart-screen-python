import os

class background_handler:
    def __init__(self):
        self.background_array = []
        self.background_index = 0
        self.redraw = False

    def get_index(self):
        return self.background_index

    def get_current_item(self):
        item = self.background_array[self.background_index]
        self.background_index = self.background_index + 1
        if(self.background_index >= len(self.background_array)):
            self.background_index = 0
        return item

    def get_item_at_index(self,index):
        if(index < len(self.background_array)):
            return self.background_array[index]
        else:
            return self.background_array[self.background_index]

    def load_backgrounds(self,background_path):
        self.background_array.clear()
        for file in os.listdir(background_path):
            self.background_array.append(background_path + file)
        self.background_index = 0
        self.redraw = True

    def check_redraw(self):
        return self.redraw

    def clear_redraw(self):
        self.redraw = False