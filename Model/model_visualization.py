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

grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500)
server = ModularServer(Model,
						[grid],
						"Ms Model",
						{"N":10, "B":60, "T":20, "Treg":10, "width":20, "height":20})
#deklaracja modelu Liczba Neuronów, Liczba Limfocytów B, Liczba Limfocytów T, Liczba Limfocytów Treg, Szerokosć, Wysokość)
server.port = 8521 # The default
server.launch()
