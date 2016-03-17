#!/usr/bin/python
# -*- coding: UTF-8 -*-

import random,sys,cPickle,time
from datetime import datetime
#from multiprocessing import Pool

random.seed(datetime.now())

groupunits = 100
playtimes = 100

rnd = random.randint
X = 1
O = 2

class Cell:        
    def __init__(self):        
        self.weight = [0] * 9
    def variation(self):
        for idx,v in enumerate(self.weight):
            if rnd(0,4) == 0:
                if rnd(0,1) == 1:
                    self.weight[idx] += 0.1
                else:
                    self.weight[idx] -= 0.1
      
class Round:
    def __init__(self):
        self.board = [0] * 9
        
class Unit:
    def __init__(self, init = True):
        self.cellnet = []
        if init:
            for i in xrange(9):
                newc = Cell()            
                newc.variation()
                self.cellnet.append(newc)
        self.score = 0

class Group:
    def __init__(self):
        self.units = []
        for i in xrange(groupunits):
            self.units += [Unit()]
        
def calcValue(c, r):
    return reduce(lambda x,y:x+y, map(lambda x,y:x*y, c.weight, r.board))

def mating(c1, c2):
    newC = Cell()
    newC.weight = c1.weight[0:5] + c2.weight[5:9]
    newC.variation()
    return newC

def hybrid(u1, u2):
    u1.score = u1.score / 4
    u2.score = u2.score / 4
    newU = Unit(False)
    newU.cellnet = map(lambda x,y:mating(x,y), u1.cellnet, u2.cellnet)
    return newU

def check3(board, p1, p2, t):
    return board[p1] == board[p2] and board[p2] == t
        

wintable = {}
wintable[0] = ((1,2), (3,6), (4,8))
wintable[1] = ((0,2), (4,7))
wintable[2] = ((0,1), (5,8), (4,6))
wintable[3] = ((0,6), (4,5))
wintable[4] = ((1,7), (3,5), (0,8), (2,6))
wintable[5] = ((2,8), (3,4))
wintable[6] = ((0,3), (2,4), (7,8))
wintable[7] = ((1,4), (6,8))
wintable[8] = ((2,5), (6,7), (0,4))

def checkwin(b, pos, t):
    #print 'cur:', pos
    checks = wintable[pos]
    for pair in checks:
        if check3(b, pair[0], pair[1], t):
            return True
    return False                                                        

def printBoard(board):
    def R(o):
        return repr(o).replace('2', 'X').replace('1', 'O').replace('0', '_').replace(',', ' ').replace('(', '|').replace(')', '|')
    print(R((board[0], board[1], board[2])) + ' 0 1 2')
    print(R((board[3], board[4], board[5])) + ' 3 4 5')
    print(R((board[6], board[7], board[8])) + ' 6 7 8')
    print('-'*19)

def XTurn(empty, board):
    if not empty:
        return -1
    ep = rnd(0, len(empty) - 1)
    pos = empty.pop(ep)
    board[pos] = X
    return pos

def maxout(empty, r, u):
    pos = -1
    e_i = -1
    maxv = -999
    for i,p in enumerate(empty):
        c = u.cellnet[p]
        v = calcValue(c, r)
        if v > maxv:
            maxv = v
            pos = p
            e_i = i
    return pos, e_i

def OTurn(empty, r, u, display = False):
    if not empty:
        return -1
    pos, e_i = maxout(empty, r, u)
    r.board[pos] = O
    empty.pop(e_i)
    if display:
        printBoard(r.board)
    return pos

def ManTurn(empty, board):
    #print('your turn')
    if not empty:
        return -1

    while True:
        try:
            pos = int(raw_input("input:"))
            empty.remove(pos)
            break
        except KeyboardInterrupt:
            print('bye bye')
            quit()
        except BaseException, e:
            print('error input')
            pass
    board[pos] = X
    printBoard(board)
    return pos
            
def play(u):
    r = Round()
    #printBoard(r.board)
    empty = [0,1,2,3,4,5,6,7,8]
    if rnd(0,1) == 0:
        XTurn(empty, r.board)
     
    while True:
        pos = OTurn(empty, r, u)
        if pos == -1:
            u.score += 1
            break
        if checkwin(r.board, pos, O):
            u.score += 2
            break
        pos = XTurn(empty, r.board)
        if pos == -1:
            u.score += 1
            break
        if checkwin(r.board, pos, X):
            u.score -= 10
            break
            
def evolution(g):
    for u in g.units:
        for i in xrange(playtimes):
            play(u)

def pve(u):
    print('\n---=== START ===---')
    r = Round()
    printBoard(r.board)
    empty = [0,1,2,3,4,5,6,7,8]
    if rnd(0,1) == 0:
        OTurn(empty, r, u, True)
     
    while True:
        pos = ManTurn(empty, r.board)
        if pos == -1:
            print('DRAW')
            time.sleep(2)
            break
        if checkwin(r.board, pos, X):
            print('YOU WIN   ' * 3)
            time.sleep(2)
            break
        pos = OTurn(empty, r, u, True)
        if pos == -1:
            print('DRAW')
            time.sleep(3)
            break
        if checkwin(r.board, pos, O):
            print('YOU LOSE   ' * 3)
            time.sleep(2)
            break

def train():
    epoch = int(raw_input('epoch:'))
    print('-'*20)
    g = Group()
    for E in xrange(epoch):
        evolution(g)
        g.units = sorted(g.units, key = lambda x:x.score, reverse=True)
        count = int(len(g.units)/2)
        g.units = g.units[0:count]
        score_sum = 0
        for u in g.units:
            score_sum += u.score        
        babies = []
        for i in xrange(count/2):
            babies.append(hybrid(g.units[i], g.units[count-1-i]))
            babies.append(hybrid(g.units[i], g.units[count-1-i]))
        g.units += babies
        sys.stdout.write(' ' * 40 + '\r')
        sys.stdout.write('[%d%%] Epoch:%d Score: %d\r' % (E*100/epoch, E, score_sum))
    fname = 'save_%d' % epoch
    fd = open(fname, 'wb+')
    cPickle.dump(g.units[0], fd)
    fd.close()
    print('train result file: %s saved' % fname)

def playpve():
    try:
        fname = raw_input('filename:')            
        fd = open(fname)
        u = cPickle.load(fd)
        fd.close()
    except:
        print('input error. Exit')
        quit()
    while True:
        pve(u)

def menu():    
    while True:
        r = raw_input('[1] Train\n[2] Play\n[3] Exit\n')
        if r == '1':
            train()
        elif r == '2':
            playpve()
        elif r == '3':
            quit()
        
if __name__ == '__main__':
    menu()