from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.time import BaseScheduler
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from random import randint
import math
def compute_gini(model):
    agent_healths=[agent.health for agent in model.schedule.agents]
    x=sorted(agent_healths)
    N=model.num_agents
    if sum(x)!=0:
        B=sum(xi * (N-i) for i, xi in enumerate(x))/(N*sum(x))
    else:
        B=0
    return (1+(1/N)-2*B)
def compute_population(model):
    population=model.num_agents
    return population
def T_population(model):
    n=0
    for agent in model.schedule.agents:
        if agent.type=="LimfocytT":
            n+=1
    return n
def T_popualtion_precentage(model):
    t=T_population(model)
    all=compute_population(model)
    x=(t/all)*100
    return x
def B_population(model):
    n=0
    for agent in model.schedule.agents:
        if agent.type=="LimfocytB":
            n+=1
    return n
def Treg_population(model):
    n=0
    for agent in model.schedule.agents:
        if agent.type=="LimfocytTreg":
            n+=1
    return n
def B_activated_population(model):
    n=0
    for agent in model.schedule.agents:
        if agent.type=="AktywowanyLimfocytB":
            n+=1
    return n
def T_activated_population(model):
    n=0
    for agent in model.schedule.agents:
        if agent.type=="AktywowanyLimfocytT":
            n+=1
    return n
def B_infected_population(model):
    n=0
    for agent in model.schedule.agents:
        if agent.type=="ZainfekowanyLimfocytB":
            n+=1
    return n   
class Cell(Agent): #główna klasa ,,parent" wszystkich agentów
    def __init__(self, unique_id, model,type):
        super().__init__(unique_id, model)
        self.health = 10
        self.type=type #zmienna ułatwiająca odczytywanie typu agenta
        self.move_count=0 #zmienna dzięki której można odczytać ile ruchów wykonał agent
        self.activation_matrix=[False, False] #tablica która odnosi się do Limfocytu B,
         #ponieważ potrzebuje on bodziec zarówno od zainfekowanegoLimfocytaB jak i od aktywowanegoLimfocytaT
        self.proliferation_rate=8#zmienna odpowiadająca za szybkość proliferacji agenta
        self.death_rate=50
        self.activated=False
        self.infected=False
        self.dead=False
        self.action_count=0 #zmienna odpowiadająca ilości akcji wykonanych przez agenta(proliferacja, aktywacja itd)
        if self.type=="Neuron":
            self.myelin_number=4 #zmienna odpowiadająca ilości komórek mielinowych otaczających agenta 
        else:
            self.myelin_number=0
        print("Hi im agent "+str(unique_id)+" "+type)
        if "LimfocytB" in self.type:
            self.health=20
            self.proliferation_rate=6
            self.death_rate=50
        if "Aktywowany" in self.type:
            self.death_rate=100
            proliferation_rate=1
        if "Treg" in self.type:
            self.health=12
            self.death_rate=85
            self.proliferaton_rate=1
        if self.type=="LimfocytT":
            self.health=10
            self.death_rate=100
            self.proliferation_rate=4
        if self.type=="ZainfekowanyLimfocytB":
            self.death_rate=100
            self.health=10
            self.proliferation_rate=10
    def step(self):
        nieruchome=['Neuron', 'Myelin']
        if self.type not in nieruchome:
            self.proliferation()
            self.move()
            self.death()
    def move(self): #funkcja odpowiadająca za ruch agenta na planszy
        possible_steps=self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False)
        new_position=self.random.choice(possible_steps)
        self.model.grid.move_agent(self,new_position)
        self.move_count+=1 
        #self.health-=math.floor(self.move_count/5)
        x=randint(1,100)
        if x<=self.death_rate:
            self.health-=1
        self.health-=math.floor(self.action_count/2) #za każdą wykonaną w danym ruch akcje odejmujemu punkt życia
        self.action_count=0
    def proliferation(self): #funkcja odpowiedzialna za mechanizm proliferacji
        x=randint(1,100) 
        if (x<=self.proliferation_rate) and (self.action_count==0) and(self.activated==False) and (self.dead==False): #prawdopodobieństwo zajścia proliferacji zależy od zmiennej proliferation_rate
            
            if len(self.model.available_ids)==0:
                self.model.max_id+=1
                id=self.model.max_id
            else:
                id=min(self.model.available_ids)
                self.model.available_ids.remove(id)
            
            #tworzymy nowego agenta zgodnie z typem agenta który dokonuje proliferacji
            if self.type=="LimfocytB":
                n=LimfocytB(id,self.model,"LimfocytB")
            if self.type=="ZainfekowanyLimfocytB":
                n=ZainfekowanyLimfocytB(id,self.model,"ZainfekowanyLimfocytB")
            if self.type=="AktywowanyLimfocytB":
                n=AktywowanyLimfocytB(id,self.model,"AktywowanyLimfocytB")
            if self.type=="LimfocytT":
                n=LimfocytT(id,self.model,"LimfocytT")
            if self.type=="AktywowanyLimfocytT":
                n=AktywowanyLimfocytT(id,self.model,"AktywowanyLimfocytT")
            if self.type=="LimfocytTreg":
                n=LimfocytTreg(id,self.model,"LimfocytTreg")
            #jako miejsce umieszczenia agenta na planszy wybieramy losowo pole sąsiadujące
            possible_steps=self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=False)
            try: 
                n.pos=self.random.choice(possible_steps) #wybraną pozycję zapisujemy w odpowiednim polu agenta
                self.model.new_agents.add(n) #dodajemy nowego agenta do listy nowych agentów
                self.action_count+=1
            except UnboundLocalError:
                print("")


    def death(self):
        if (self.health<=0) and (self.activated==False) and (self.infected==False):
            self.model.dead_agents.add(self) #dodajemy agenta do setu zmarłych agentów
            self.model.available_ids.add(self.unique_id) # dodajemy id agenta do setu wolnych id
            self.dead=True

    def cytotoxicity(self):
        #wybieramy sąsiadujących agentów w odległości 1 pól
        neighbors=self.model.grid.get_neighbors(self.pos, True, True, 2) 
        affected=['ZainfekowanyLimfocytB', 'Neuron', 'Myelin'] #lista typów agentów na które działa efekt cytotoksyczny
        for agent in neighbors:
            if agent.type in affected:
                #warunek ten odnosi się do neuronu, ponieważ może on otrzymać ,,obrażenia",
                #tylko kiedy jest pozbawiony osłonki mielinowej
                if agent.myelin_number<=0: 
                    agent.health-=2
                    self.action_count+=1
    
