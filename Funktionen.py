# -*- coding: utf-8 -*-
"""

@author: Lisa Kudlik
Enthält die benötigten Funktionen
    -konvexe_Huelle : Berechnung der konvexen Hülle bezüglich der einzelnen Cluster, speichert diese pro Mitarbeiter/in in einem DataFrame
    -Standortplotten: Plotten aller konvexen Hüllen in einer Graphik, dient zur Visulaisierung der Maschinenstandorte
    -Materialfluss: Liste mit den Maschinennummer in der Reihenfolge in der das Teil die Stationen besucht hat
    -Greedy_Alg: gibt am Ende die neue Zuordnung der Anlagen zu den Standorten wieder, versucht das QZOP optimal zu lösen
    -neuesLayoutplotten: Plotten des neuen Layouts wobei die Mittelpunkte die selben sind
"""

import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull





def konvexe_Huelle(Daten,label): #Daten:x,y-Koordinaten als DataFrame, label: Vektor mit den Clusternr. für die Koordinaten
    zukleineCluster=[]
    Cluster_Nr=0   
    Cluster_Anzahl=np.amax(label) #erstes Cluster 0 bis max(Wert), wobei -1 die "Noise"-Punkte sind
   
    alle_konHull=pd.DataFrame()
    temp3=0
    
    #Iteration über alle Cluster 
    while temp3 <=Cluster_Anzahl:
            ganze_Cluster=pd.DataFrame(columns=('x','y')) 
            konHull=pd.DataFrame(columns=('x'+ str(Cluster_Nr),'y'+ str(Cluster_Nr)))#x,y-Koordinaten der Punkte auf der Konvexen Hülle
            n=0
            for i in range(len(Daten)): #iteration über alle Koordinaten-Daten
            #Falls das Label(Clusternummer) von einem Punkt dem gerade gesuchten Cluster entspricht,dann wird der Punkt zum Cluster hinzugefügt
            #Bildung eines DataFrame, wo alle Punkte die zu einem Cluster gehören enthalten sind 
            #von dieser Menge kann dann die konvexe Hülle bestimmt werden
            #davon nur die Punkte, die uf der Hülle liegen, zurück geben (alle_konHull)
                if(label[i]== temp3):
                        ganze_Cluster.loc[n]=[Daten['x'][i],Daten['z'][i]]
                        n=n+1
            
            #Konvexe Huelle bilden falls das Cluster mehr als x Punkte enthält, Vermeidung von kleinen 'falschen' Anhäufungen von Punkten
            l=int(len(Daten)*0.1) #mehr als 10% der Gesamtmenge aller Punkte
            if len(ganze_Cluster)>l: 
                    Index_of_point=ConvexHull(ganze_Cluster).vertices # Indizes von den Punkten, die die Hülle bilden
                    #Punkte der konvexen Hülle in einem DataFrame speichern
                    temp2=0
                    
                    for temp1 in Index_of_point:
                            #konHull beinhaltet alle Punkte aus dem Cluster, die die konvexe Hülle bilden
                            konHull.loc[temp2]=[ganze_Cluster['x'][temp1],ganze_Cluster['y'][temp1]]
                            temp2=temp2+1
                            
                    alle_konHull=pd.concat([alle_konHull,konHull],axis=1) #die neue konvexe Hülle zu den bereits bearbeiteten konvexen Hüllen hinzufügen
                    Cluster_Nr=Cluster_Nr+1
            
            else:
                zukleineCluster.append(temp3) 
                #Cluster Nummern von den Clustern, die zu klein waren und als Fehlerhaft gelten
                #die Punkte werden dann zu den Laufwegen(Cluster -1) hinzugezählt
                
                
            temp3=temp3+1
            
    return   alle_konHull, zukleineCluster


def Standortplotten(alleMaschinen): #alleMaschinen: Dictionary mit allen Maschinen
    #Erstellung einer graphischen Darstellung der Maschinenstandorte
    #die Standorte werden durch die Konvexen Hüllen repräsentiert

    for temp in alleMaschinen:

            M=alleMaschinen[temp].getkonvexeHull()
            M0=M.loc[0]
            M=M.append(M0)
            plt.plot(M['x'],M['y'])
            
            #Mittelpunkt plotten
            Mittelpunkt=alleMaschinen[temp].getMittelpunkt()
            plt.plot(Mittelpunkt[0],Mittelpunkt[1],'r.')
            plt.text(Mittelpunkt[0], Mittelpunkt[1], alleMaschinen[temp].getnumber(), horizontalalignment='left',verticalalignment='bottom')
     
        
    plt.title("Maschinenstandorte")  
    plt.xlabel('x-Achse in Meter')
    plt.ylabel('y-Achse in Meter')       
    plt.show()


