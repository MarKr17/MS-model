from model import *
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from mesa.visualization.ModularVisualization import VisualizationElement 
from colour import Color
import numpy as np
cell_colors=list(Color("white").range_to(Color("blue"),11))

def agent_portrayal(agent):
	portrayal = {"Shape": "circle",
				"Color": "blue",
				"Filled": "true",
				"Layer": 0,
				"text": agent.unique_id,
				"text_color": "black",
				"r": 0.2}
	if agent.type=='Neuron':
		portrayal["Color"]="red"
		portrayal["r"]=0.6
	if agent.type=='LimfocytB':
		portrayal["Color"]="blue"
		portrayal["r"]=0.2
	if agent.type=='ZainfekowanyLimfocytB':
		portrayal["Color"]="black"
		portrayal["r"]=0.2
	if agent.type=='LimfocytT':
		portrayal["Color"]="purple"
		portrayal["r"]=0.2
	if agent.type=='AktywowanyLimfocytT':
		portrayal["Color"]="purple"
		portrayal["r"]=0.4
	if agent.type=='LimfocytTreg':
		portrayal["Color"]="green"
		portrayal["r"]=0.2
	if agent.type=='AktywowanyLimfocytB':
		portrayal["Color"]="blue"
		portrayal["r"]=0.4
	if agent.type=='Myelin':
		portrayal["Color"]="yellow"
		portrayal["r"]=0.2
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
grid = CanvasGrid(agent_portrayal, 30, 30, 500, 500)
server = ModularServer(Model,
						[grid, chart1,chart2,chart3,chart4,chart5,chart6,chart7],
						"Ms Model",
						{"N":10, "B":50, "T":33, "Treg":17, "width":30, "height":30})
#deklaracja modelu Liczba Neuronów, Liczba Limfocytów B, Liczba Limfocytów T, Liczba Limfocytów Treg, Szerokosć, Wysokość)
server.port = 8521 # The default
server.launch()
