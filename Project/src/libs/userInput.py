from time import sleep

class userInput:
    def __init__(self):
        self.user_input = 0
        self.switcher = {
            26: 1,
            19: 2,
            13: 3,
            6: 4,
            5: 5,
        }

    def setUserInput(self, channel):
       self.user_input = self.switcher.get(channel)

    def getUserInput(self):
        return self.user_input

    def handleUserInput(self):
        print("Input: ")
        while True:
            self.user_input = 0
            sleep(0.2)
            if self.user_input != 0:
                print("User Input: ", self.user_input)
                break
