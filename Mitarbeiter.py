# -*- coding: utf-8 -*-
"""

@author: Lisa Kudlik
class Mitarbeiter:
    Attribute:  Koordinaten (die Bewegungsdaten, die von den Sensoren aufgenommen wurden)
                MitarbeiterNr (übergebene Nummer, sollte aber immmer eindeutig sein)
                label (sind die Clusterzuordnungen der einzelnen Punkte von "Koordinaten")
                zeitlicher_Ablauf (Dataframe mit der Reihenfolge und der Aufenthalftsdauer in den verschiedenen Bereichen)
                Maschinenzuord (Vektor der die verschieden Stationen enthält, die der Mitarbeiter abgelaufen ist)

    Funktionen: alle get-Methoden
                label_bestimmen: Anwendung des DBSCAN auf  die Koordinaten und Erstellung eines Labels für jeden Punkt
                Zuordnen: Ordnet dem Mitarbeiter die globalen Maschinen zu an denen er arbeitet
                Maschinenaufenthaltszeit: gibt anhand lokaler Variablen den Ablauf der Stationen von einem Mitarbeiter wieder
                
"""
from sklearn.cluster import DBSCAN
from scipy.spatial import ConvexHull
from scipy.spatial import Delaunay

import Funktionen as fkt
import pandas as pd
import numpy as np


class Mitarbeiter:
 
   
 def __init__(self,Koordinaten,MitarbeiterNr): #Constructor
        
                self.Koordinaten=Koordinaten #Koordinaten
                self.MitarbeiterNr=MitarbeiterNr #Jeder Mitarbeiter hat eine Nummer die in identifiziert

                self.label = self.label_bestimmen(4) #enthaelt die Clusternummern bzgl. jeden einzelnen Punktes
                self.zeitlicher_Ablauf = pd.DataFrame() #Zeitliche Abfolge mit entsprechender Aufenthaltsdauer
                self.Maschinenzuord=[]#Liste mit den Maschinen die von diesem Mitarbeiter ausgeführt werden

#==============================================
#get-Funktionen für die Attribute 
 def getlabel(self):
      return(self.label)
 
 def getMitarbeiterNr(self):
     return(self.MitarbeiterNr)
 
 def getzeitlicher_Ablauf(self):
     return(self.zeitlicher_Ablauf)
 
# def getReihenfolge(self):
#     return(self.Reihenfolge)
 
 def getMaschinenzuord(self):
     
     return(self.Maschinenzuord)
 
#=====================================================
#create Funktion für Attribute
 def createzeitlicher_Ablauf(self,zukleineCluster):
    self.zeitlicher_Ablauf = self.Maschinenaufenthaltszeit(zukleineCluster)
   
#====================================================
 def Eps_bestimmen(self,k): # k: int Zahl, k=minPts, welches die Anzahl an Nachbarn in der eps-Nchbrschaft angibt

        if type(self.Koordinaten) is pd.DataFrame:
            self.Koordinaten = self.Koordinaten.values
        #k-dist Funktion
        dim0=self.Koordinaten.shape[0]
        #euklidische Norm berechnen
        p=-2*self.Koordinaten.dot(self.Koordinaten.T)+np.sum(self.Koordinaten**2, axis=1).T+ np.repeat(np.sum(self.Koordinaten**2, axis=1),dim0,axis=0).reshape(dim0,dim0)
        p = np.delete(p,range(0,p.shape[0]**2,(p.shape[0]+1))).reshape(p.shape[0],(p.shape[1]-1)) #löschen der diagonal Elemente, da jeder Punkt zu sich selbst genau den Abstand 0 hat
        if(np.all(p>0)): #nur Wurzelziehen falls keine negativen Werte enthalten
            
            p = np.sqrt(p)  #Wurzel bilden
        else:
            print("Error: negative value in root")
           
            
            
        p.sort(axis=1) #sortieren nach der Größe entlang jeder einzelnen Zeile
        k_dist=p[:,k] # nur die k-te Spalte betrachten, da dort der Abstand zum k-ten Nachbarn gespeichert ist
       
        #Berechnung des Quantils für die gegebene Menge , k-dist(X).
        eps =np.quantile(k_dist,0.85) #85% Quantil
        return eps



#Cluster-zuordnung für jeden einzelnen Punkt, Erstellung des Labels
# mit Hilfe der k-dist Funktion Eps bestimmen und danach den DBSCAN anwenden
 def label_bestimmen(self,k): #  k: int Zahl, k=minPts, welches die Anzahl an Nachbarn in der eps-Nchbrschaft angibt, meistens k=4

        #Eps bestimmen
        eps=self.Eps_bestimmen(k)
        #Epsilon einsetzen , MinPts = 4 
        #Anwenden des in der Bibiothek vorgegebenen DBSCAN
        dbscan=DBSCAN(eps=eps,min_samples=4).fit(self.Koordinaten)
        label = dbscan.labels_ #Vector mit den Clusternummer zu den oben eingegebenen Daten
        
        return label
  
