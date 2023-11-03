from random import uniform

def kdist(p1, p2):
    [x1,y1,z1] = p1
    [x2,y2,z2] = p2    
    return (((x2-x1)**2)+((y2-y1)**2)+((z2-z1)**2))**(1/2)     


class KMeans(object):
    def __init__(self, _points, _numCentroids):
        self.particles = []
        self.centroids = []
        self.centroidFinalPositions = []
        self.clusters = []
        
        self.numberOfCentroids = _numCentroids
        self.minX = 0.0
        self.maxX = 0.0
        self.minY = 0.0
        self.maxY = 0.0
        self.minZ = 0.0
        self.maxZ = 0.0
        self.totalStability = 0.0
        self.stableThreshold = 0.0001
        self.ready = False
        
        for p in _points:
            if (p[0] < self.minX):
                self.minX = p[0]
            if (p[0] > self.maxX):
                self.maxX = p[0]
            if (p[1] < self.minY):
                self.minY = p[1]
            if (p[1] > self.maxY):
                self.maxY = p[1]
            if (p[2] < self.minZ):
                self.minZ = p[2]
            if (p[2] > self.maxZ):
                self.maxZ = p[2]
            self.particles.append(KParticle(p))
        
        self.init()
    
    def init(self):    
        self.ready = False
        self.centroids.clear()
        self.clusters.clear()
    
        for i in range(0, self.numberOfCentroids):
            c = KCentroid(i, 127+uniform(0,127), 127+uniform(0,127), 127+uniform(0,127), self.minX, self.maxX, self.minY, self.maxY, self.minZ, self.maxZ)
            self.centroids.append(c)
        
    def update(self):
        for particle in self.particles: 
            particle.findClosestCentroid(self.centroids)
        
        self.totalStability = 0
        
        for centroid in self.centroids:
            centroid.update(self.particles)
            if (centroid.stability > 0):
                self.totalStability += centroid.stability
        
        if (self.totalStability < self.stableThreshold):
            for centroid in self.centroids:
                p = centroid.position # PVector
                self.clusters.append(KCluster(p))
                self.centroidFinalPositions.append(p)
            
            for particle in self.particles:
                self.clusters[particle.centroidIndex].points.append(particle.position)
            
            self.ready = True
        
    def run(self):
        if (self.ready == False):
            self.update()
 

class KCentroid(object):
    def __init__(self, _internalIndex, _r, _g, _b, _minX, _maxX, _minY, _maxY, _minZ, _maxZ):
        self.position = (uniform(_minX, _maxX), uniform(_minY, _maxY), uniform(_minZ, _maxZ))
        self.colorR = _r
        self.colorG = _g
        self.colorB = _b
        self.internalIndex = _internalIndex
        self.stability = -1.0

    def update(self, _particles):
        # Move the centroid to its position.
        newPosition = (0.0, 0.0, 0.0)

        numberOfAssociatedParticles = 0

        for curParticle in _particles:
            if (curParticle.centroidIndex == self.internalIndex):
                x = newPosition[0] + curParticle.position[0]
                y = newPosition[1] + curParticle.position[1]
                z = newPosition[2] + curParticle.position[2]
                newPosition = (x, y, z)
                numberOfAssociatedParticles += 1

        if (numberOfAssociatedParticles < 1):
            numberOfAssociatedParticles = 1

        newPosition = (newPosition[0] / numberOfAssociatedParticles, newPosition[1] / numberOfAssociatedParticles, newPosition[2] / numberOfAssociatedParticles)
        self.stability = kdist(self.position, newPosition)
        self.position = newPosition


class KParticle(object):
    def __init__(self, _position): # PVector
        self.position = _position # PVector
        self.velocity = (0.0,0.0,0.0) # PVector
        self.centroidIndex = 0 # int
        self.colorR = 0.0
        self.colorG = 0.0
        self.colorB = 0.0
        self.brightness = 0.8
    
    def findClosestCentroid(self, _centroids):
        closestCentroidIndex = 0
        closestDistance = 100000.0

        # Find which centroid is the closest.
        for i in range(0, len(_centroids)):             
            curCentroid = _centroids[i]

            distanceCheck = kdist(self.position, curCentroid.position)

            if (distanceCheck < closestDistance):
                closestCentroidIndex = i
                closestDistance = distanceCheck

        # Now that we have the closest centroid chosen, assign the index...
        self.centroidIndex = closestCentroidIndex

        # ...and get the color for visualization.        
        curCentroid = _centroids[self.centroidIndex]
        self.colorR = curCentroid.colorR * self.brightness
        self.colorG = curCentroid.colorG * self.brightness
        self.colorB = curCentroid.colorB * self.brightness
    

class KCluster(object):
    def __init__(self, _centroid): 
        self.centroid = _centroid
        self.points = []