class Neuron(Cell):
    def step(self):
        #fragment odpowiadający za sprawdzenie ile żywych komórek mielinowych znajduje się przy neuronie w danym momencie
        neighbors=self.model.grid.get_neighbors(self.pos, False, False,1)
        m=0
        for agent in neighbors:
            if agent.type=='Myelin':
                m+=1
        self.myelin_number=m
        self.death()



class LimfocytB(Cell):
    def step(self):
        self.action_count=0
        if self.health<1:
            self.death()
        else:
            self.move()
            virus_activation_rate=1
            x=randint(1,100)
            if x<=virus_activation_rate:
                self.aktywacja_wirusa()
            self.proliferation()
        
    def aktywacja_wirusa(self): #funckaj która zmienia LimfocytB z zainfekowanyLimfocytB
        if  (self.infected==False) and (self.dead==False):
            n=ZainfekowanyLimfocytB(self.unique_id,self.model,"ZainfekowanyLimfocytB")
            n.pos=self.pos #pozycja pozostaje ta sama, id również
            self.model.new_agents.add(n) #dodajemy do setu nowych agentów
            self.model.dead_agents.add(self) #dodajemy do setu zmarłuch agentów
            self.infected=True

    def activate(self):
        d=[True, True]
        #if (self.activation_matrix==d) and (self.action_count==0) and (self.activated==False) and (self.dead==False): #sprawdzamy czy otrzymano bodźce zarówno od Limfocyta T 
        n=AktywowanyLimfocytB(self.unique_id, self.model, "AktywowanyLimfocytB")#jak i od zainfekowanego limfocyta B
        n.pos=self.pos
        self.model.new_agents.add(n)
        self.model.dead_agents.add(self)
        self.action_count+=1
        self.activated=True

class ZainfekowanyLimfocytB(Cell):
    def step(self):
        if self.health<1:
            self.death()
        else:
            self.move()
            self.infection()
            self.antigen_activation()
            self.proliferation()
        
    def infection(self): #funkcja odpowiedzialna za infekowanie innych LimfocytówB
        infection_rate=100
        x=randint(1,100)
        if x<=infection_rate:
            cellmates=self.model.grid.get_cell_list_contents([self.pos])
            for agent in cellmates:
                if agent.type=="LimfocytB":
                    agent.aktywacja_wirusa()
                    self.action_count+=1
    def antigen_activation(self): #funkcja odpowiedzialna za aktywowanie sąsiednik Limfocytów B i T
        antigen_activation_rate=10
        x=randint(1,10)
        if x<=antigen_activation_rate:
            neighbors=self.model.grid.get_neighbors(self.pos,True, False, 1)
            for agent in neighbors:
                if agent.type=="LimfocytT":
                    agent.activate()
                    self.action_count+=1 
                if agent.type=="LimfocytB":
                    agent.activation_matrix[0]==True
                    agent.activate()
                    self.action_count+=1
                    #możliwe że zmienna action_count powinna się zwiększać zgodnie z ilością aktytowanych agentów