def Materialfluss(Doc,Sensor_Nr,alleMaschinen): #Doc:Datei mit den Daten vom Server, Senosor_Nr: Nummer des Sensors von Produkt, alleMaschinen: Dic. mit allen Maschinen
    from scipy.spatial import Delaunay 
    
    #Koordinaten vom Produkt als DataFrame speichern, gleich wie bei den Daten von den Mitarbeitern 
    Koordinaten_Teil=pd.DataFrame()
    Materialfluss=[]
    j=0  
    for i in Doc['sensors'][Sensor_Nr]['positions']:
                Koordinaten_Teil = Koordinaten_Teil.append(Doc['sensors'][Sensor_Nr]['positions'][j],True) #x,y,z-Koordinaten 
                j=j+1
    Koordinaten_Teil=Koordinaten_Teil.drop(columns=['y']) # da y und z vertauscht sind, wird 'y' gelöscht nun hat man die x,y-Koordinaten
    Koordinaten_Teil['z']=-Koordinaten_Teil['z'] #da z invertiert ist   
    #Testen ob die Datei Daten enthält oder ob der Sensor "nur aktiv rumliegt"  
    T_empty=Koordinaten_Teil.empty
    if T_empty == True: #False falls die Datei Koordinaten enthält
        print("Keine Daten für den Materialfluss gefunden")
    else:
    
        #Bestimmung in welchem Cluster der Punkt liegt
        #so kann die Reihenfolge der besuchten Cluster des Produkts erkannt werden
        Koord_np=Koordinaten_Teil.to_numpy()
        for j in range(len(Koordinaten_Teil)):
            Punkt=Koord_np[j]
            Inside=False #True falls das Produkt innerhalb eines Clusters liegt
            
            for i in alleMaschinen : # itriert über Zahlen z.B. 1,2,3,...
             
             if(Inside==False):
               
                hull=alleMaschinen[i].getkonvexeHull().to_numpy() #einlesen der konvexen Hüllen derMaschine i
                if not isinstance(hull,Delaunay):  
                    hull = Delaunay(hull)
                    Inside=hull.find_simplex(Punkt)>=0 #True falls der Punkt innerhalb liegt vom Cluster i liegt
                
                if (Inside==True): #Punkt liegt in noch nicht vom Produkt besuchten Cluster
                    if(i not in Materialfluss):
                        Materialfluss.append(i)#Clusternr. der Ausgabe hinzufügen
                        
        
        #Testen ob alle Stationen von 1 bis n vorkommen, falls nicht soll die nicht erkannte Anlage am Ende hinzugefügt werden
        for i in alleMaschinen:
            if (i not in Materialfluss):
                Materialfluss.append(i)
        print(Materialfluss)
        
    return(Materialfluss)
               