#Zuordnung der Stationen die von diesem Mitarbeiter betätigt werden, unhabhängig von der Reihenfolge in der die Stationen besucht werden
#kann erst ausgeführt werden wenn alle Maschinen definiert sind, da sich dann die Stationen Nummern dann erst eindeutig werden
 def Zuordnen(self,alleMaschinen):
        Zuordnung=[]
     
        #die Stationen, die Nummern zuteilen, die global gelten, im Moment abhängig von jedem einzelnen Mitarbeiter           

        uniqueListe=np.unique(self.label) #Liste mit den lokalen Clusternummern
        for i in uniqueListe: 
         if i != -1:
            
            Liste=self.label.tolist() #beinhaltet alle verschiedenen Maschinen aber noch mit den lokalen Nummern
            temp=Liste.index(i)
            #immer nur einen Punkt von einem Cluster betrachten
            einPunkt=self.Koordinaten[temp] #repräsentant für das lokale Cluster, nun wird die dazugehörige globale Clusternummer gesucht
             
            for j in alleMaschinen : # itriert über Zahlen z.B. 1,2,3,...
                
                hull=alleMaschinen[j].getkonvexeHull().to_numpy() #einlesen der konvexen Hüllen der einzelnen Maschinen
                if not isinstance(hull,Delaunay):  
                    hull = Delaunay(hull)
                    Inside=hull.find_simplex(einPunkt)>=0 #True falls der Punkt innerhalb liegt
                
            
                if Inside == True:
                    
                    if(j not in Zuordnung):
                        Zuordnung.append(alleMaschinen[j].getnumber())
                                           
        self.Maschinenzuord=Zuordnung
        return Zuordnung
       
        
       
# Bestimmen der Dauer und der Abgelaufenen Stationen unter Verwendung der lokalen Clusternummern
 def Maschinenaufenthaltszeit(self,zukleineCluster): #zukleineCluster: Liste mit den Clusternr. die zu klein waren
    
    Aufenthaltsdauer=pd.DataFrame(columns=("Station","Dauer"))  
    temp=0
    dauer=1 #Dauer= Anzahl der Datenpunkte die innerhalb des Clusters liegen
    Aufenthaltsdauer.loc[0]=[self.label[0],1]
    
    #die Anzahl der Punkte, die chronologisch in einem Cluster liegen bevor dieses wieder verlassen wird, zusammenzählen
    for i in range(0,len(self.label)-1):  
        
            if self.label[i] in zukleineCluster: # falls das Label zu einem Cluster das vorher schon ausgeschlossen wurde gehört
                     self.label[i]=-1                # wird das Label auf -1 (Randpunkt)= Laufweg gesetzt
            if self.label[i+1] in zukleineCluster: # falls der nachfolgende Punkt auch in den zukleinen Cluster ist, das gleiche
                     self.label[i+1]=-1
            
            if self.label[i]==self.label[i+1]: #falls zwei aufeinanderfolgende Punkte im gleichen Cluster liegen wird die Dauer um eins erhöht
                 dauer=dauer+1     # das passiert solange bis das Cluster verlassen wird
           
            else: #Falls das Cluster verlassen wird steht die Dauer von dem Vorherigen Cluster fest  
                Aufenthaltsdauer["Dauer"][temp]=dauer
                Aufenthaltsdauer.loc[temp +1]=[self.label[i+1],1]
                dauer=0
                temp=temp+1
    
     #Alle, die zu klein sind löschen ( alle die eine Aufenthaltsdauer von 1 haben)
    #Es wird ausgegangen das dies Aufgrung von Ungenauigkeiten entsteht und deswegen werden solche Ausreißer gelöscht
    Indexname=Aufenthaltsdauer[Aufenthaltsdauer["Dauer"] <= 1].index
    Aufenthaltsdauer=Aufenthaltsdauer.drop(Indexname) #Index wieder anpassen
    Aufenthaltsdauer.index = range(len(Aufenthaltsdauer.index))
    
    
    j=1
    while j< len(Aufenthaltsdauer)-1 :
        
        if Aufenthaltsdauer["Station"][j]==Aufenthaltsdauer["Station"][j-1]:
            
               Aufenthaltsdauer["Dauer"][j-1]= Aufenthaltsdauer["Dauer"][j]+Aufenthaltsdauer["Dauer"][j-1]
               Aufenthaltsdauer=Aufenthaltsdauer.drop([j], axis=0)
               Aufenthaltsdauer.index = range(len(Aufenthaltsdauer.index))
               
        else:
            j=j+1
            
    return Aufenthaltsdauer       
      
     
    



