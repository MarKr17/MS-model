from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.time import BaseScheduler
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from random import randint
import math
import numpy as np
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
def myelin_population(model):
    n=0
    for agent in model.schedule.agents:
        if agent.type=="Myelin":
            n+=1
    return n

def myelin_healths(model):
    n=0
    for agent in model.schedule.agents:
        if agent.type=="Myelin":
            n+=agent.health
            #print(str(n))
    if n<0:
        n=0
    return n


class Agent(Agent): #główna klasa ,,parent" wszystkich agentów
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
        self.prob_dmg=1000 # zmienna określająca prawdopodobieństwo otrzymania dmg dla neuronu
        self.action_count=0 #zmienna odpowiadająca ilości akcji wykonanych przez agenta(proliferacja, aktywacja itd)
        if self.type=="Neuron":
            self.myelin_number=8 #zmienna odpowiadająca liczbie komórek mielinowych otaczających agenta 
            self.regeneration_counter=0#zmienna odpowiadająca liczbie wykonanych regeneracji przez dany neuron
            self.prob_dmg=0
        else:
            self.myelin_number=0
        if self.type=="Myelin":
            self.health=100
        #print("Hi im agent "+str(unique_id)+" "+type)
        if "LimfocytB" in self.type:
            self.health=25
            #self.proliferation_rate=3+math.floor(self.model.cytokina/30)
            self.proliferation_rate=7+math.floor(self.model.cytokina/10)
            self.death_rate=40
        if "Aktywowany" in self.type:
            self.death_rate=90
            #self.proliferation_rate=1+math.floor(self.model.cytokina/10)
            self.proliferation_rate=2
            proliferation_rate=1
        if "Treg" in self.type:
            self.health=15
            self.death_rate=50
            self.proliferaton_rate=2
            self.proliferation_rate=3#+math.floor(self.model.cytokina/120)
        if self.type=="LimfocytT":
            self.health=10
            self.death_rate=50
            self.proliferation_rate=2+math.floor(self.model.cytokina/10)
            #self.proliferation_rate=1
        if self.type=="ZainfekowanyLimfocytB":
            self.death_rate=100
            self.health=10
            self.proliferation_rate=5
    def step(self):
        nieruchome=['Neuron', 'Myelin']
        if self.type not in nieruchome:
            self.proliferation()
            self.move()
            self.death()
    def move(self): #funkcja odpowiadająca za ruch agenta na planszy
        
        d=self.direction()
        v=np.array(np.asarray(self.pos))
        v2=d+v
        #print("Vector1:" + str(v2))

        if v2[[0]]>=self.model.grid.width:
            v2[[0]]=self.model.grid.width-1
        if v2[[0]]<0:
            v2[[0]]=0
        if v2[[1]]>=self.model.grid.height:
            v2[[1]]=self.model.grid.height-1
        if v2[[1]]<0:
            v2[[1]]=0

        #print("Vector2:" + str(v2))
        self.model.grid.move_agent(self,(int(v2[[0]]),int(v2[[1]])))
        self.move_count+=1

        
        #self.health-=math.floor(self.move_count/5)
        x=randint(1,100)
        if x<=self.death_rate:
            self.health-=1
        self.health-=math.floor(self.action_count/2) #za każdą wykonaną w danym ruch akcje odejmujemu punkt życia
        if self.health<0:
            self.health=0;
        self.action_count=0
    
    def proliferation(self): #funkcja odpowiedzialna za mechanizm proliferacji
        x=randint(1,100) 
        bools=[False,False,False,True]
        bools2=[self.activated, self.dead, self.infected, x<=self.proliferation_rate]
        if bools==bools2: #prawdopodobieństwo zajścia proliferacji zależy od zmiennej proliferation_rate
            
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
            #self.model.available_ids.add(self.unique_id) # dodajemy id agenta do setu wolnych id
            self.dead=True

    def cytotoxicity(self):
        #wybieramy sąsiadujących agentów w odległości 1 pól
        mimicry=1 #0, 0.25 0.5 0.75 1 zrobić 5 powtórzeń na wartość
        neighbors=self.model.grid.get_neighbors(self.pos, True, True, 3) 
        affected=['ZainfekowanyLimfocytB', 'Neuron', 'Myelin'] #lista typów agentów na które działa efekt cytotoksyczny
        x=randint(1,1000)
        for agent in neighbors:
            if agent.type in affected:
                #warunek ten odnosi się do neuronu, ponieważ może on otrzymać ,,obrażenia",
                #tylko kiedy jest pozbawiony osłonki mielinowej
                if x<=agent.prob_dmg: 
                    if agent.type=="Myelin":
                        agent.health-=1+(math.floor(self.model.cytokina))*10*mimicry
                    else:
                        agent.health-=1+(math.floor(self.model.cytokina/10))

                    if agent.health<0:
                        agent_health=0;
                    self.action_count+=1
                    self.model.B+=1

    def direction(self):
        point=self.attraction_point()
        dest_vector=np.array(np.asarray(point))
        org_vector=np.array(np.asarray(self.pos))
        direct=dest_vector-org_vector
        direct=direct*(-1)
        for i in range(0,2):
            if direct[[i]]<0:
                direct[[i]]=-1
            if direct[[i]]==0:
                direct[[i]]=0
            if direct[[i]]>0:
                direct[[i]]=1


        #print("Vector "+str(direct))
        #disquared= np.square(direct)
        #G=6
        #magnitude=G/disquared
        return direct
    def attraction_point(self):
        rad=5
        point_contents=[]
        neighbors=self.model.grid.get_neighborhood(self.pos,moore=True, include_center=False, radius=rad)
        point=self.random.choice(neighbors)
        for cell in neighbors:
            cell_contents=self.model.grid.get_cell_list_contents(cell)
            if len(cell_contents)>=len(point_contents):
                point=cell
                point_contents=self.model.grid.get_cell_list_contents(point)
        return point

    
