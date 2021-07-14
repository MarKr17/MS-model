from model import *
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from mesa.visualization.ModularVisualization import VisualizationElement 
from colour import Color
import numpy as np
cell_colors=list(Color("white").range_to(Color("blue"),11))

myelin_colors=["#a64100","#a64100","#b45200","##c16400","#ce7500","#d98800",
				"#e39b00","#ebae00","#f2c200","#f8d600","#fcea00",
				"#ffff04","#ffff04"]
neuron_color="#dd0303"
limfocytB_color="#0016ff"
infected_color="#565656"
limfocytT_color="#8c0080"
limfocytTreg_color="#17831c"
activatedB_color="#ff0055"
activatedT_color="#8c0041"

hexagons=[]
for i in range(0,10):
	hexagons.append("hexagons/hexagon"+str(i)+".png")
hexagons.insert(0,"hexagons/hexagon0.png")
hexagons.append("hexagons/hexagon10.png")



def agent_portrayal(agent):
	portrayal = {"Shape": "circle",
				"Color": "blue",
				"Filled": "true",
				"Layer": 0,
				"text_color": "black",
				"r": 0.2}
	if agent.health<0:
			agent.health=0
	if agent.type=='Neuron':
		portrayal["Color"]=neuron_color
		portrayal["w"]=0.6
		portrayal["h"]=0.6
		portrayal["Shape"]="rect"
	if agent.type=='LimfocytB':
		portrayal["Color"]=limfocytB_color
		portrayal["r"]=0.4
	if agent.type=='ZainfekowanyLimfocytB':
		portrayal["Color"]=infected_color
		portrayal["r"]=0.4
	if agent.type=='LimfocytT':
		#portrayal["Shape"]=hexagons[agent.health]
		#portrayal["w"]=0.2
		#portrayal["h"]=0.2
		#portrayal["scale"]=0.6
		portrayal["Color"]=limfocytT_color
		portrayal["r"]=0.4
	if agent.type=='AktywowanyLimfocytT':
		portrayal["Color"]=activatedT_color
		portrayal["r"]=0.4
	if agent.type=='LimfocytTreg':
		portrayal["Color"]=limfocytTreg_color
		portrayal["r"]=0.4
	if agent.type=='AktywowanyLimfocytB':
		portrayal["Color"]=activatedB_color
		portrayal["r"]=0.4
	if agent.type=='Myelin':
		#print("Myelin hp "+ str(agent.health))
		portrayal["Color"]=myelin_colors[agent.health]
		portrayal["r"]=0.5
	return portrayal
chart1 = ChartModule([{"Label": "Populacja",
                      "Color": "Black"}],
                    data_collector_name='datacollector_population')
chart2 = ChartModule([{"Label": "Populacja Limfocytów T",
                      "Color": "Purple"}],
                    data_collector_name='datacollector_T_population')
chart3 = ChartModule([{"Label": "Populacja Limfocytów B",
                      "Color": "Blue"}],
                    data_collector_name='datacollector_B_population')
chart4 = ChartModule([{"Label": "Populacja Limfocytów Treg",
                      "Color": "Green"}],
                    data_collector_name='datacollector_Treg_population')
chart5 = ChartModule([{"Label": "Populacja Aktywnych Limfocytów B",
                      "Color": "Blue"}],
                    data_collector_name='datacollector_B_active_population')
chart6 = ChartModule([{"Label": "Populacja Aktywnych Limfocytów T",
                      "Color": "Purple"}],
                    data_collector_name='datacollector_T_active_population')
chart7 = ChartModule([{"Label": "Populacja Zainfekowanych Limfocytów B",
                      "Color": "Black"}],
                    data_collector_name='datacollector_B_infected_population')
chart8=ChartModule([{"Label": "Populacja osłonek mielinowych",
						"Color": "Yellow"}],
					data_collector_name='datacollector_myelin_population')
grid = CanvasGrid(agent_portrayal, 30, 30, 500, 500)
server = ModularServer(Model,
						[grid,chart8, chart1,chart2,chart3,chart4,chart5,chart6,chart7],
						"Ms Model",
						{"N":17, "B":25, "T":16, "Treg":9, "width":30, "height":30})
#deklaracja modelu Liczba Neuronów, Liczba Limfocytów B, Liczba Limfocytów T, Liczba Limfocytów Treg, Szerokosć, Wysokość)
server.port = 8521 # The default
server.launch()
