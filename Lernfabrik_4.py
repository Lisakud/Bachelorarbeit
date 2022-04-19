# -*- coding: utf-8 -*-
"""
@ author: Lisa Kudlik
Das Programm hat 2 große Teile, die aufeinander ausbauen
1. Teil:    Einlesen der Daten und Bestimmung der Maschinenstandorte
            bildliche Wiedergabe der Standote durch konvexe Hüllen
2.Teil:     Bestimmung eines optimierten Layouts unter Beachtung der Laufwege der Mitarbeiter und des Teilchenflusses
            Verwendung des Simple Greedy Algorithmus 

"""
import requests
import json
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



import Funktionen as fkt
import Mitarbeiter as Mi
import Maschine as Ma
   
#========================================================================
"""
Teil 1: Einlesen und Aufbereiten der Daten
        Erstellung der Objekte Mitarbeiter für jeden Mitarbeiter, der bei der Aufnahme tätig war
        Erstellung der Objekte Maschine für jede Maschine, die genutzt wurde
        Bildliche Wiedergabe der Anordnung der Maschinen mit Hilfe konvexer Hüllen
    
"""

#globale Variablen
Anzahlarbeiter=0

List_of_Workers=[]
Mittelpunkte=[]
dic_Maschine = {}

#Aufrufen der zu testenden Daten 
r = requests.get('http://129.13.234.138:3000/sessions/bd050d04-383a-4990-b5f9-8f2d5aa9a8bf') #Fall1
#r = requests.get('http://129.13.234.138:3000/sessions/b1209f27-0627-4442-ac10-087c35ea9666')#Fall2
#r = requests.get('http://129.13.234.138:3000/sessions/de686d7e-bbc3-46c6-8445-bb4eaf927453')#Fall3

Doc = r.json()

#Datei aufrufen und Array aus x und y erstelle
#Normalerweise iteration range(0,len(Doc["sensors"])), jedoch bei den drei Fällen nicht möglich
for N in [1,8,10,12,13] : #Fall3   # [1,8,10,12,13] für Fall1 und Fall2
    
      Koordinaten1=pd.DataFrame()
      j=0  
      for i in Doc['sensors'][N]['positions']:
                Koordinaten1 = Koordinaten1.append(Doc['sensors'][N]['positions'][j],True) #x,y,z-Koordinaten 
                j=j+1
       
      #Testen ob die Datei Daten enthält oder ob der Sensor "nur aktiv rumliegt"  
      T_empty=Koordinaten1.empty
      if T_empty == False: #False falls die Datei Koordinaten enthält
      
            Anzahlarbeiter=Anzahlarbeiter+1  #jeder ativ genutzte Sensor spiegelt einen Mitarbeiter wieder
            xyKoord1=Koordinaten1.drop(columns=['y']) # da y und z vertauscht sind, wird 'y' gelöscht nun hat man die x,y-Koordinaten
            xyKoord1['z']=-xyKoord1['z'] #da z invertiert ist
          
#Erstellen von Arbeitern der Klasse Mitarbeiter 
            Arbeiter=Mi.Mitarbeiter(xyKoord1,Anzahlarbeiter)
            List_of_Workers.append(Arbeiter) #hinzufügen zu der Liste aller Mitarbeiter
            labels=Arbeiter.getlabel()+0 # +0 damit in der Graphik, die irrelevanten Cluster auch angezeigt werden

            
            #Bilden der konvexen Hülle pro Cluster pro Mitarbeiter    
            Maschinenstandort, zukleineCluster=fkt.konvexe_Huelle(xyKoord1, labels)
            
            #Aufenthaltsdauern der Mitarbeiter an den einzelnen Stationen bestimmen
            
            Arbeiter.createzeitlicher_Ablauf(zukleineCluster)
            
            
            
#Erstellung der Maschinen mit Hilfe der Klasse Maschinen, welche danach in einem Dictornay abgespeichert werden
            i=0
            while i < Maschinenstandort.shape[1]/2:
        
                    M=Ma.Maschine(Maschinenstandort["x"+str(i)],Maschinenstandort["y"+str(i)],Anzahlarbeiter)
                    dic_Maschine[M.getnumber()] = M
                    Mittelpunkte.append(M.getMittelpunkt())  # Mittelpunkte in Liste speichern für die Ausgabe
                    i=i+1
              
                    
              
              
# Ausgabe der Mittelpunkte als Excel                    
            Mittelpunkte_excel=pd.DataFrame(Mittelpunkte,columns=("x","y"))
            Mittelpunkte_excel.to_excel(r'C:\Users\Beste\Documents\Python\Bachelorarbeit\Cluster_Mittelpunkte.xlsx', index=False)    
        
                        
        
        #Plotten der konvexen Hüllen um die Punkte
            i=0
            while i < Maschinenstandort.shape[1]/2 :
                
                plt.plot(Maschinenstandort['x'+ str(i)],Maschinenstandort['y'+ str(i)])
                i=i+1
            
            #plotten der xyKoordinaten,dabei werden alle Mitarbeiter ins gleiche Diagramm übertragen
            plt.scatter(xyKoord1['x'],xyKoord1['z'], c=labels)
            plt.title("Mitarbeiter:in " + str(Anzahlarbeiter))
            plt.xlabel('x-Achse in Meter')
            plt.ylabel('y-Achse in Meter') 
            plt.show() 