class AktywowanyLimfocytB(LimfocytB):
    def step(self):
        if self.health<1:
            self.death()
        else:
            self.wspomaganie_LimfocytT()
            self.move()
            self.proliferation()
    def wspomaganie_LimfocytT(self): #funkcja wspomagająca proliferację LimfocytówT, 
        support_rate=5
        x=randint(1,10)
        if x<=support_rate:
            neighbors=self.model.grid.get_neighbors(self.pos,True, False, 2)
            for agent in neighbors:
                if agent.type=="LimfocytT":
                    agent.proliferation_rate+=1
                    self.action_count+=1
        
class LimfocytT(Cell):
    def step(self):
        self.action_count==0
        if self.health<1:
            self.death()
        else:
            self.move()
            self.proliferation()
    def activate(self):
        if (self.activated==False) and (self.dead==False):
            n=AktywowanyLimfocytT(self.unique_id, self.model, "AktywowanyLimfocytT")
            n.pos=self.pos
            self.model.new_agents.add(n)
            self.model.dead_agents.add(self)
            self.action_count+=1
            self.activated=True
class AktywowanyLimfocytT(LimfocytT):
    def step(self):
        if self.health<1:
            self.death()
        else:
            
            self.move()
            self.LimfocytB_activation()
            cytotoxicity_rate=10
            x=randint(1,10)
            if x<=cytotoxicity_rate:
                self.cytotoxicity()
            self.proliferation()
        
    def LimfocytB_activation(self):
        activation_rate=2
        x=randint(1,10)
        if x<=activation_rate:
            neighbors=self.model.grid.get_neighbors(self.pos,True, True, 1)
            for agent in neighbors:
                if agent.type=="LimfocytB":
                    agent.activation_matrix[1]=True
                    agent.activate()
                self.action_count+=1
class LimfocytTreg(Cell):
    def step(self):
        if self.health<1:
            self.death()
        else:
            
            self.move()
            self.RegulacjaLimfocytówT()
            self.proliferation()
    def RegulacjaLimfocytówT(self):
        regulation_rate=10
        x=randint(1,10)
        if x<=regulation_rate:
            neighbors=self.model.grid.get_neighbors(self.pos, True, True,1)
            for agent in neighbors:
                if (agent.type=="LimfocyT") or (agent.type=="AktywowanyLimfocytT"):
                    agent.health-=2
                    #self.proliferation_rate+=1
                    self.action_count+=1

class Myelin(Cell):
    def step(self):
        self.regeneracja()
        self.death()
    def regeneracja(self):
        regeneration_rate=3
        x=randint(1,10)
        if x<=regeneration_rate:
            self.health+=1

