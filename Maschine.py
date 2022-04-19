 # -*- coding: utf-8 -*-

"""

@author: Lisa Kudlik
class Maschine
    Attribute:  number (individueller Key)
                konvexeHull (die Koordinaten der konvexen Hülle, d.h. die Fläche der Maschine)
                Mittelpunkt (Mittelpunkt der konvexeHull)
                zustaendigerMitarbeiter (Nummer des Mitarbeiters der für diese Maschine zuständig ist)
    
    Funktionen: get-Funktionen
                Mittelpunkt_bestimmen: Zur Bestimmung des Clustermittelpunkts
                Abstand: Berechnet den Abstand zweier Maschinenmittelpunkte

"""
import pandas as pd
import numpy as np
from math import dist


class Maschine:
    
    Nr = 0
    def __init__(self,x,y,Mitarbeiter): #Constructor
     
             self.number= Maschine.Nr #jedes Objekt hat eine automatisch generierte Number/Key
             Maschine.Nr +=1
             konvexeHull= pd.concat([x,y],axis=1).set_axis(['x', 'y'], axis='columns')
             self.konvexeHull=konvexeHull.dropna()
             self.Mittelpunkt= self.Mittelpunkt_bestimmen()
             self.zustaendigerMitarbeiter=Mitarbeiter
            

#===========================================
#get-Funktionen             
    def getnumber(self):
        return(self.number)
    
    def getMittelpunkt(self):
        return(self.Mittelpunkt)
    
    def getkonvexeHull(self):
        return(self.konvexeHull)
    
    def getMitarbeiter(self):
        return(self.zustaendigerMitarbeiter)
  
#==============================================
#Funktion zur Bestimmung des Mittelpunktes des Clusters    
    def Mittelpunkt_bestimmen(self):
        
        #konvexe Hülle hat x und y das muss mit beachtet werden
        meanx= (np.amax(self.konvexeHull['x'])+np.amin(self.konvexeHull['x']))/2
        meany= (np.amax(self.konvexeHull['y'])+np.amin(self.konvexeHull['y']))/2
        Mittelpunkt=[meanx,meany]
        return Mittelpunkt
    
#Abstand zwischen zwei Maschinen bestimmen (euklidischer Abstand) anhand der Mittelpunkte
#die Clustergröße spielt dabei keine Rolle 
    def Abstand(self,Maschine):
        Abstand =dist(self.Mittelpunkt,Maschine.getMittelpunkt())
        
        return Abstand
    
    

