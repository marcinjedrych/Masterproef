"""
A simulation of the experiment with 4 state factors. (with 3 decks)

Created on Tue Feb 17 12:11:06 2022
@author: Marcin Jedrych
"""
import numpy as np
import matplotlib.pyplot as plt
#import seaborn as sns
from pymdp import utils
from pymdp.agent import Agent

def changes(H, L):

    verbose = False
    
    D1_names = ['High','Low']
    D2_names = ['High','Low']
    D3_names = ['High', 'Low']
    choice_names = ['Start', 'ChD1', 'ChD2','ChD3']
    
    """ Define `num_states` and `num_factors` below """
    num_states = [len(D1_names), len(D2_names),len(D3_names), len(choice_names)]
    num_factors = len(num_states)
    
    context_action_names = ['Do-nothing']
    choice_action_names = ['Start', 'ChD1', 'ChD2','ChD3']
    
    """ Define `num_controls` below """
    num_controls = [len(context_action_names), len(choice_action_names)]
    
    reward_obs_names = ['Null', 'High', 'Low']
    choice_obs_names = ['Start', 'ChD1', 'ChD2','ChD3']
    
    """ Define `num_obs` and `num_modalities` below """
    num_obs = [len(reward_obs_names), len(choice_obs_names)]
    num_modalities = len(num_obs)
    
    ########
    ##A
    
    A = utils.obj_array( num_modalities )
    
    prob_win1 = [0.6,0.4] # what is the probability of high and low reward for deck1
    prob_win2 = [0.8,0.2] # what is the probability of high and low reward for deck2
    prob_win3 = [0.4,0.6] # what is the probability of high and low reward for deck3
    
    #probabilities according to the generative model
    pH1_G = 0.8 #chance to see high reward if deck 1 is good
    pH1_B = 0.2 #chance to see high reward if deck 1 is bad
    pH2_G = 0.8  #chance to see high reward if deck 2 is good
    pH2_B = 0.2 #chance to see high reward if deck 2 is bad
    pH3_G = 0.8  #chance to see high reward is deck 3 is good
    pH3_B = 0.2 #chance to see high reward if deck 3 is bad
    
    # 3x2x2x2x4 = 96 cells
    A_reward = np.zeros((len(reward_obs_names), len(D1_names), len(D2_names),len(D3_names), len(choice_names)))
    
    # 4x2x2x2x4 = 128 cells
    A_choice = np.zeros((len(choice_obs_names), len(D1_names), len(D2_names),len(D3_names), len(choice_names)))
    
    #with probabilities in each cell
    for choice_id, choice_name in enumerate(choice_names):
        
        if choice_name == 'Start':
    
            A_reward[0,:,:,:,choice_id] = 1.0
    
        elif choice_name == 'ChD1':
            
            for i in range(len(D1_names)):
                for loop in range(len(D1_names)):
                    A_reward[1:,:,i,loop,choice_id] = np.array([[pH1_G,pH1_B],[1-pH1_G,1-pH1_B]])
            
        elif choice_name == 'ChD2':
            
            for i in range(len(D2_names)):
                for loop in range(len(D2_names)):
                    A_reward[1:,i,loop,:,choice_id] = np.array([[pH2_G,pH2_B],[1-pH2_G,1-pH2_B]])
    
        elif choice_name == 'ChD3':
            
            for i in range(len(D3_names)):
                for loop in range(len(D3_names)):
                    A_reward[1:,loop,:,i,choice_id] = np.array([[pH3_G,pH3_B],[1-pH3_G,1-pH3_B]])
    
    A[0] = A_reward
    
    A_choice = np.zeros((len(choice_obs_names), len(D1_names), len(D2_names),len(D3_names), len(choice_names)))
    
    for choice_id in range(len(choice_names)):
    
      A_choice[choice_id, :,:,:, choice_id] = 1.0
    
    A[1] = A_choice
    
    ##B (4 arrays because 4 state factors)
    B = utils.obj_array(num_factors)
    
    B_context1 = np.zeros((len(D1_names), len(D1_names), len(context_action_names))) 
    B_context1[:,:,0] = np.eye(len(D1_names))
    B[0] = B_context1
    
    B_context2 = np.zeros((len(D2_names), len(D2_names), len(context_action_names))) 
    B_context2[:,:,0] = np.eye( len(D2_names))
    B[1] = B_context2
    
    B_context3 = np.zeros((len(D3_names), len(D3_names), len(context_action_names)))
    B_context3[:,:,0] = np.eye( len(D3_names))
    B[2] = B_context3
    
    B_choice = np.zeros((len(choice_names), len(choice_names), len(choice_action_names)))
    
    for choice_i in range(len(choice_names)):
        
      B_choice[choice_i, :, choice_i] = 1.0 ##
    
    B[3] = B_choice
    
    ##C
    from pymdp.maths import softmax
    C = utils.obj_array_zeros([3, 4])
    C[0][1] = H #higher preference for high reward
    C[0][2] = L
    rewval = C[0][1] - C[0][2] #a value for reward
    infoval = 1-rewval #a value for information
    
    ##D     high and low reward equaly likely for all decks in start.
    D = utils.obj_array(num_factors)
    D_context1 = np.array([0.5,0.5])
    D_context2 = np.array([0.5,0.5])
    D_context3 = np.array([0.5,0.5])
    
    D[0] = D_context1
    D[1] = D_context2
    D[2] = D_context3
    
    D_choice = np.zeros(len(choice_names))
    D_choice[choice_names.index("Start")] = 1.0
    D[3] = D_choice
    
    ############################################
    
    my_agent = Agent(A = A, B = B, C = C, D = D)
    
    class omgeving(object):
    
      def __init__(self, context = None):
    
        self.context_names = ['High','Low']
        self.context = context
        self.reward_obs_names = ['Null', 'High', 'Low']
    
      def step(self, action):
    
        if action == "Start": 
          observed_reward = "Null"
          observed_choice   = "Start"
    
        elif action == "ChD1":
          self.context = self.context_names[utils.sample(np.array(prob_win1))]
          observed_choice = "ChD1"
          if self.context == "High":
            observed_reward = "High"
          else:
            observed_reward = "Low"
            
        elif action == "ChD2":
          self.context = self.context_names[utils.sample(np.array(prob_win2))] 
          observed_choice = "ChD2"
          if self.context == "High":
            observed_reward = "High"
          else:
            observed_reward = "Low"
       
        elif action == "ChD3":
          self.context = self.context_names[utils.sample(np.array(prob_win3))]
          observed_choice = "ChD3"
          if self.context == "High":
            observed_reward = "High"
          else:
            observed_reward = "Low"
        
        obs = [observed_reward, observed_choice]
    
        return obs
    
    deck1,deck2,deck3 = [],[],[]
    
    def run_active_inference_loop(my_agent, my_env, T = 5):
    
      """ Initialize the first observation """
      obs_label = ["Null", "Start"]  # agent observes a `Null` reward, and seeing itself in the `Start` location
      obs = [reward_obs_names.index(obs_label[0]), choice_obs_names.index(obs_label[1])]
      print('Initial observation:',obs)
      chosendecks = ["Start"]
      High_or_Low = [obs_label[0]] #will make a list containing whether it is high or low reward on each timepoint (for plotting)
      
      prev_action = 'ChD1'
      changes = 0
      
      for t in range(T):
        #print(obs)
        qs = my_agent.infer_states(obs)  # agent changes beliefs about states based on observation
        print("Beliefs about the decks reward:", qs[0], qs[1], qs[2])
        
        q_pi, efe = my_agent.infer_policies() #based on beliefs agent gives value to actions
        print('EFE for each action:', efe)
        
        ##forced choice trials
        if t < 6:
            choice_action = 'ChD1'
        else:
            chosen_action_id = my_agent.sample_action()   #agent choses action with less negative expected free energy
            #print('chosen action id',chosen_action_id)
        
            movement_id = int(chosen_action_id[3])
            #print("movement id", movement_id)
             
            choice_action = choice_action_names[movement_id]
            print("Chosen action:", choice_action)
            
            #count how many times agent changes action
            if prev_action != choice_action:
                changes += 1
                prev_action = choice_action
            
        obs_label = my_env.step(choice_action) #use step methode in 'omgeving' to generate new observation
        obs = [reward_obs_names.index(obs_label[0]), choice_obs_names.index(obs_label[1])]
    
        print(f'Action at time {t}: {choice_action}')
        print(f'Reward at time {t}: {obs_label[0]}')
        High_or_Low.append(obs_label[0][0])
        print(f'New observation:',choice_action,'&', reward_obs_names[obs[0]] + ' reward', '\n')
        
      return changes
    
    env = omgeving() #environment
    T = 50
        
    changes = run_active_inference_loop(my_agent, env, T = T)
    
    print('value of reward =', rewval) #difference between high and low reward in C[0]
    print('value of information =', infoval) #1- value of reward (probably not correct)
    print('amount of changes =', changes) #amount of times that agent changes it's action/chosing another deck.
    
    #when smaller value of reward/ smaller difference between C[0][1] and C[0][2] --> more changes, more exploration / higher information value
    
    return changes

#high reward value vs small reward value (preferences c matrix)
smallrew, highrew = [], []
for i in range(20):
    C = changes(H = 0.4, L = 0.2) #c matrix probabilities
    C2 = changes(H = 0.8,L = 0.2) #c matrix probabilities
    smallrew.append(C)
    highrew.append(C2)

#histogram of changes
plt.figure(1)
plt.hist(x=smallrew, bins=10, alpha=0.7, rwidth=0.85, label = 'small reward value')
plt.hist(x=highrew, bins=10, alpha=0.7, rwidth=0.85, label = 'big reward value')
plt.grid(axis='y', alpha=0.5)
plt.legend()
plt.xlabel('Changes')
plt.ylabel('Frequency')
plt.title('Exploration vs Exploitation')

#bar chart with mean of changes
plt.figure(2)
mean1 = sum(smallrew)  / len(smallrew)
mean2 = sum(highrew) / len(highrew)
objects = ('Small reward value', 'Big reward value')
Yas = [mean1,mean2]
y_pos = np.arange(len(objects))
plt.bar(y_pos, Yas, align='center', alpha=0.5)
plt.xticks(y_pos, objects)
plt.ylabel('Exploration')
plt.title('Exploration vs Exploitation')
plt.show()


    