class Model(Model):
    def __init__(self, N, B, T, Treg, width,height):
        self.num_myelin=N*4
        self.num_agents = N+B+T+Treg+self.num_myelin
        self.num_neurons=N
        self.num_myelin=4
        self.num_limfocytB=B
        self.num_active_B=0
        self.num_infected_B=0
        self.num_limfocytT=T
        self.num_activeT=0
        self.num_limfocytTreg=Treg
        self.grid=MultiGrid(width,height,True)
        self.schedule = RandomActivation(self)
        self.available_ids=set()
        self.dead_agents=set()
        self.new_agents=set()
        self.max_id=0
        self.step_count=1
        open('new_and_dead.txt', 'w').close()
        # Create agents
        for i in range(self.num_neurons):
            a = Neuron(i, self,"Neuron")
            self.schedule.add(a)
            #Add agent to a random grid cell
            x=self.random.randrange(self.grid.width)
            y=self.random.randrange(self.grid.height)
            self.grid.place_agent(a,(x,y))
            cells=self.grid.get_neighborhood(a.pos, False, False, 1)
            id=self.num_agents-i*4
            for cell in cells:
                m=Myelin(id, self, "Myelin")
                self.schedule.add(m)
                self.grid.place_agent(m,cell)
                id-=1

        #dodawanie różnych typów agentów zgodnie z ich liczbą podaną przy inicjacji modelu
        for i in range(self.num_limfocytB):
            a = LimfocytB(i+self.num_neurons, self,"LimfocytB")
            self.schedule.add(a)
            #Add agent to a random grid cell
            x=self.random.randrange(self.grid.width)
            y=self.random.randrange(self.grid.height)
            self.grid.place_agent(a,(x,y))
        for i in range(self.num_limfocytT):
            a = LimfocytT(i+N+B,self, "LimfocytT")
            self.schedule.add(a)
            #Add agent to a random grid cell
            x=self.random.randrange(self.grid.width)
            y=self.random.randrange(self.grid.height)
            self.grid.place_agent(a,(x,y))
        for i in range(self.num_limfocytTreg):
            a = LimfocytTreg(i+N+B+T,self,"LimfocytTreg")
            self.schedule.add(a)
            #Add agent to a random grid cell
            x=self.random.randrange(self.grid.width)
            y=self.random.randrange(self.grid.height)
            self.grid.place_agent(a,(x,y))

        self.max_id=self.num_agents-1

        self.datacollector_population=DataCollector(
            model_reporters={"Populacja":compute_population})
        self.datacollector_T_population=DataCollector(
            model_reporters={"Populacja Limfocytów T":T_population})
        #self.datacollector_T_precentage=DataCollector(
            #model_reporters={"Precentage Limfocyt T": T_popualtion_precentage})
        self.datacollector_B_population=DataCollector(
            model_reporters={"Populacja Limfocytów B":B_population})
        self.datacollector_Treg_population=DataCollector(
            model_reporters={"Populacja Limfocytów Treg":Treg_population})
        self.datacollector_B_active_population=DataCollector(
            model_reporters={"Populacja Aktywnych Limfocytów B": B_activated_population})
        self.datacollector_T_active_population=DataCollector(
            model_reporters={"Populacja Aktywnych Limfocytów T": T_activated_population})
        self.datacollector_B_infected_population=DataCollector(
            model_reporters={"Populacja Zainfekowanych Limfocytów B": B_infected_population})

    def step(self):
        self.schedule.step()
        self.datacollector_population.collect(self)
        self.datacollector_T_population.collect(self)
        #self.datacollector_T_precentage.collect(self)
        self.datacollector_B_population.collect(self)
        self.datacollector_Treg_population.collect(self)
        self.datacollector_B_active_population.collect(self)
        self.datacollector_T_active_population.collect(self)
        self.datacollector_B_infected_population.collect(self)
        self.adding_removing()
        print("Liczba agentów: " + str(self.num_agents))
        self.step_count+=1
        
    def running(self):
        self.step()

    def adding_removing(self): #funckja odpowiedzialna za dodawanie i usuwanie agentów

        f=open("new_and_dead.txt", 'a')
        f.write("Step " + str(self.step_count) +"\n")
        f.write("======Dead agents======: "+"\n")
        for d in self.dead_agents:
            try:
                self.schedule.remove(d)
                self.num_agents-=1
                #self.available_ids.add(d.unique_id)
            except KeyError:
                continue
            try:
                self.grid._remove_agent(d.pos,d)
            except KeyError:
                continue
            f.write(str(d.unique_id) +" " + d.type +"\n")
        self.dead_agents.clear()
        f.write("======New Agents=====: " +"\n")
        for n in self.new_agents:
            self.schedule.add(n)
            self.num_agents+=1
            self.grid.place_agent(n, n.pos)
            if n.unique_id in self.available_ids:
                self.available_ids.remove(n.unique_id)
            f.write(str(n.unique_id) + " " + n.type +"\n")
        self.new_agents.clear()
        m=1
        n=0
        for agent in self.schedule.agents:
            if agent.unique_id>m:
                m=agent.unique_id
            if (agent.type=="LimfocytT") or (agent.type=="AktywowanyLimfocytT"):
                n+=1
        self.max_id=m
        self.num_limfocytT=0
        self.deficiencies()
        f.close()
    def deficiencies(self):
        n=B_population(self)
        if n==0:
            if len(self.available_ids)==0:
                self.max_id+=1
                id=self.max_id
            else:
                id=min(self.available_ids)
                self.available_ids.remove(id)
            agent=LimfocytB(id,self,"LimfocytB")
            self.schedule.add(agent)
            x=self.random.randrange(self.grid.width)
            y=self.random.randrange(self.grid.height)
            self.grid.place_agent(agent,(x,y))
        n=T_population(self)
        if n==0:
            for i in range(10):    
                if len(self.available_ids)==0:
                    self.max_id+=1
                    id=self.max_id
                else:
                    id=min(self.available_ids)
                    self.available_ids.remove(id)
                agent=LimfocytB(id,self,"LimfocytT")
                self.schedule.add(agent)
                x=self.random.randrange(self.grid.width)
                y=self.random.randrange(self.grid.height)
                self.grid.place_agent(agent,(x,y))
        n=Treg_population(self)
        if n==0:
            if len(self.available_ids)==0:
                self.max_id+=1
                id=self.max_id
            else:
                id=min(self.available_ids)
                self.available_ids.remove(id)
            agent=LimfocytB(id,self,"LimfocytTreg")
            self.schedule.add(agent)
            x=self.random.randrange(self.grid.width)
            y=self.random.randrange(self.grid.height)
            self.grid.place_agent(agent,(x,y))

        
            

