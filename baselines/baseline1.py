import numpy as np
import environment

class BaseLine1:
    def __init__(self, env=None, nbots=3):
        if env is None:
            self.env = environment.Environment(nbots=nbots)
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
        
        try:
            max_d = max_d[0]
        except IndexError:
            pass

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
                try:
                    max_d = max_d[0]
                except IndexError:
                    pass
                
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
                
                try:
                    min_d = min_d[0]
                except IndexError:
                    pass
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