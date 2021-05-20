from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.time import BaseScheduler
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from random import randint
def compute_gini(model):
    agent_healths=[agent.health for agent in model.schedule.agents]
    x=sorted(agent_healths)
    N=model.num_agents
    if sum(x)!=0:
        B=sum(xi * (N-i) for i, xi in enumerate(x))/(N*sum(x))
    else:
        B=0
    return (1+(1/N)-2*B)
class Cell(Agent): #główna klasa ,,parent" wszystkich agentów
    def __init__(self, unique_id, model,type):
        super().__init__(unique_id, model)
        self.health = 10
        self.type=type #zmienna ułatwiająca odczytywanie typu agenta
        self.move_count=0 #zmienna dzięki której można odczytać ile ruchów wykonał agent
        self.activation_matrix=[False, False] #tablica która odnosi się do Limfocytu B,
         #ponieważ potrzebuje on bodziec zarówno od zainfekowanegoLimfocytaB jak i od aktywowanegoLimfocytaT
        self.proliferation_rate=1 #zmienna odpowiadająca za szybkość proliferacji agenta
        self.death_rate=1 
        self.action_count=0 #zmienna odpowiadająca ilości akcji wykonanych przez agenta(proliferacja, aktywacja itd)
        if self.type=="Neuron":
            self.myelin_number=4 #zmienna odpowiadająca ilości komórek mielinowych otaczających agenta 
        else:
            self.myelin_number=0
        print("Hi im agent "+str(unique_id)+" "+type)
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
        if self.move_count%self.death_rate==0:
            self.health-=1
        self.health-=self.action_count #za każdą wykonaną w danym ruch akcje odejmujemu punkt życia
        self.action_count=0
    def proliferation(self): #funkcja odpowiedzialna za mechanizm proliferacji
        x=randint(1,10) 
        if x<=self.proliferation_rate: #prawdopodobieństwo zajścia proliferacji zależy od zmiennej proliferation_rate
            self.action_count+=1
            new=len(self.model.new_agents)+1
            dead=len(self.model.dead_agents)
            agents=self.model.num_agents
            self.model.available_ids.add(agents+new-dead+2)#dodawanie nowych id do listy przechowującej id do wykorzystania
            #self.model.available_ids.add(agents+new-dead+3)
            id=min(self.model.available_ids) # jako id nowego agenta przyjmujemy najmniejsze wolne id
            self.model.available_ids.remove(id) #usuwamy najmniejsze id z setu wolnych id
            
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
            except UnboundLocalError:
                print("")


    def death(self):
        if self.health<=0:
            self.model.dead_agents.add(self) #dodajemy agenta do setu zmarłych agentów
            self.model.available_ids.add(self.unique_id) # dodajemy id agenta do setu wolnych id

    def cytotoxicity(self):
        #wybieramy sąsiadujących agentów w odległości 1 pól
        neighbors=self.model.grid.get_neighbors(self.pos, True, True, 2) 
        affected=['ZainfekowanyLimfocytB', 'Neuron', 'Myelin'] #lista typów agentów na które działa efekt cytotoksyczny
        for agent in neighbors:
            if agent.type in affected:
                #warunek ten odnosi się do neuronu, ponieważ może on otrzymać ,,obrażenia",
                #tylko kiedy jest pozbawiony osłonki mielinowej
                if agent.myelin_number<=0: 
                    agent.health-=1
    
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
        if self.health<1:
            self.death()
        else:
            self.proliferation()
            self.move()
            x=randint(1,100)
            if x<=2:
                self.aktywacja_wirusa()
    def aktywacja_wirusa(self): #funckaj która zmienia LimfocytB z zainfekowanyLimfocytB
        n=ZainfekowanyLimfocytB(self.unique_id,self.model,"ZainfekowanyLimfocytB")
        n.pos=self.pos #pozycja pozostaje ta sama, id również
        self.model.new_agents.add(n) #dodajemy do setu nowych agentów
        self.model.dead_agents.add(self) #dodajemy do setu zmarłuch agentów
        self.action_count+=1

    def activate(self):
        d=[True, True]
        if self.activation_matrix==d: #sprawdzamy czy otrzymano bodźce zarówno od Limfocyta T 
                                        #jak i od zainfekowanego limfocyta B
            n=AktywowanyLimfocytB(self.unique_id, self.model, "AktywowanyLimfocytB")
            n.pos=self.pos
            self.model.new_agents.add(n)
            self.model.dead_agents.add(self)

