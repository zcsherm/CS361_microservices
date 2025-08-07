import pickle
import os
import Player from player_record

PIPE = "player_pipe.txt"
ADD_REQUEST = "ADD"
REMOVE_REQUEST = "REMOVE"
CREATE_REQUEST = "CREATE"
QUIT_REQUEST = "QUIT"
USER_SELECT = "USER"
REQUESTS = [ADD_REQUEST, REMOVE_REQUEST, REMOVE_REQUEST, QUIT_REQUEST]

REQUESTS = {ADD_REQUEST: }
PASSED_READ = "PLAYER"
WHICH_TEAM = "TEAM"
FAILED_READ = "INVALID"

NOT_FOUND = "404"
TIMED_OUT = "408"
FORBIDDEN = "403"
SUCCESS = "200"

PLAYER_DIRECTORY = "players"
MASTER_FILE = PLAYER_DIRECTORY + "/" + "master.pkl"
PLAYER_NAMES = "names.txt"

class Microservice:
    def __init__(self):
        self.requests = {
                        ADD_REQUEST: self.add_player,
                        REMOVE_REQUEST: self.remove_player,
                        CREATE_REQUEST: self.add_new_player_to_database,
                        QUIT_REQUEST: self.quit
                        }
        self.make_pipe()
        self.make_player_directory()
        self.open_master()
        self.last_write = None
        self.main()
        

    def main(self):
        while self.last_write != QUIT_REQUEST:
            time.sleep(1)
            with open(PIPE, "r") as file:
                content = file.read().upper()
            if content != '':
                self.route_request(content)
        
    def make_pipe(self):
        if not os.path.isfile(path):
            if not os.path.isfile(PIPE):
            with open(PIPE, 'w') as file:
                file.write('')
        
    def make_player_directory(self):
        if not os.path.isdir(PLAYER_DIRECTORY):
            os.mkdir(PLAYER_DIRECTORY)
            self.make_master_file()

    def make_master_file():
        player_names = []
        players = {}
        with open(PLAYER_NAMES,'r') as file:
            for line in file.read():
                player_names.append(line)
        count = 0
        for player in players:
            data = {"name": player,
                    "id": count,
                    "current_team": None
                   }
            players[player_names] = Player(data)
        with open(MASTER_FILE, 'wb') as file:
            pickle.dump(players, file)

    def open_master(self):
        with open(MASTER_FILE, 'rb') as file:
            self.players = pickle.load(file)

    def send_and_wait_for_message(self, sent_message, response_function):
        self.write_to_pipe(sent_message)
        count = 0
        while count < 20:
            time.sleep(.5)
            with open(PIPE, "r") as file:
                content = file.read()
            if content != '':
                response_function(content)
                
    def choose_user(self):
        self.send_and_wait_for_message(USER_SELECT,
    def add_player(self):
        
            
    
    def validate_player_exists(self, player):
        pass

    def validate_player_available(self):
        pass
        
    def validate_player_on_team(self):
        pass

    def remove_player(self):
        pass

    def add_new_player_to_database(self):
        pass

    def write_to_pipe(self, contents):
        """
        Writes a given message to the pipeline and saves what was written
        :param contents: The message to be written
        """
        with open(PIPE, "w") as file:
            file.write(contents)
        self.last_write = contents
        
    def route_request(self, content):
        try:
            self.requests[content]()
        except KeyError:
            self.invalid_request()

    def invalid_request(self):
        self.write_to_pipe(FAILED_READ)
