# MS-model
Multiagent model of demielization in Multiple scleroosis

Zawarte na ten moment typy agentów oraz ich funkcje/interakcje
-Neuron
  -śmierć
-Mielina
  -śmierć
-LimfocytB
  -proliferacja
  -aktywacja wirusa
  -śmierć
-ZainfekowanyLimfocytB
  -zarażanie innych limfocytów B
  -proliferacja
  -śmierć
  -aktywowanie LimfocytówB i LimfocytówT
-AktywowanyLimfocytB
  -proliferacja
  -śmierć
  -wspomaganie proliferacji LimfocytówT
-LimfocytT
  -proliferacja 
  -śmierć
  -aktywacja
-AktywowanyLimfocytT
  -proliferacja
  -śmierć
  -aktywacja Limfocytów B
  -efekt cytotoksyczny
-LimfocytTreg
  -proliferation
  -śmierć
  Pracuję jeszcze nad rozwiązaniem indeksowania przy dodawaniu i usuwaniu agentów. Widzę że problem występuje,
  ponieważ kiedy wizualizacja modelu jest uruchumiona można zaobserwować (zwłaszcza po dłuższym czasie) że istnieją agenty które nie poruszają się,
  a jednak istnieją w ramach modelu. 
