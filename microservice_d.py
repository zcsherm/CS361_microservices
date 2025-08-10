# Takes in a players win loss record
# Maintains a high score record for seasonal performance
# Allows you to view top x scores and users
import time
import os
import pickle

SCORE_DIRECTORY = 'scores'
PIPE = "score_pipe.txt"
MASTER_FILE = SCORE_DIRECTORY + "/" + "master.pkl"
ADD_REQUEST = "ADD"
VIEW_REQUEST = "VIEW"
QUIT_REQUEST = "QUIT"
FAILED_READ = "INVALID"
TIMED_OUT = '408'
USER_SELECT = 'USER'
SEASON_SELECT = 'SEASON'
SCORE_QUANT = 'HOW MANY'
WINS = 'WINS'
LOSSES = 'LOSSES'
SUCCESS = '200'

def write_to_pipe(pipe, message):
    with open(pipe, 'w') as file:
        file.write(message)
def read_pipe(pipe):
    with open(pipe, 'r') as file:
        return file.read()

def read_write_cycle(pipe, message):
    write_to_pipe(pipe, message)
    count = 0
    while count < 20:
        time.sleep(.5)
        content = read_pipe(pipe)
        if content != '' and content != message:
            return content
        count += 1
    return False

class Microservice:
    def __init__(self):
        self.requests = {
                        ADD_REQUEST: self.add_score,
                        VIEW_REQUEST: self.view_score,
                        QUIT_REQUEST: self.quit
                        }
        self.last_write = None
        self.make_pipe()
        self.make_score_directory()
        self.load_score_file()
        self.main()

    def make_pipe(self):
        """
        Creates the communication pipe if it does not exist
        """
        if not os.path.isfile(PIPE):
            print(f"creating pipeline with name {PIPE}...")
            if not os.path.isfile(PIPE):
                with open(PIPE, 'w') as file:
                    file.write('')

    def make_score_directory(self):
        """
        Creates the player directory if it does not exist
        """
        if not os.path.isdir(SCORE_DIRECTORY):
            print(f"creating a player directory with name {SCORE_DIRECTORY}...")
            os.mkdir(SCORE_DIRECTORY)
            self.make_score_file()

    def make_score_file(self):
        if not os.path.isfile(MASTER_FILE):
            scores = []
            with open(MASTER_FILE, 'wb') as file:
                pickle.dump(scores, file)

    def load_score_file(self):
        with open(MASTER_FILE, 'rb') as file:
            self.scores = pickle.load(file)

    def save_score_file(self):
        with open(MASTER_FILE, 'wb') as file:
            pickle.dump(self.scores, file)

    def main(self):
        print(f"listening on {PIPE}...")
        while self.last_write != QUIT_REQUEST:
            time.sleep(1)
            with open(PIPE, "r") as file:
                content = file.read().upper()

            # If there is a client request, route that request to the appropriate function
            if content != '':
                self.route_request(content)

    def route_request(self, content):
        """
        Redirects a client request to the appropriate function
        """
        if content == FAILED_READ:
            return
        print(f"Attempting to handle request from client: {content}")
        try:
            self.requests[content]()
        except KeyError:
            self.invalid_request()

    def invalid_request(self):
        """
        Tell the client that an invalid request type was sent
        """
        if self.last_write == FAILED_READ:
            return
        print(f"Unable to handle request!")
        write_to_pipe(PIPE, FAILED_READ)

    def get_query_params(self):
        """
        Gets request parametes from client
        :return: user, team, and player parameters
        """
        user = self.choose_user()
        if user is not None:
            season = self.choose_season()
            if season is not None:
                wins = self.choose_wins()
                if wins is not None:
                    losses = self.choose_losses()
                    if losses is not None:
                        return user, season, wins, losses
        return None, None, None, None

    def add_score(self):
        # Get parameters for addition from client
        user, season, wins, losses = self.get_query_params()
        print(f"Client sent the following request: Add {user}'s {season} season with score {wins}-{losses} to the scoreboard")
        # Stop execution if the client failed to respond
        if user is None:
            return
        win_percent = int(wins)/(int(losses)+int(wins))
        i = 0
        for i in range(len(self.scores)):
            if win_percent > (self.scores[i]['win_percent']):
                if i == len(self.scores) - 1:
                    i -= 1
                break
        score_obj = {'user':user,'season': season, 'wins': wins, 'losses': losses, 'win_percent': win_percent}
        if i != len(self.scores)-1:
            self.scores.insert(i, score_obj)
        else:
            self.scores.append(score_obj)
        self.save_score_file()
        self.write_to_pipe(SUCCESS)

    def view_score(self):
        num = read_write_cycle(PIPE, SCORE_QUANT)
        if num == '0':
            self.write_to_pipe(FAILED_READ)
        count = 1
        output= ''
        for score in self.scores:
            output += score['user'] +','
            output += score['season']+','
            output += score['wins'] + ','
            output += score['losses']+ '\n'
            count += 1
            if count > int(num):
                break
        self.write_to_pipe(output)

    def quit(self):
        self.write_to_pipe('')
        self.last_write = QUIT_REQUEST
        print("Microservice is shutting down.")

    def send_and_wait_for_message(self, sent_message):
        """
        Sends a message to the pipe line and waits for a response from the client
        :param sent_message: The message to send to the client
        :return: The response from client, or None if timed out
        """
        print(f"Sending request back to client: {sent_message}...")
        self.write_to_pipe(sent_message)

        # Read the pipe for 10 seconds, wait for a response
        count = 0
        while count < 20:
            time.sleep(.5)
            with open(PIPE, "r") as file:
                content = file.read()
            if content != '':
                print(f"Read response from client: {content}...")
                return content
            count += 1

        # After 10 seconds, time out
        print(f"Connection timed out! Client did not respond within 10 seconds.")
        self.write_to_pipe(TIMED_OUT)

    def write_to_pipe(self, contents):
        """
        Writes a given message to the pipeline and saves what was written
        :param contents: The message to be written
        """
        with open(PIPE, "w") as file:
            file.write(contents)
        print(f"Wrote the following message to {PIPE}: {contents}")
        self.last_write = contents

    def choose_user(self):
        """
        Gets the user from the client
        """
        return self.send_and_wait_for_message(USER_SELECT)

    def choose_season(self):
        """
        Gets the user from the client
        """
        return self.send_and_wait_for_message(SEASON_SELECT)

    def choose_wins(self):
        """
        Gets the user from the client
        """
        return self.send_and_wait_for_message(WINS)

    def choose_losses(self):
        """
        Gets the user from the client
        """
        return self.send_and_wait_for_message(LOSSES)


if __name__ == '__main__':
    Microservice()