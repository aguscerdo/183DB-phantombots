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



class BaseLine:
    def __init__(self, env=None):
        if env is None:
            self.env = environment.Environment()
        else:
            self.env = env
    
    
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
        if not ok:
            raise ValueError("Failed to play round: {} -- {} -- {}".format(pursuer_moves, target_move1, target_move2))
        return pursuer_moves, target_move1, target_move2
    
    
    def baseline_moves(self):
        pursuer_moves = self.pursuer_move()
        target_move1, target_move2 = self.target_move()
        
        return pursuer_moves, target_move1, target_move2
    
    def run_baseline(self):
        i = 0
        while not self.env.win_condition():
            self.baseline_step()
            if i % 25 == 0:
                self.env.plot_grid()
            i += 1