#Plotten aller konvexen Hüllen in einer Graphik
fkt.Standortplotten(dic_Maschine)

#=============================================================================================
#%%
"""Teil 2: Bestimmung des optimalen Layouts
    Bestimmung des Materialflusses
    Bestimmung des QZOP, Erstellung der Flow und Distanz Matrix
    Berechnung der QZOP, mit Hilfe der Heuristik Simple Greedy
    Bildliche Wiedergabe
#Koordinaten des Teils einlesen, in fast allen Aufnahmen war das Teil der 10-te Sensor
"""
#Daten einlesen und den Bewegungsfluss des Teilchen bestimmen
Sensor_Nr=9
Materialfluss=fkt.Materialfluss(Doc,Sensor_Nr,dic_Maschine)


#Erstellen der Flow und Distanz Matrix
flow_list=[]
distance_list=[]

#Lambda gibt die Gewichtung an, wie weit der Produktfluss oder wie weit der Mitarbeiterweg beachtet werden soll
#Dabei ergeben beide Gewichtungen zusammen jeweils 1, Teilchenfluss: Lambda , Mitarbeiterzugehörigkeit: 1-Lambda
print("Please insert a Lambda between 0 and 1:")
Lambda = float(input())
Lambda1= 1-Lambda

n=len(dic_Maschine)
#Spaltenweise 
for i in dic_Maschine:
    
    #beachten der Laufwege der Mitarbeiter und ordnungsgemäßes Abbilden in der Flowmatrix
    #schauen welcher Arbeiter diese Station i anläuft und dann die nächste Station finden
    inn=False
    k= 0
    while inn == False:
        
        Ordnung=List_of_Workers[k].Zuordnen(dic_Maschine)
        #print(Ordnung)
        folge_Station= n+100 #damit dieser Fall aus dem Raster fällt, falls er nicht auftritt
        if i in Ordnung:
            inn=True
            if len(Ordnung)>1: #beachten das der Mitarbeiter überhaupt mehr als eine Station betätigt
                temp2= Ordnung.index(i)
               
                #schauen was die nachfolgende Station ist falls es die im Vektor als letztes stehenede Station ist,
                # wird davon ausgegangen das der Arbeiter wieder mit der ersten Station beginnt (Kreislauf)
                if temp2 < len(Ordnung)-1:
                    
                    folge_Station=Ordnung[temp2+1]
                else: 
                    folge_Station=Ordnung[0]
        k=k+1
                
            #print(str(i)+ " folgt "+ str(folge_Station))
  
                
    
        #temp1 ist der Materialfluss es gibt immer nur eine nächste Station
        temp1=Materialfluss.index(i) #Index der Anlage die auf die i-te Anlage folgt
        if temp1 < n-1:
            folge_Anlage=Materialfluss[temp1+1]
        else:
            folge_Anlage= n+100 #damit dieser Fall aus dem Raster fällt
        
    for j in dic_Maschine:
           
            if i != j:  #es gibt keine Distanz von i nach i und auch keinen Flow 
                """
                Fallunterscheidungen zur Erstellung der Flow-Matrix:
                    1. Fall: Der Arbeiter und das Teilchen bewegen sich zur selben Station = 1
                    2. Fall: Das Teil bewegt sich weiter zu Station j, der Arbeiter nicht = Lamdba
                    3. Fall: Der Arbeiter geht weiter zu Station j, das Teil nicht = 1-Lamnda
                    4. Fall weder das Teil noch der Arbeiter gehen zu Station j = 0
                """
                if folge_Anlage == j and folge_Station ==j :
                    f=1
                    #print("fall 1 " + str(i) + " folgt " + str(j))
                elif folge_Anlage==j and folge_Station != j:
                    f=Lambda
                    #print("fall 2 " + str(i) + " folgt " + str(j))
                elif folge_Anlage !=j and folge_Station == j:
                    #print("fall 3  " + str(i) + " folgt " + str(j))
                    f=Lambda1
                else:
                    f=0
                
                
                flow_list.append((f,i,j))
                #Distanz Liste erstellen
                d=dic_Maschine[i].Abstand(dic_Maschine[j])
                distance_list.append((d,i,j))
            

Solution=fkt.Greedy_Alg(flow_list,distance_list,n)
#Plotten des neuen Layouts, die Nummern haben sich verändert sonst ist es gleich geblieben
fkt.neuesLayoutplotten(dic_Maschine,Solution, Lambda)                
                
            
        
        


        
      

#%%