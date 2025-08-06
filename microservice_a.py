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

CANT_FIND = "404"
TIMED_OUT = "408"

class Microservice:
    def __init__(self):
        self.last_write = None
        self.main()

    def main(self):
        while True:
            time.sleep(1)
            with open(PIPE, "r") as file:
                content = file.read().upper()
            if content in REQUESTS:
                if content == FETCH_REQUEST:
                    self.fetch_file()
                if content == WRITE_REQUEST:
                    self.overwrite_file()
                if content == QUIT_REQUEST:
                    return
            elif content != self.last_write:
                self.request_error(content)

    def fetch_file(self):
        with open(PIPE, "w") as file:
            file.write(PASSED_READ)
        content = PASSED_READ
        while content == PASSED_READ:
            count = 0
            time.sleep(.5)
            with open(PIPE, "r") as file:
                content = file.read()
            if content != PASSED_READ:
                content = content.lower().strip()
                file = self.locate_file(content)
    def overwrite_file(self):
        pass