class Neuron(Agent):
    def step(self):
        #fragment odpowiadający za sprawdzenie ile żywych komórek mielinowych znajduje się przy neuronie w danym momencie
        neighbors=self.model.grid.get_neighbors(self.pos, True, False,1)
        m=0
        for agent in neighbors:
            if agent.type=='Myelin':
                m+=1
        self.myelin_number=m
        self.prob_dmg= 1000 - (m*125)
        #print("myelin_number: "+str(self.myelin_number))
        self.regeneracja()
        self.death()
    def regeneracja(self):
        #print("Regeneracja")
        neighborhood=self.model.grid.get_neighborhood(self.pos, True, False,1)
        no_myelin= True
        max_regeneration=8#tyle osłonek mielinowych może być zregenerowanych w jednym kroku
        #prob=100-self.model.cytokina
        #x=randint(1,100)
        for cell in neighborhood:
            contents=self.model.grid.get_cell_list_contents(cell)
            for agent in contents:
                if agent.type=="Myelin":
                    no_myelin=False
                    agent.health=min(100,agent.health+self.health)
            if no_myelin:
                max_regeneration-=1
                if max_regeneration>=0:
                    self.addMyelin(self, cell)
                    print("cell"+ str(cell))

                

    def addMyelin(self, x,y):
        #regeneration_rate=100-math.floor(self.model.cytokina/10)
        print("Add myelin")
        #health=10-math.floor(self.regeneration_counter/2)
        health=10*self.health
        regeneration_rate=100
        x=randint(1,100)
        if x<=regeneration_rate:
            if len(self.model.available_ids)==0:
                self.model.max_id+=1
                id=self.model.max_id
            else:
                id=min(self.model.available_ids)
                self.model.available_ids.remove(id)

            n=Myelin(id,self.model,"Myelin")
            print("x:"+str(x)+"y:"+str(y))
            n.pos=y
            n.health=health
            self.model.new_agents.add(n)
            self.regeneration_counter+=1
            if self.model.B>=1:
                self.model.B-=1