class ZainfekowanyLimfocytB(Cell):
    def step(self):
        if self.health<1:
            self.death()
        else:
            self.proliferation()
            self.move()
            self.infection()
            self.antigen_activation()
        
    def infection(self): #funkcja odpowiedzialna za infekowanie innych LimfocytówB
        cellmates=self.model.grid.get_cell_list_contents([self.pos])
        for agent in cellmates:
            if agent.type=="LimfocytB":
                agent.aktywacja_wirusa()
                self.action_count+=1
    def antigen_activation(self): #funkcja odpowiedzialna za aktywowanie sąsiednik Limfocytów B i T
        neighbors=self.model.grid.get_neighbors(self.pos,True, False, 1)
        for agent in neighbors:
            if agent.type=="LimfocytB" or agent.type=="LimfocytT":
                agent.activation_matrix[0]=True #tablica ta ma tylko znaczenie w przypadku Limfocytów B
                agent.activate()
                self.action_count+=1 
                #możliwe że zmienna action_count powinna się zwiększać zgodnie z ilością aktytowanych agentów
class AktywowanyLimfocytB(LimfocytB):
    def step(self):
        if self.health<1:
            self.death()
        else:
            self.proliferation()
            self.wspomaganie_LimfocytT()
            self.move()
    def wspomaganie_LimfocytT(self): #funkcja wspomagająca proliferację LimfocytówT, 
        neighbors=self.model.grid.get_neighbors(self.pos,True, False, 2)
        for agent in neighbors:
            if agent.type=="LimfocytT":
                agent.proliferation_rate=2
                self.action_count+=1
        
class LimfocytT(Cell):
    def step(self):
        if self.health<1:
            self.death()
        else:
            self.proliferation()
            self.move()
        
    def activate(self):
        n=AktywowanyLimfocytT(self.unique_id, self.model, "AktywowanyLimfocytT")
        n.pos=self.pos
        self.model.new_agents.add(n)
        self.model.dead_agents.add(self)
class AktywowanyLimfocytT(LimfocytT):
    def step(self):
        if self.health<1:
            self.death()
        else:
            self.proliferation()
            self.move()
            self.LimfocytB_activation()
            self.cytotoxicity()
        
    def LimfocytB_activation(self):
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
            self.proliferation()
            self.move()

class Myelin(Cell):
    def step(self):
        self.death()

class Model(Model):
    def __init__(self, N, B, T, Treg, width,height):
        self.num_myelin=N*4
        self.num_agents = N+B+T+Treg+self.num_myelin
        self.num_neurons=N
        self.num_limfocytB=B
        self.num_limfocytT=T
        self.num_limfocytTreg=Treg
        self.grid=MultiGrid(width,height,True)
        self.schedule = RandomActivation(self)
        self.available_ids=set()
        self.dead_agents=set()
        self.new_agents=set()
        self.max_id=0
        # Create agents
        for i in range(self.num_neurons):
            a = Neuron(i, self,"Neuron")
            self.schedule.add(a)
            #Add agent to a random grid cell
            x=self.random.randrange(self.grid.width)
            y=self.random.randrange(self.grid.height)
            self.grid.place_agent(a,(x,y))
            cells=self.grid.get_neighborhood(a.pos, False, False, 1)
            id=self.num_agents-i
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

        self.available_ids.add(self.num_agents+1)
        self.max_id=self.num_agents

        self.datacollector=DataCollector(
            model_reporters={"Gini":compute_gini},
            agent_reporters={"Health": "health"})
    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)
        self.adding_removing()
        print("Liczba agentów: " + str(self.num_agents))
        
    def running(self):
        self.step()

    def adding_removing(self): #funckja odpowiedzialna za dodawanie i usuwanie agentów
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

        self.dead_agents.clear()
        for n in self.new_agents:
            self.schedule.add(n)
            self.num_agents+=1
            self.grid.place_agent(n, n.pos)
        self.new_agents.clear()
        self.max_id=max(self.available_ids)
        self.available_ids.add(self.num_agents+1)
            

