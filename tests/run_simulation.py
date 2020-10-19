from collections import namedtuple
import gym,os
from sys import argv
# import pandas as pd
from simglucose.controller.basal_bolus_ctrller import BBController
from simglucose.controller.pid_ctrller import PIDController

Observation = namedtuple('Observation', ['CGM'])
Patient_list=['adult#001','adult#002','adult#003','adult#004','adult#005','adult#006','adult#007','adult#008','adult#009','adult#010', ]


def save_results(path,df,patient_name):
    # df = self.results()
    if not os.path.isdir(path):
        os.makedirs(path)
    filename = os.path.join(path, str(patient_name) + '.csv')
    df.to_csv(filename)

# def Run_simulation():
class Run_simulation(object):

    def __init__(
        self,
        es=None,
        policy=None,
        patient_id=1,
        Initial_Bg=0):
        self.es=es
        self.policy = policy
        self.patient_id=patient_id
        self.Initial_Bg =Initial_Bg
    
        # action1 = env.action_space.new_tensor_variable(
        #     'action',
        #     extra_dims=1,
        # )
        # obs1=env.observation_space.new_tensor_variable('obs',extra_dims=1,)
        # print (qf.get_qval_sym(Observation(CGM=180),action1))
        # for bg in range(120,200):
        #     # print(algo.policy.get_action(Observation(CGM=bg)))
        #     print(es.get_action(1, Observation(CGM=bg), policy) )
    
    @staticmethod
    def run(es=None,policy=None,patient_id=1,Initial_Bg=0):
        # es=self.es[0]
        print(es)
        env = gym.make('simglucose-adult{}-CHO{}-v0'.format(Initial_Bg,patient_id+1))

        ctrller = BBController()
        # ctrller = PIDController(P=0.001, I=0.00001, D=0.001)

        reward = 0
        done = False
        info = {'sample_time': 5,
                'patient_name': 'adult#001',
                'meal': 0}

        observation = env.reset()
        pre_glucose = 0
        pre_rate = 0
        for t1 in range(150):
            t = t1 -30 #wait 30*5=150 minutes
            env.render(mode='human')
            glucose = observation.CGM
            # print(observation)
            glucose_refresh = True 
            rate_refresh = True # update the glucose reading and rate output command


            #Fault injection Hook################
            #glucose:HOOK#

            #hold the glucose value when fresh signal is false
            if glucose_refresh != True:
                glucose = pre_glucose
            #update observation
            if observation.CGM != glucose:
                observation=Observation(CGM=glucose)
                print(observation)

            

            #get the action beased on policy and observation
            # (1) random action
            # action = env.action_space.sample()
            # (2) PID or BB control action
            ctrl_action = ctrller.policy(observation, reward, done, **info)
            action = ctrl_action.basal + ctrl_action.bolus
            # (3) RL or DDPG action     
            # action,_ = policy.get_action(observation)# action = es.get_action(t, observation, policy) #algo.policy.get_action(observation)
            # print(action)
            # print(es.get_action(t, observation, policy))

            #Fault injection Hook################
            #rate:HOOK#
            
            #hold the action value when fresh signal is false
            if rate_refresh != True:
                action = pre_rate

            #take the action
            observation, reward, done, info = env.step(action)
            #update previous glucose and rate value
            pre_glucose = glucose
            pre_rate = action

            # if done:
            #     print("Episode finished after {} timesteps".format(t + 1))
            #     break
        
        # print(env.show_history())
        save_results('./simulation_data/',env.show_history(),Patient_list[patient_id])
        env.close()

# if __name__ == "__main__":
#     Run_simulation(argv[1],argv[2])  