import discord
from datetime import datetime, timedelta
import heapq

# TODO: implement heapq and make the values negative for MaxHeap
# a dictionary storing all people on the leaderboard
# member id:person object
persons = {}


class Person:
    """
    Class made to keep track of members on a leaderboard
    """
    __anti_spam = timedelta(seconds=15)

    def __init__(self, message):
        global persons

        self.member = message.author.id
        self._score = -1
        self.last_time = message.created_at
        persons[message.author.id] = self

    def get_score(self):
        return self._score

    def score(self, message):
        if message.author.id != self.member:
            raise Exception("This message was not writen by this person.")
        if self.last_time + self.__anti_spam < message.created_at:
            self._score -= 1
            self.last_time = message.created_at

    def save_string(self):
        return str(self.member) + ',' + str(self._score) + '\n'

    def __str__(self):
        return str(self.member) + ',' + str(self.last_time)

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

    def set_member(self, member):
        self.member = member

    def set_score(self, score):
        self._score += score


class Leaderboard:
    def __init__(self, lst=[]):
        #stores the person objects and sorts them as a heap
        self.leaderboard = lst

    def score(self, message):
        if message.author.guild_permissions.change_nickname or message.channel.id == 764998372070916106 or message.channel.id == 808964881167679529:
            return
        if message.author.id not in persons:
            heapq.heappush(self.leaderboard, Person(message))
        else:
            persons[message.author.id].score(message)
            heapq.heapify(self.leaderboard)

    def get_leader(self):
        return self.leaderboard[0]

    async def show_leaderboard(self, message):
        embed = discord.Embed(title='Most Active Users')
        board = self.leaderboard.copy()
        x = 10
        if len(board) < x:
            x = len(board)
        for i in range(x):
            member = heapq.heappop(board)
            if member is not None:
                embed.add_field(name='@'+str(message.guild.get_member(member.member).display_name), value=member.get_score()*-1, inline=False)
        await message.channel.send(embed=embed)

    async def award_leaderboard(self, message):
        board = self.leaderboard.copy()
        x = 10
        if len(board) < x:
            x = len(board)
        for i in range(x):
            member = heapq.heappop(board)
            if member is not None:
                await member.add_roles(message.guild.get_role(833911100147761152))

    async def reset_leaderboard(self, message):
        global persons
        self.leaderboard = []
        persons = {}
        await message.channel.send('Leaderboard Reset')

    def save_leaderboard(self, message):
        #saved as id,score
        filename = str(message.guild.id) + '.leaderboard'
        with open(filename,'w') as file:
            for person in self.leaderboard:
                out = person.save_string()
                file.write(out)

    def load_leaderboard(self, message):
        print('loading leaderboard')
        filename = str(message.guild.id) + '.leaderboard'
        with open(filename) as file:
            lines = file.readlines()
            for line in lines:
                arg = line.split(',')
                try:
                    person = persons[int(arg[0])]
                except KeyError:
                    person = Person(message)
                persons[int(arg[0])] = person
                person.set_score(1)
                person.set_member(int(arg[0]))
                person.set_score(int(arg[1]))
                person.last_time = datetime.now()
                heapq.heappush(self.leaderboard, person)
