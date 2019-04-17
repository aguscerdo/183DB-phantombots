import matplotlib

class BS1:
    def __init__(self, env):
        self.env = env
    
    def evaderAlg(self, pos):
        while (self.env.win_condition is 0): #while game is not over
            adj = self.env.adjacent(pos)  #find all adjacent spots
            for spots in adj:       #determine actual legal spots from adjacent spots
                if self.env.legal_move_pos(pos, spots) is 0:
                    adj.remove(spots)
            listOfDistances = []    #list of list of distances
            for spot in adj:    #find distances from each bot to spot
                distances = []
                for bot in range(len(self.env.bots)-1):
                    distances.append(self.env.dist(spot,self.env.bots[bot].get_position()))
                listOfDistances.append((distances))
            minDistances = []
            for item in listOfDistances:
                minDistances.append(min(item))
            maxMin = 0
            for i in range(len(minDistances)):
                if minDistances[i] < minDistances[maxMin]:
                    maxMin = i
            return adj[maxMin]
    
    
    def pursuerAlg(self, pos):   #pass in list of initial position of pursuer bots
        pursuerMoves = []
        while (self.env.win_condition() == 0): #while game is not over
            for i in range(0, len(self.env.bots)-1):    #run for each pursuer
                adj = self.env.adjacent(pos[i])
                for spots in adj:
                    if self.env.legal_move_pos(pos[i], spots) == 0:
                        adj.remove(spots)   #remove spot if not valid
                distances = []
                for spot in adj:
                    distances.append((self.env.dist(spot, self.env.bots[-1].get_position()))) #find distance of spot to pacman
                min = 0
                for i in range(len(distances)):
                    if distances[i] < distances[min]:   #determine min distance
                        min = i
                pursuerMoves.append(adj[i])
                
            return pursuerMoves
