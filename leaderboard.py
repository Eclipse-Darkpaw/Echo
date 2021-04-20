import discord
from datetime import datetime, timedelta
from maxHeap import MaxHeap

# a dictionary storing all people on the leaderboard
# member id:person object
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
        persons[message.author.id] = self

    def get_member(self):
        return self.member

    def get_score(self):
        return self._score

    def score(self, message):

        if message.author != self.member:
            raise Exception("This message was not writen by this person.")
        if self.last_time + self.__anti_spam < message.created_at:
            self._score += 1
            self.last_time = message.created_at

    '''
    def get_save_string(self):
        return '(' + str(self.member.id) + ',' + str(self._score) + ',' + str(self.last_time) + ')'
    '''

    def __str__(self):
        return str(self.member.id) + ',' + str(self.last_time)

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
    def __init__(self, lst=[]):
        #stores the person objects and sorts them as a heap
        self.leaderboard = MaxHeap(lst)

    def score(self, message):
        if message.author.guild_permissions.change_nickname or message.channel.id == 764998372070916106:
            return
        if message.author.id not in persons:
            self.leaderboard.insert(Person(message))
        else:
            persons[message.author.id].score(message)
            self.leaderboard.buildheap(self.leaderboard.heap)

    def get_leader(self):
        return self.leaderboard.getMax()

    async def show_leaderboard(self, message):
        embed = discord.Embed(title='Most Active Users')
        board = MaxHeap(self.leaderboard.heap.copy())
        x = 10
        if len(board) < x:
            x = len(board)
        for i in range(x):
            member = board.extractMax()
            if member is not None:
                embed.add_field(name='<@!'+str(member.member.display_name)+'>', value=member.get_score(), inline=False)
        await message.channel.send(embed=embed)

    async def award_leaderboard(self, message):
        board = MaxHeap(self.leaderboard.heap.copy())
        x = 10
        if len(board) < x:
            x = len(board)
        for i in range(x):
            member = board.extractMax()
            if member is not None:
                await member.add_roles(message.guild.get_role(833911100147761152))

    def reset_leaderboard(self, message):
        global persons
        self.leaderboard = MaxHeap()
        persons = {}


