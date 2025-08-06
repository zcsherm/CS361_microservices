# Microservice A
# Reads from a text file
# Fetches a file
# writes that file/file_location to the text file
#
# reads from text file
# Gets a new image from text file
# Updates the requested file with the new image
import os
import time

PIPE = "image_pipe.txt"
FETCH_REQUEST = "FETCH"
WRITE_REQUEST = "WRITE"
QUIT_REQUEST = "QUIT"
REQUESTS = [FETCH_REQUEST, WRITE_REQUEST]

PASSED_READ = "ACCEPT"
FAILED_READ = "INVALID"

NOT_FOUND = "404"
TIMED_OUT = "408"

IMAGE_DIRECTORY = 'card_image/'
i

class Microservice:
    def __init__(self):
        self.last_write = None
        self.make_image_directory()
        self.main()
        
    def main(self):
        while self.last_write != QUIT_REQUEST:
            time.sleep(1)
            with open(PIPE, "r") as file:
                content = file.read().upper()
            if content in REQUESTS:
                if content == FETCH_REQUEST:
                    self.fetch_file()
                if content == WRITE_REQUEST:
                    self.overwrite_file()
                if content == QUIT_REQUEST:
                    self.quit()
            elif content != self.last_write:
                self.request_error(content)

    def fetch_file(self):
        self.write_to_pipe(PASSED_READ)
        timer = 0
        while content == self.last_write:
            time.sleep(.5)
            with open(PIPE, "r") as file:
                content = file.read()
            if content != PASSED_READ:
                content = content.strip()
                file = self.locate_file(content)
                self.write_to_pipe(file)
            if timer > 20:
                self.write_to_pipe(TIMED_OUT)
            timer += 1

    def write_to_pipe(self, contents):
        pass

    def locate_file(self, query):
        file_name = query.lower() + ".png"
        file_path = os.path.abspath(IMAGE_DIRECTORY + file_name)
        if not os.path.isfile(file_path):
            file_path = NOT_FOUND
        return file_path
            
    def overwrite_file(self):
        pass

    def make_image_directory(self):
        pass
