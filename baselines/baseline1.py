import matplotlib
import numpy as np
import environment


# class BS1:
#     def __init__(self, env):
#         self.env = env
#
#     def evaderAlg(self, pos):
#         while (not self.env.win_condition()): #while game is not over
#             adj = self.env.adjacent(pos)  #find all adjacent spots
#             for spots in adj:       #determine actual legal spots from adjacent spots
#                 if self.env.legal_move_pos(pos, spots) is 0:
#                     adj.remove(spots)
#             listOfDistances = []    #list of list of distances
#             for spot in adj:    #find distances from each bot to spot
#                 distances = []
#                 for bot in range(len(self.env.bots)-1):
#                     distances.append(self.env.dist(spot,self.env.bots[bot].get_position()))
#                 listOfDistances.append((distances))
#             minDistances = []
#             for item in listOfDistances:
#                 minDistances.append(min(item))
#             maxMin = 0
#             for i in range(len(minDistances)):
#                 if minDistances[i] < minDistances[maxMin]:
#                     maxMin = i
#             return adj[maxMin]
#
#
#     def pursuerAlg(self, pos):   #pass in list of initial position of pursuer bots
#         pursuerMoves = []
#         while (not self.env.win_condition()): #while game is not over
#             for i in range(0, len(self.env.bots)-1):    #run for each pursuer
#                 adj = self.env.adjacent(pos[i])
#                 for spots in adj:
#                     if self.env.legal_move_pos(pos[i], spots) == 0:
#                         adj.remove(spots)   #remove spot if not valid
#                 distances = []
#                 for spot in adj:
#                     distances.append() #find distance of spot to pacman
#                 mmin = 0
#                 for j in range(len(distances)):
#                     if distances[j] < distances[mmin]:   #determine min distance
#                         mmin = j
#                 pursuerMoves.append(adj[mmin])
#
#             return pursuerMoves
#         return []


# def baseline_motion(self):
#     pursuer_pos = []
#     evader = self.bots[-1]
#     evader_pos = evader.get_position()
#     evader_second_move = None
#     # for i in range(0, len(self.bots)-1):
#     #     pursuer_pos.append(self.bots[i].get_position())
#     pursuer_moves = self.bs1.pursuerAlg(pursuer_pos)
#     evader_move = self.bs1.evaderAlg(evader_pos)
#     if evader.double_move():
#         evader_second_move = self.bs1.evaderAlg((evader.get_position()))
#     if self.play_round(pursuer_moves, evader_move, evader_second_move):
#         return True    #we moved!
#     print ("err!!")
#     return False



class BaseLine1:
    def __init__(self):
        self.env = environment.Environment()
    
    
    def target_move(self):
        move1, move2 = None, None
        
        target = self.env.bots[-1]
        pos = target.get_position()
        prev_pos = pos
        
        adj = [spot for spot in self.env.adjacent(pos) if self.env.legal_move_pos(pos, spot)]
        listOfDistances = []
        
        for spot in adj:
            perSpot = []
            for bot in range(len(self.env.bots) - 1):
                dists = self.env.dist(spot, self.env.bots[bot].get_position())
                perSpot.append(dists)
            listOfDistances.append(perSpot)
        
        minDistances = [min(item) for item in listOfDistances]
        max_d = np.argmax(minDistances)
        max_d = max_d if not isinstance(max_d, np.ndarray) else max_d[0]
        move1 = adj[max_d]
        if target.double_move():
            pos = move1
            listOfDistances = []
            adj = [spot for spot in self.env.adjacent(pos) if self.env.legal_move_pos(pos, spot)]

            for spot in adj:
                perSpot = []
                for bot in range(len(self.env.bots) - 1):
                    dists = self.env.dist(spot, self.env.bots[bot].get_position())
                    perSpot.append(dists)
                listOfDistances.append(perSpot)
    
            minDistances = [min(item) for item in listOfDistances]
            if len(minDistances) == 0:
                move2 = prev_pos # move back 
            else:
                max_d = np.argmax(minDistances)
                max_d = max_d if not isinstance(max_d, np.ndarray) else max_d[0]
                move2 = adj[max_d]
        return move1, move2
    
    
    def pursuer_move(self):
        moves = []
        for i in range(len(self.env.bots) - 1):
            pos = self.env.bots[i].get_position()
    
            adj = [spot for spot in self.env.adjacent(pos) if self.env.legal_move_pos(pos, spot)]
            if len(adj) == 0: # stay!
                moves.append(pos)
            else:
                d = [(self.env.dist(spot, self.env.bots[-1].get_position())) for spot in adj]
                min_d = np.argmin(d)
                min_d = min_d if isinstance(min_d, np.int64) else min_d[0]

                moves.append(adj[min_d])

        return moves


    def baseline_step(self):
        pursuer_moves = self.pursuer_move()
        target_move1, target_move2 = self.target_move()
        
        ok = self.env.play_round(pursuer_moves, target_move1, target_move2)
        # if not ok:
        #     raise ValueError("Failed to play round: {} -- {} -- {}".format(pursuer_moves, target_move1, target_move2))
        return pursuer_moves, target_move1, target_move2
    
    
    def baseline_moves(self):
        pursuer_moves = self.pursuer_move()
        target_move1, target_move2 = self.target_move()
        return pursuer_moves, target_move1, target_move2




