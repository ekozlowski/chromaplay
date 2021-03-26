import random
import threading
import time

class Person:
    def __init__(self, name):
        self.name = name
        self.is_running = True

    def say_name(self):
        print(f"Hi, my name is: {self.name}")
    


def say_name(person):
    # while we're running, if the last API request is more than 5 seconds 
    # old, make a keepalive API request, until the Chroma object's running
    # attribute is False.
    while person.is_running:
        print(f"threading.active_count is {threading.active_count()}")
        person.say_name()
        sleep_time = random.randint(1,5)
        print(f"{person.name} going back to sleep for {sleep_time} seconds.")
        time.sleep(sleep_time)
        

people = [Person('1'), Person('2'), Person('3')]

running_threads = []

### Start threaded processes ###
for p in people:
    person_thread = threading.Thread(target=say_name, args=(p,))
    person_thread.start()
    running_threads.append(person_thread)

### end starting threaded processes ###

### Main program loop ###
for x in range(10):
    print(f"Main thread running {x}")
    time.sleep(5)
### end main program loop ###


### Start cleanup of sub processes / threads ###
for p in people:
    p.is_running = False

for r in running_threads:
    r.join()

### end thread cleanup ###

print("Program ended.")