def Greedy_Alg(flow_list,distance_list,n): #flow_list:Liste mit tripeln (repräsentiert die Flowmatrix) , distance_list: Liste mit tripeln (repräsentiert die Distanzmatrix)
                                            # n = Anzahl an Standorten/Maschinen
    
    solution=pd.DataFrame(index=range(0,n),columns=("Standort", "Anlage"))
    #sortieren der Listen, eine von größten zu kleinsten und die andere genau andersrum(klein zu groß)
    flow_list.sort(reverse=True)
    distance_list.sort()
    #merken welche Statioen und Standorte schon vergeben sind
    unused_locations = list(range(0,n))
    unused_Anlage= list(range(0,n))
    tempA=0
    tempL=0
    while len(unused_locations) > 0:
        
            hflow = flow_list[tempA] #höchstes noch nicht genutzte Flow-tupel
            ldist = distance_list[tempL]#niedrigste noch nicht genutzte Distanz-tupel
            #if Abfrage ob der eine Standort schon vergeben ist oder die Maschine schon zugeordnet wurde
            """
            Algorithmus baut auf dem Pseudo Code Simple Greedy Algorithmus auf
            Es wird immer die Standort Verfügbarkeit zu erst geprüft, somit wird nicht zwangsläufig die optimalste Lösung gefunden
            bei den Standorten wird auch zuerst ldist[1] geprüft und abhängig davon weiter entschieden, ist aber nicht relevant,
            da die Distanzmatrix symetrisch ist
            Fallunterscheidungen:
                1 Fall: beide Standorte sind frei und beide Anlagen sind noch nicht belegt
                2 Fall: nur ein Standort ist schon belegt(ldist[2] belegt oder ldist[1]) und eine der Anlagen ist frei
                3 Fall: beide Standorte sind schon belegt, dann wird sich das nächste Paar betrachtet
            """
            if((ldist[1] in unused_locations)):
                if ((ldist[2] in unused_locations)):
                    
                    if((hflow[1] in unused_Anlage) and (hflow[2] in unused_Anlage)):  
    
                        #Standorte und Anlagen einander zuordnen
                        #dabei ist der kleinste noch mögliche Anstand zwischen ldist[1] und ldist[2] 
                        #der maximal mögliste Flow ist zwischen hflow[1] und hflow[2] 
                        #somit wird  hflow[1] ldist[1] zugeordnet und  hflow[2] ldist[2]
                        solution["Anlage"][ldist[1]] = hflow[1]
                        solution["Anlage"][ldist[2]] = hflow[2]
                        solution["Standort"][ldist[1]] = ldist[1]
                        solution["Standort"][ldist[2]] = ldist[2]
                        #die vergebenen Anlagen, Standorte aus den Listen entfernen
                        unused_Anlage.remove(hflow[1])
                        unused_Anlage.remove(hflow[2])
                        unused_locations.remove(ldist[1]) 
                        unused_locations.remove(ldist[2])   
                        tempA=tempA+1
                

                else: #ldist[2] ist schon belegt
  
                    if(hflow[1] in unused_Anlage):
                        solution["Anlage"][ldist[1]] = hflow[1]
                        solution["Standort"][ldist[1]] = ldist[1]
                        unused_Anlage.remove(hflow[1])
                        unused_locations.remove(ldist[1])
                        
                        
                    elif(hflow[2] in unused_Anlage):
                            solution["Anlage"][ldist[1]] = hflow[2]
                            solution["Standort"][ldist[1]] = ldist[1]
                            unused_Anlage.remove(hflow[2])
                            unused_locations.remove(ldist[1])
                            
                    tempA=tempA+1
                    
                    
            else: #ldist[1] ist schon belegt
                if ((ldist[2] in unused_locations)):
            
                    if(hflow[1] in unused_Anlage):
                        solution["Anlage"][ldist[2]] = hflow[1]
                        solution["Standort"][ldist[2]] = ldist[2]
                        unused_Anlage.remove(hflow[1])
                        unused_locations.remove(ldist[2])
                        
                        
                    elif(hflow[2] in unused_Anlage):
                            solution["Anlage"][ldist[2]] = hflow[2]
                            solution["Standort"][ldist[2]] = ldist[2]
                            unused_Anlage.remove(hflow[2])
                            unused_locations.remove(ldist[2])
                            
                    tempA=tempA+1
                    

            tempL=tempL+1
    return solution
                    

def neuesLayoutplotten(alleMaschinen,Solution,Lam, Materialfluss): #alleMaschinen: dictionary mit allen Maschinen
                                                    #Solution: DataFrame mit den neuen Zuordnungen von den Mschinen zu ihren Standorten
                                                    #Lam:Lambda für die Bildüberschrift
    #Erstellung einer graphischen Darstellung der Maschinenstandorte
    #die Standorte werden durch die Konvexen Hüllen repräsentiert
    
    #Standorte in der Reihenfolge wie der Materialfluss
    j=0
    Mfluss=pd.DataFrame(columns=("x","y"),index=(range(0,len(alleMaschinen))))
    for i in Materialfluss:
        Anlageliste=Solution["Anlage"].tolist()
        temp0=Anlageliste.index(i)
        temp=Solution["Standort"][temp0]
        Fluss=alleMaschinen[temp].getMittelpunkt()
        Mfluss["x"][j]=Fluss[0]
        Mfluss["y"][j]=Fluss[1]
        j=j+1
    
    
    for temp in alleMaschinen:
        
            Standort_Liste= Solution["Standort"].tolist()
            temp2=Standort_Liste.index(temp) #temp Standort Nummer
            temp3=Solution["Anlage"][temp2] #Anlagen Nummer
            Mittelpunkt2=alleMaschinen[temp].getMittelpunkt()
            Mittelpunkt=alleMaschinen[temp3].getMittelpunkt()
            Abstandx=Mittelpunkt2[0]-Mittelpunkt[0]
            Abstandy=Mittelpunkt2[1]-Mittelpunkt[1]
            M=alleMaschinen[temp3].getkonvexeHull()
            M0=M.loc[0]
            M=M.append(M0)
            plt.plot(M['x']+Abstandx,M['y']+Abstandy)
            

          
            #Mittelpunkt plotten
            plt.plot(Mittelpunkt[0],Mittelpunkt[1],'r.')
            plt.text(Mittelpunkt2[0], Mittelpunkt2[1], temp3, horizontalalignment='left',verticalalignment='bottom')
     
    plt.plot(Mfluss['x'],Mfluss['y'], 'g' , label ='Produktfluss') 
    plt.title("Layout: λ = " + str(Lam)) 
    plt.legend(loc ="lower right")
    plt.xlabel('x-Achse in Meter')
    plt.ylabel('y-Achse in Meter')          
    plt.show()      
        





                
                