class LimfocytB(Agent):
    def step(self):
        #self.proliferation_rate+=math.floor(self.model.cytokina/100)
        #print("proliferation_rate"+str(self.proliferation_rate))
        self.proliferation_rate+=1
        self.action_count=0
        if self.health<1:
            self.death()
        else:
            self.move()
            virus_activation_rate=5
            x=randint(1,100)
            if x<=virus_activation_rate:
                self.aktywacja_wirusa()
            else:
                self.proliferation()
        
    def aktywacja_wirusa(self): #funckaj która zmienia LimfocytB z zainfekowanyLimfocytB
        x=[False,False,False]
        if [self.activated,self.dead, self.infected]==x:
            self.model.max_id+=1
            id=self.model.max_id
            n=ZainfekowanyLimfocytB(id, self.model, "ZainfekowanyLimfocytB")#jak i od zainfekowanego limfocyta B
            n.pos=self.pos
            self.model.new_agents.add(n)
            self.model.dead_agents.add(self)
            #self.action_count+=1
            self.infected=True
            self.dead=True

    def activate(self):
        d=[True, True]
        x=[False,False,False, True]
        #if (self.activation_matrix==d) and (self.action_count==0) and (self.activated==False) and (self.dead==False): #sprawdzamy czy otrzymano bodźce zarówno od Limfocyta T 
        if [self.activated,self.dead, self.infected, self.activation_matrix==d]==x:
            n=AktywowanyLimfocytB(self.unique_id, self.model, "AktywowanyLimfocytB")#jak i od zainfekowanego limfocyta B
            n.pos=self.pos
            self.model.new_agents.add(n)
            self.model.dead_agents.add(self)
            #self.action_count+=1
            self.activated=True
            self.dead=True

class ZainfekowanyLimfocytB(Agent):
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
            neighbors=self.model.grid.get_neighbors(self.pos,True, False, 2)
            for agent in neighbors:
                if agent.type=="LimfocytT":
                    agent.activate()
                    self.action_count+=1 
                if agent.type=="LimfocytB":
                    agent.activation_matrix[0]=True
                    agent.activate()
                    self.action_count+=1
                    #możliwe że zmienna action_count powinna się zwiększać zgodnie z ilością aktytowanych agentów
class AktywowanyLimfocytB(LimfocytB):
    def step(self):
        #self.proliferation_rate=1+math.floor(self.model.cytokina/10)
        #self.proliferation_rate=0
        if self.health<1:
            self.death()
        else:
            self.wspomaganie_LimfocytT()
            self.move()
            self.proliferation()
    def wspomaganie_LimfocytT(self): #funkcja wspomagająca proliferację LimfocytówT, 
        support_rate=1+math.floor(self.model.cytokina/10)
        x=randint(1,10)
        if x<=support_rate:
            neighbors=self.model.grid.get_neighbors(self.pos,True, False, 2)
            for agent in neighbors:
                if agent.type=="LimfocytT":
                    agent.proliferation_rate+=1
                    self.action_count+=1
        
class LimfocytT(Agent):
    def step(self):
        if self.health<1:
            self.death()
        else:
            self.move()
            self.proliferation()
        #print("Agent: "+self.type+" Health: "+str(self.health))
    def activate(self):
        x=[False,False]
        if [self.activated,self.dead]==x:
            n=AktywowanyLimfocytT(self.unique_id, self.model, "AktywowanyLimfocytT")
            n.pos=self.pos
            self.model.new_agents.add(n)
            self.model.dead_agents.add(self)
            self.action_count+=1
            self.activated=True
            self.dead=True
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
        activation_rate=2+math.floor(self.model.cytokina/2)
        x=randint(1,10)
        if x<=activation_rate:
            neighbors=self.model.grid.get_neighbors(self.pos,True, True, 1)
            for agent in neighbors:
                if agent.type=="LimfocytB":
                    agent.activation_matrix[1]=True
                    agent.activate()
                self.action_count+=1
class LimfocytTreg(Agent):
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
                    if agent.health<0:
                        agent.health=0
                    #self.proliferation_rate+=1
                    #self.action_count+=1
                    if self.model.B>=1 :
                        self.model.B-=1
                    
class Myelin(Agent):
    def step(self):
        self.death()

        

