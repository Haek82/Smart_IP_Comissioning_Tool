import random

class BlinkInsults:

    def __init__(self):
        self.insults = ["Blink Blink???!", "Can´t find your speaker huh?", "HAAA HAA !!!", "Try a little harder yes?", "A little more to the left!", "A Little more to the right!", "Have you tried to look up in roof?", "Are you color blind or someting?", "RUN FORREST RUN !!!!!!"]
        self.count = 0

    def blinkIncr(self):
        self.count += 1

        if self.count > 1:
            print()
            print(random.choice(self.insults))
            print()
