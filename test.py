import unittest
import os
import time
import shutil
import microservice_a as a
import microservice_b as b
import microservice_d as d
import random

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

class TestMicroServiceA(unittest.TestCase):

    def test_file_request(self):
        shutil.copy('test.png', dst=os.getcwd() + '/' + a.IMAGE_DIRECTORY + '/' + 'test.png')
        write_to_pipe(a.PIPE, a.FETCH_REQUEST)
        count = 0
        while count < 20:
            time.sleep(.5)
            content = read_pipe(a.PIPE)
            if content != '' and content != a.FETCH_REQUEST:
                self.assertTrue(content, a.PASSED_READ)
                if content == a.PASSED_READ:
                    break
            count += 1
        if count >= 20:
            self.assertFalse(True)
        else:
            write_to_pipe(a.PIPE, 'test')
            count = 0
            while count < 20:
                time.sleep(.5)
                content = read_pipe(a.PIPE)
                if content != 'test' and content != '':
                    self.assertEqual(content, 'C:\\Users\\zashe\\PycharmProjects\\CS361_microservices\\card_image\\test.png'
)
                    return
        self.assertFalse(True)

    def test_something(self):
        self.assertTrue(os.path.isdir(a.IMAGE_DIRECTORY))
        self.assertTrue(os.path.isfile(a.PIPE))

class TestMicroB(unittest.TestCase):

    def test1_add_player(self):
        content = read_write_cycle(b.PIPE,b.ADD_REQUEST)
        self.assertEqual(content, b.USER_SELECT)
        content = read_write_cycle(b.PIPE, 'Test')
        self.assertEqual(content, b.WHICH_TEAM)
        content = read_write_cycle(b.PIPE, 'Team Test')
        self.assertEqual(content, b.WHICH_PLAYER)
        content = read_write_cycle(b.PIPE, 'jasper')
        self.assertEqual(content, b.SUCCESS)

    def test2_add_fails(self):
        content = read_write_cycle(b.PIPE,b.ADD_REQUEST)
        self.assertEqual(content, b.USER_SELECT)
        content = read_write_cycle(b.PIPE, 'Test')
        self.assertEqual(content, b.WHICH_TEAM)
        content = read_write_cycle(b.PIPE, 'Team Failure')
        self.assertEqual(content, b.WHICH_PLAYER)
        content = read_write_cycle(b.PIPE, 'jasper')
        self.assertEqual(content, b.FORBIDDEN)

    def test3_remove_passes(self):
        content = read_write_cycle(b.PIPE, b.ADD_REQUEST)
        self.assertEqual(content, b.USER_SELECT)
        content = read_write_cycle(b.PIPE, 'Test')
        self.assertEqual(content, b.WHICH_TEAM)
        content = read_write_cycle(b.PIPE, 'none')
        self.assertEqual(content, b.WHICH_PLAYER)
        content = read_write_cycle(b.PIPE, 'jasper')
        self.assertEqual(content, b.SUCCESS)

    def test4_new_player(self):
        content = read_write_cycle(b.PIPE, b.CREATE_REQUEST)
        self.assertEqual(content, b.USER_SELECT)
        content = read_write_cycle(b.PIPE, 'Test')
        self.assertEqual(content, b.WHICH_TEAM)
        content = read_write_cycle(b.PIPE, 'none')
        self.assertEqual(content, b.WHICH_PLAYER)
        content = read_write_cycle(b.PIPE, 'hulk')
        self.assertEqual(content, b.SUCCESS)

    def test5_new_player(self):
        content = read_write_cycle(b.PIPE, b.CREATE_REQUEST)
        self.assertEqual(content, b.USER_SELECT)
        content = read_write_cycle(b.PIPE, 'Test')
        self.assertEqual(content, b.WHICH_TEAM)
        content = read_write_cycle(b.PIPE, 'none')
        self.assertEqual(content, b.WHICH_PLAYER)
        content = read_write_cycle(b.PIPE, 'dog')
        self.assertEqual(content, b.FORBIDDEN)

    def test6_add_new_player(self):
        content = read_write_cycle(b.PIPE, b.ADD_REQUEST)
        self.assertEqual(content, b.USER_SELECT)
        content = read_write_cycle(b.PIPE, 'Test')
        self.assertEqual(content, b.WHICH_TEAM)
        content = read_write_cycle(b.PIPE, 'Team Test')
        self.assertEqual(content, b.WHICH_PLAYER)
        content = read_write_cycle(b.PIPE, 'hulk')
        self.assertEqual(content, b.SUCCESS)

    def test7_get_players(self):
        content = read_write_cycle(b.PIPE,b.GET_PLAYERS)
        content = read_write_cycle(b.PIPE, 'Test')
        content = read_write_cycle(b.PIPE, 'Test')
        content = read_write_cycle(b.PIPE, 'Test')
        print(content)

    def test99_close(self):
        os.remove(b.PLAYER_DIRECTORY + "/" + "Test.pkl")

class TestMicroD(unittest.TestCase):
    def test1_add_score(self):
        content = read_write_cycle(d.PIPE, d.ADD_REQUEST)
        self.assertEqual(content, d.USER_SELECT)
        content = read_write_cycle(d.PIPE, 'Test')
        self.assertEqual(content, d.SEASON_SELECT)
        content = read_write_cycle(d.PIPE, '2045')
        self.assertEqual(content, d.WINS)
        wins = random.randint(0,33)
        content = read_write_cycle(d.PIPE, str(wins))
        self.assertEqual(content, d.LOSSES)
        losses = 33-wins
        content = read_write_cycle(d.PIPE, str(losses))
        self.assertEqual(content, d.SUCCESS)

    def test2_view_score(self):
        content=read_write_cycle(d.PIPE,d.VIEW_REQUEST)
        self.assertEqual(content,d.SCORE_QUANT)
        content = read_write_cycle(d.PIPE,'3')
        print(content)

if __name__ == '__main__':
    print('hello')
    unittest.main()
    os.rmdir(a.IMAGE_DIRECTORY)
    os.remove(a.PIPE)