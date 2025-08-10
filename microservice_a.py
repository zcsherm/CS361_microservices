# Microservice A
# Reads from a text file
# Fetches a file
# writes that file/file_location to the text file
#
# reads from text file
# Gets a new image from text file
# Updates the requested file with the new image
import os
import shutil
import time

PIPE = "image_pipe.txt"
FETCH_REQUEST = "FETCH"
WRITE_REQUEST = "WRITE"
QUIT_REQUEST = "QUIT"
REQUESTS = [FETCH_REQUEST, WRITE_REQUEST, QUIT_REQUEST]

PASSED_READ = "ACCEPT"
FAILED_READ = "INVALID"

NOT_FOUND = "404"
TIMED_OUT = "408"
SUCCESS = "200"

IMAGE_DIRECTORY = 'card_image'
IMAGE_TYPE = '.png'

class Microservice:
    def __init__(self):
        self.last_write = None
        self.make_pipe()
        self.make_image_directory()
        self.main()
        
    def main(self):
        """
        Reads the communication pipe and executes the requested action
        """
        # Keep reading the pipe every second, as long as it was not instructed to terminate
        while self.last_write != QUIT_REQUEST:
            time.sleep(1)
            with open(PIPE, "r") as file:
                content = file.read().upper()

            # Execute the desired request
            if content in REQUESTS:
                if content == FETCH_REQUEST:
                    self.fetch_file()
                if content == WRITE_REQUEST:
                    self.overwrite_file()
                if content == QUIT_REQUEST:
                    self.quit()

            # If the request was invalid, communicate an error to client
            elif content != self.last_write and content != '':
                self.write_to_pipe(FAILED_READ)

    def fetch_file(self):
        """
        Finds a requested resource and writes the absolute file path to the pipeline
        """
        # Send back to the client that the request was successful and that we are waiting for the resource name
        self.write_to_pipe(PASSED_READ)
        timer = 0

        # Read the pipe very 1/2 second until 10 seconds have elapsed or we have written the file path
        while self.last_write == PASSED_READ:
            time.sleep(.5)
            with open(PIPE, "r") as file:
                content = file.read()

            # strip the whitespace from the clients requested resource, find the resource and write it to the pipe
            if content != PASSED_READ and content != '':
                content = content.strip()
                file = self.locate_file(content)
                self.write_to_pipe(file)

            # If 10 seconds have elapsed without a request from the client, send back a time out error and return to main
            if timer > 20:
                self.write_to_pipe(TIMED_OUT)
            timer += 1
    
    def write_to_pipe(self, contents):
        """
        Writes a given message to the pipeline and saves what was written
        :param contents: The message to be written
        """
        with open(PIPE, "w") as file:
            file.write(contents)
        self.last_write = contents
    
    def locate_file(self, query):
        """
        Get the absolute path to the requested resource.
        :query: The resource to be searched for
        """
        file_name = query.lower()
        if IMAGE_TYPE not in file_name:
            file_name = file_name + IMAGE_TYPE
        file_path = os.path.abspath(IMAGE_DIRECTORY + '/' + file_name)
        if not os.path.isfile(file_path):
            file_path = NOT_FOUND
        return file_path
            
    def overwrite_file(self):
        """
        Overwrites a resource with a new file provided by the client
        """
        # Send that request was succesful and that we are waiting for the file
        self.write_to_pipe(PASSED_READ)
        timer = 0

        # Read the pipe every .5 seconds until we have written to the pipe again
        while self.last_write == PASSED_READ:
            time.sleep(.5)
            with open(PIPE, "r") as file:
                content = file.read()

            # Try to replace the original resource with the new resource and send back a status code
            if content != PASSED_READ and content != '':
                replace_status = self.replace_file(content)
                self.write_to_pipe(replace_status)

            # Time out after 10 seconds and return to main
            if timer > 20:
                self.write_to_pipe(TIMED_OUT)
            timer += 1

    def replace_file(self, filename):
        """
        Copies a source file to the IMAGE_DIRECTORY, replacing the original
        :param filename: The absolute path to the source file
        """
        # Verify that the supplied file path exists
        if not os.path.isfile(filename):
            return NOT_FOUND

        # Strip out the resource name
        original_file = ""
        for i in range(len(filename),0,-1):
            if filename[i] == '/' or filename[i] == "\\":
                original_file = filename[i + 1:]
                break
        original_file = IMAGE_DIRECTORY + '/' + original_file

        # Verify that the resource exists
        if not os.path.isfile(IMAGE_DIRECTORY + '/' + original_file):
            return NOT_FOUND

        # Delete the original resource and replace it
        os.remove(IMAGE_DIRECTORY + '/' + original_file)
        shutil.copy(filename, original_file)
        return SUCCESS
    
    def make_pipe(self):
        if not os.path.isfile(PIPE):
            with open(PIPE, 'w') as file:
                file.write('')
    
    def make_image_directory(self):
        if not os.path.isdir(IMAGE_DIRECTORY):
            os.mkdir(IMAGE_DIRECTORY)

    def quit(self):
        self.write_to_pipe('')
        self.last_write = QUIT_REQUEST


if __name__ == '__main__':
    Microservice()