from time import sleep

class userInput:
    user_input = 0

    def __init__(self):
        pass

    def setUserInput(self, val):
       self.user_input = val

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