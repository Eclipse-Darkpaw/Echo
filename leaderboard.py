from discord import Embed
from datetime import datetime, timedelta

persons = {}


class Person:
    """
    Class made to keep track of members on a leaderboard
    """
    __anti_spam = timedelta(seconds=15)

    # (member, score, last message time)
    def __init__(self, message):
        global persons

        self.member = message.author
        self._score = 1
        self.last_time = message.created_at
        persons[member.id] = self

    def get_member(self):
        return self.member

    def get_score(self):
        return self._score

    def score(self, message):
        if message.author != self.member:
            raise Exception("This message was not writen by this person.")
        if self.last_time + anti_spam < message.created_at:
            self._score += 1
            self.last_time = message.created_at

    '''
    def get_save_string(self):
        return '(' + str(self.member.id) + ',' + str(self._score) + ',' + str(self.last_time) + ')'
    '''

    def __str__(self):
        return str(self.member.id + ',' + self.last_time)

    def __lt__(self, other):
        return self._score < other.get_score()

    def __le__(self, other):
        return self._score <= other.get_score()

    def __eq__(self, other):
        return self._score == other.get_score()

    def __ne__(self, other):
        return self._score != other.get_score()

    def __gt__(self, other):
        return self._score > other.get_score()

    def __ge__(self, other):
        return self._score >= other.get_score()


class Leaderboard:
    def __init__(self):
        self.persons
        self.leaderboard = []
        # assuming theres not a previous leaderboard

    def add_score(self, member, message):
        if member.id not in self.persons:
            self.persons[member.id] = Person(member, message.created_at)
        else:
            self.persons[member.id].score()

    def score(self, message):
        if message.author.id not in persons:
            self.persons =


    def get_leader(self):
        return self.leaderboard[0]

    def top_ten(self):
        pass

    def show_leaderboard(self):
        embed = Embed(title='Most Active Users')