class BaseLine2:
    def __init__(self):
        self.env = environment.Environment()

    def target_move(self):

        move1, move2 = None, None

        target = self.env.bots[-1]
        target_pos = target.get_position()
        target_adj = [target_spot for target_spot in self.env.adjacent(target_pos) if self.env.legal_move_pos(target_pos, target_spot)]
        if len(target_adj) == 0:
            move1 = target_pos
        else:
            pursuer_bots = self.env.bots[:-1]
            dist = [self.env.dist(target_pos, pursuer_bots[i].get_position()) for i in range(len(pursuer_bots))]
            min_pursuer_index = np.argmin(dist)
            min_pursuer_index = min_pursuer_index if isinstance(min_pursuer_index, np.int64) else min_pursuer_index[0]
            max_adjacent_dist = [self.env.dist(pursuer_bots[min_pursuer_index].get_position(), spot) for spot in target_adj]
            best_adjacent_spot = np.argmax(max_adjacent_dist)
            best_adjacent_spot = best_adjacent_spot if not isinstance(best_adjacent_spot, np.ndarray) else best_adjacent_spot[0]
            move1 = target_adj[best_adjacent_spot]
        if target.double_move():
            target_pos = move1
            target_adj = [spot for spot in self.env.adjacent(target_pos) if self.env.legal_move_pos(target_pos, spot)]
            if len(target_adj) == 0:
                move2 = target_pos
            else:
                pursuer_bots = self.env.bots[:-1]
                dist = [self.env.dist(target_pos, pursuer_bots[i].get_position()) for i in range(len(pursuer_bots))]
                min_pursuer_index = np.argmin(dist)
                min_pursuer_index = min_pursuer_index if isinstance(min_pursuer_index, np.int64) else min_pursuer_index[0]
                max_adjacent_dist = [self.env.dist(pursuer_bots[min_pursuer_index].get_position(), spot) for spot in target_adj]
                best_adjacent_spot = np.argmax(max_adjacent_dist)
                best_adjacent_spot = best_adjacent_spot if not isinstance(best_adjacent_spot, np.ndarray) else best_adjacent_spot[0]
                move2 = target_adj[best_adjacent_spot]

        return move1, move2
    
    
    def pursuer_move(self):

        moves = []
        target = self.env.bots[-1]
        target_pos = target.get_position()
        pursuer_bots = self.env.bots[:-1]
        target_adj = [target_spot for target_spot in self.env.adjacent(target_pos) if self.env.legal_move_pos(target_pos, target_spot)]
        bot_number_tasked = []
        bot_move_dict = {}

        for target_spot in target_adj:

            d1 = [(self.env.dist(pursuer_bots[i].get_position(), target_spot)) for i in [x for x in range(len(pursuer_bots)) if not bot_number_tasked.__contains__(x)]]  # type: List[Any] # type: List[Any]
            min_d1 = np.argmin(d1)
            min_d1 = min_d1 if isinstance(min_d1, np.int64) else min_d1[0]
            bot_number_tasked.append(min_d1)
            pursuer_pos = pursuer_bots[min_d1].get_position()
            pursuer_adj = [pursuer_spot for pursuer_spot in self.env.adjacent(pursuer_pos) if self.env.legal_move_pos(pursuer_pos, pursuer_spot)]
            if len(pursuer_adj) == 0: #stay
                bot_move_dict[min_d1] = pursuer_pos
            else:
                d2 = [(self.env.dist(pursuer_spot, target_spot)) for pursuer_spot in pursuer_adj]
                min_d2 = np.argmin(d2)
                min_d2 = min_d2 if isinstance(min_d2, np.int64) else min_d2[0]
                bot_move_dict[min_d1] = pursuer_adj[min_d2]

        if len(bot_number_tasked) != len(pursuer_bots):

            pursuer_bots_index = [i for i in range(len(pursuer_bots))]
            remaining_bots = list(set(pursuer_bots_index) - set(bot_number_tasked))

            for i in remaining_bots:
                pos = self.env.bots[i].get_position()
                adj = [spot for spot in self.env.adjacent(pos) if self.env.legal_move_pos(pos, spot)]
                if len(adj) == 0:  # stay!
                    bot_move_dict[i] = pos
                else:
                    d = [(self.env.dist(spot, self.env.bots[-1].get_position())) for spot in adj]
                    min_d = np.argmin(d)
                    min_d = min_d if isinstance(min_d, np.int64) else min_d[0]
                    bot_move_dict[i] = adj[min_d]

        for i in range(len(bot_move_dict)):
            moves.append(bot_move_dict[i])
        return moves

    def baseline_step(self):
        pursuer_moves = self.pursuer_move
        target_move1, target_move2 = self.target_move()

        ok = self.env.play_round(pursuer_moves, target_move1, target_move2)
        # if not ok:
        #     raise ValueError("Failed to play round: {} -- {} -- {}".format(pursuer_moves, target_move1, target_move2))
        return pursuer_moves, target_move1, target_move2

    def baseline_moves(self):
        pursuer_moves = self.pursuer_move
        target_move1, target_move2 = self.target_move()
        return pursuer_moves, target_move1, target_move2