class Model(Model):
    def __init__(self, N, B, T, Treg, width,height):
        self.num_myelin=N*8
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
        self.cytokina=0
        self.cytokina_prev=0
        self.sum=0
        self.B=0
        self.a=0.80
        self.Ymax=100
        open('new_and_dead.txt', 'w').close()
        # Create agents
        neuron_positions=[
                            [3,3], [3,10], [3,20], [3,27],
                            [10,3],[10,10],[10,20],[10,27],
                            [19,3],[19,10],[19,20],[19,27],
                            [26,3],[26,10],[26,20],[26,27],
                            [14,15]]
        for i in range(self.num_neurons):
            a = Neuron(i, self,"Neuron")
            self.schedule.add(a)
            #Add agent to a random grid cell
            #x=self.random.randrange(self.grid.width)
            #y=self.random.randrange(self.grid.height)
            #self.grid.place_agent(a,(x,y))
            pos=neuron_positions[i]
            self.grid.place_agent(a,(pos[0], pos[1]))
            cells=self.grid.get_neighborhood(a.pos, True, False, 1)
            id=self.num_agents-i*8
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
        
        self.datacollector_myelin_population=DataCollector(
            model_reporters={"Populacja osłonek mielinowych": myelin_population})

        self.datacollector_myelin_healths=DataCollector(
            model_reporters={"Suma punktów życia osłonek mielinowych": myelin_healths})

    def step(self):
        #print("self running: "+str(self.running()))


        self.schedule.step()
        self.datacollector_population.collect(self)
        self.datacollector_T_population.collect(self)
        #self.datacollector_T_precentage.collect(self)
        self.datacollector_B_population.collect(self)
        self.datacollector_Treg_population.collect(self)
        self.datacollector_B_active_population.collect(self)
        self.datacollector_T_active_population.collect(self)
        self.datacollector_B_infected_population.collect(self)
        self.datacollector_myelin_population.collect(self)
        self.datacollector_myelin_healths.collect(self)
        self.adding_removing()

        self.datacollector_myelin_healths.get_model_vars_dataframe().to_csv(r'Data/myelin_healths25.txt', sep=' ', mode='w')
        self.datacollector_T_population.get_model_vars_dataframe().to_csv(r'Data/T_population25.txt', sep=' ', mode='w')
        self.datacollector_B_population.get_model_vars_dataframe().to_csv(r'Data/B_population25.txt', sep=' ', mode='w')
        self.datacollector_Treg_population.get_model_vars_dataframe().to_csv(r'Data/Treg_population25.txt', sep=' ', mode='w')
        self.datacollector_B_active_population.get_model_vars_dataframe().to_csv(r'Data/B_active_population25.txt', sep=' ', mode='w')
        self.datacollector_T_active_population.get_model_vars_dataframe().to_csv(r'Data/T_active_population25.txt', sep=' ', mode='w')
        self.datacollector_B_infected_population.get_model_vars_dataframe().to_csv(r'Data/B_infected_population25.txt', sep=' ', mode='w')


        print("Liczba agentów: " + str(self.num_agents))
        print("MaxID: " + str(self.max_id))
        
        
        self.cytokina=max(min((self.B+self.cytokina_prev), self.Ymax)*self.a,0)

        print("Cytokina "+str(self.cytokina))
        print("Cytokina_prev "+str(self.cytokina_prev))



        f=open("agents.txt", 'a')
        f.write("======Step : "+str(self.step_count)+"\n")
        for agent in self.schedule.agents:
            f.write("Agent: "+str(agent.type)+" "+str(agent.unique_id)+str(agent.pos)+"\n")

        f.close()
        self.cytokina_prev=self.cytokina
        self.B=0

    def running(self):
        self.step()

    def adding_removing(self): #funckja odpowiedzialna za dodawanie i usuwanie agentów
        #print("AddingRemoving")
        f=open("new_and_dead.txt", 'a')
        f.write("Step " + str(self.step_count) +"\n")
        f.write("======Dead agents======: "+"\n")
        for d in self.dead_agents:
            try:
                self.schedule.remove(d)
                self.num_agents-=1
                self.available_ids.add(d.unique_id)
            except KeyError:
                continue
            try:
                self.grid._remove_agent(d.pos,d)
            except KeyError:
                continue
            f.write(str(d.unique_id) +" " + d.type +"\n")
            #if d.type=="AktywowanyLimfocytT":
            #    self.cytokina-=1
        self.dead_agents.clear()
        f.write("======New Agents=====: " +"\n")
        for n in self.new_agents:
            self.schedule.add(n)
            self.num_agents+=1
            self.grid.place_agent(n, n.pos)
            if n.unique_id in self.available_ids:
                self.available_ids.remove(n.unique_id)
            f.write(str(n.unique_id) + " " + n.type +"\n")
            #if n.type=="AktywowanyLimfocytT":
            #   self.cytokina+=1
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
            self.num_agents+=1
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
                self.num_agents+=1
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
            self.num_agents+=1