class BaseLine3:
    def __init__(self):
        self.env = environment.Environment()

    def target_move(self):

        move1, move2 = None, None
        target = self.env.bots[-1]
        target_pos = target.get_position()
        target_adj = [target_spot for target_spot in self.env.adjacent(target_pos) if self.env.legal_move_pos(target_pos, target_spot)]
        rand_num = np.random.randint(1, 4)
        if rand_num <= 2:
            pursuer_bots = self.env.bots[:-1]
            if len(target_adj) == 0:
                move1 = target_pos
            else:
                dist = [self.env.dist(target_pos, pursuer_bots[i].get_position()) for i in range(len(pursuer_bots))]
                min_pursuer_index = np.argmin(dist)
                min_pursuer_index = min_pursuer_index if isinstance(min_pursuer_index, np.int64) else min_pursuer_index[0]
                max_adjacent_dist = [self.env.dist(pursuer_bots[min_pursuer_index].get_position(), spot) for spot in target_adj]
                best_adjacent_spot = np.argmax(max_adjacent_dist)
                best_adjacent_spot = best_adjacent_spot if not isinstance(best_adjacent_spot, np.ndarray) else best_adjacent_spot[0]
                move1 = target_adj[best_adjacent_spot]

        else:
            x = len(target_adj)
            rand_adj = np.random.randint(0, x)
            if len(target_adj) == 0:
                move1 = target_pos
            else:
                move1 = target_adj[rand_adj]

        if target.double_move():
            target_pos = move1
            target_adj = [target_spot for target_spot in self.env.adjacent(target_pos) if self.env.legal_move_pos(target_pos, target_spot)]
            x = len(target_adj)
            rand_adj = np.random.randint(0, x)
            if len(target_adj) == 0:
                move2 = target_pos
            else:
                move2 = target_adj[rand_adj]

        return move1, move2

    
    def pursuer_move(self):

        moves = []
        pursuer_bots = self.env.bots[:-1]
        target = self.env.bots[-1]
        target_pos = target.get_position()
        for i in range(len(pursuer_bots)):
            rand_num = np.random.randint(1, 4)
            pursuer_pos = pursuer_bots[i].get_position()
            pursuer_adj = [pursuer_spot for pursuer_spot in self.env.adjacent(pursuer_pos) if self.env.legal_move_pos(pursuer_pos, pursuer_spot)]
            if rand_num <= 1:
                if len(pursuer_adj) == 0:
                    moves.append(pursuer_pos)
                else:
                    dist = [self.env.dist(target_pos, spot) for spot in pursuer_adj]
                    min_dist = np.argmin(dist)
                    min_dist = min_dist if isinstance(min_dist, np.int64) else min_dist[0]
                    moves.append(pursuer_adj[min_dist])

            else:
                x = len(pursuer_adj)
                rand_adj = np.random.randint(0, x)
                if len(pursuer_adj) == 0:
                    moves.append(pursuer_pos)
                else:
                    moves.append(pursuer_adj[rand_adj])

        return moves

    def baseline_step(self):
        pursuer_moves = self.pursuer_move
        target_move1, target_move2 = self.target_move()

        ok = self.env.play_round(pursuer_moves, target_move1, target_move2)
        # if not ok:
        #     raise ValueError("Failed to play round: {} -- {} -- {}".format(pursuer_moves, target_move1, target_move2))
        return pursuer_moves, target_move1, target_move2

    def baseline_moves(self):
        pursuer_moves = self.pursuer_move
        target_move1, target_move2 = self.target_move()
        return pursuer_moves, target_move1, target_move2
