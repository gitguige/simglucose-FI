import os
import os.path
import numpy as np
import time
from sys import argv
from collections import namedtuple
from importlib import reload
from tests.test_rllab import Rigister_patient,test_rllab
import tests.run_simulation



Observation = namedtuple('Observation', ['CGM'])
Patient_list=['adult#001','adult#002','adult#003','adult#004','adult#005','adult#006','adult#007','adult#008','adult#009','adult#010', ]


def insert_fault_code(fileLoc, faultLoc, codeline):
  brk = 0
  bkupFile = fileLoc+'.bkup'
  if os.path.isfile(bkupFile) != True:
    cmd = 'cp ' + fileLoc + ' ' + bkupFile
    os.system(cmd)
  else:
    print('Bkup file already exists!!')

  src_fp = open(fileLoc, 'w')
  bkup_fp = open(bkupFile, 'r')

  for line in bkup_fp:
    src_fp.write(line)
    if brk>0:
      for i in range(1, leadSp+1):
        src_fp.write(' ')
      src_fp.write('else:'+'\n')
      for l in np.arange(brk,len(codeline)):
        for i in range(1, leadSp+3):
          src_fp.write(' ')
        src_fp.write(codeline[l]+'\n')

    brk = 0

    if faultLoc in line:
      print ("injected 888")
      leadSp = len(line) - len(line.lstrip(' ')) # calculate the leading spaces

      for i in range(1, leadSp+1):
        src_fp.write(' ')
      src_fp.write(codeline[0]+'\n')

      for l in np.arange(1,len(codeline)):
        if codeline[l] != 'none\n':
          for i in range(1, leadSp+3):
            src_fp.write(' ')
          src_fp.write(codeline[l]+'\n')
        else:
          brk=l+1
          for i in range(1,3):
            src_fp.write(' ')
          break

  src_fp.close()
  bkup_fp.close()

# def inject_fault(fileName,es,policy):
class FInject(object):

  def __init__(
            self,
            fileName,
            es,
            policy,
            patient_id=1,
            Initial_Bg=0):
    self.fileName =fileName
    self.es = es
    self.policy = policy
    self.patient_id=patient_id
    self.Initial_Bg=Initial_Bg

  def inject_fault(self):
    # global start_time_0
    in_file = self.fileName+'.txt'
    # outfile_path = 'out/'
    sceneLine  = self.fileName.split('_')
    sceneNum = sceneLine[len(sceneLine)-1]

    # # recFaultTime="//fltTime=open(\'out/fault_times.txt\',\'a+\')//fltTime.write(str(time.time())+\'||\')//fltTime.close()"
    # recFaultTime="//fltTime=open(\'out/fault_times.txt\',\'a+\')//fltTime.write(str(_)+\'||\')//fltTime.close()"

    # name_end = 0
    # name_id = []
    # fileNames = os.listdir("./result")
    # #rint("Num of Line",len(fileNames))
    # if len(fileNames) == 0:
    #   name_end = 0
    # else:
    #   for name in fileNames:
    #     name_id.append(int(((name.split('_')[1])).split('.')[0]))
    #   name_end = max(name_id)

    with open(in_file, 'r') as fp:
      print( in_file)
      line = fp.readline() # title line
      tLine = line.split('-')
      hz = tLine[len(tLine)-1].replace('\n','')
      title_num = line.split(':')
      scene_num = title_num[1].split('_')
      title = line.split(':')
      title[1] = title[1].replace('\n','')

      # if os.path.isdir('../output_files/'+title[1]) != True:
      #   os.makedirs('../output_files/'+title[1])

      # hazardFile = open('../output_files/'+title[1]+'/Hazards.txt','w')
      # alertFile = open('../output_files/'+title[1]+'/Alerts.txt','w')
      # summFile = open('../output_files/'+title[1]+'/summary.csv','w')

      # summLine = 'Scenario#,Fault#,Fault-line,Alerts,Hazards,T1,T2,T3\n'
      # summFile.write(summLine)

      # hazardFile.close()
      # alertFile.close()
      # summFile.close()

      # hazardFile = open('../output_files/'+title[1]+'/Hazards.txt','a+')
      # alertFile = open('../output_files/'+title[1]+'/Alerts.txt','a+')
      # summFile = open('../output_files/'+title[1]+'/summary.csv','a')

      line = fp.readline() # fault location line
      lineSeg = line.split('//')
      fileLoc = lineSeg[1]
      faultLoc = lineSeg[2]
      for line in fp:
        # line = line + recFaultTime
        lineSeg = line.split('//')
        startWord = lineSeg[0].split(' ')
        del lineSeg[0]

        if startWord[0]=='fault':
          print("+++++++++++Initial_Bg="+str(self.Initial_Bg)+'//'+title[1]+'//fault '+startWord[1]+"++++++++++++++")

          insert_fault_code(fileLoc, faultLoc, lineSeg)
          # print(os.getcwd())

          # print(self.es.get_action(1, Observation(CGM=180), self.policy))
          # print(self.es)

          # os.system('python3 run_simulation.py  '+self.es + '  ' +self.policy)#+title[1]+' '+startWord[1]) #pass scenario and fault num to the .sh script
         
          
          ##############reload tests.run_simulation and Run_simulation function#######
          # from importlib import reload
          # import tests.run_simulation
          reload(tests.run_simulation)
          from tests.run_simulation import Run_simulation
          ############################################################################


          rs=Run_simulation(
            es=self.es,
            policy=self.policy,
            patient_id=self.patient_id,
            Initial_Bg=self.Initial_Bg)

          #use static method as there is some problem in transmiting parameters using default method
          rs.run(es=self.es,
            policy=self.policy,
            patient_id=self.patient_id,
            Initial_Bg=self.Initial_Bg)

          # cmd = 'rm run_simulation.pyc' 
          # os.system(cmd)

          '''Copy all output files in a common directory'''
          # cmd = 'cp -a ' + outfile_path+'/.' + ' ' + output_dir
          # os.system(cmd)

          patient_name =str(Patient_list[patient_id])
          dir_source = './simulation_data'
          if os.path.isdir(dir_source) == True:
            dir_dest = './simulationCollection/'+ patient_name + '/' +title[1]+'/'+startWord[1]
            if os.path.isdir(dir_dest) != True:
              os.makedirs(dir_dest)
            cmd = 'mv -f {}/{} '.format(dir_source,str(patient_name+'.csv')) + ' ' + dir_dest+'/{}_{}.csv'.format(patient_name,Initial_Bg)
            os.system(cmd)
            # cmd = 'rm -rf ./simulation_data'
            # os.system(cmd)
              
            
      
      print('Fault injection and execution done !!!')
      bkupFile = fileLoc+'.bkup'
      refFile = fileLoc+'.reference'       
      cmd = 'cp ' + fileLoc + ' ' + refFile
      os.system(cmd)
      cmd = 'cp ' + bkupFile + ' ' + fileLoc
      os.system(cmd)
      cmd = 'rm ' + bkupFile
      os.system(cmd)

fault_lib=[
  'fault_library_monitor_V2/scenario_9',
  'fault_library_monitor_V2/scenario_12',
  'fault_library_monitor_V2/scenario_13',
  'fault_library_monitor_V2/scenario_14',
  'fault_library_monitor_V2/scenario_17',
  'fault_library_monitor_V2/scenario_18',
  'fault_library_monitor_V2/scenario_19',
  'fault_library_monitor_V2/scenario_20',
  'fault_library_monitor_V2/scenario_21',
  'fault_library_monitor_V2/scenario_22',

]
Fault_Injection_Enable = False
if __name__ == "__main__":
      
  start_time_0 = time.time()

  # if len(argv)>3:
  #   fi=FInject(argv[1],argv[2],argv[3])
  #   fi.inject_fault()
  # else:
  #   print('Fault library filename is missing, pass the filename as argument')


  for patient_id in range(1):
    for Initial_Bg in range(80,210,20):
      Rigister_patient(patient_id,Initial_Bg)
      #RL controller
      es,policy=test_rllab(patient_id,Initial_Bg)
      # #otherwise
      # es=0
      # policy=0

      #inject fault##############################################
      if Fault_Injection_Enable:
        for fault_item in fault_lib:
          fi=FInject(
              fault_item,
              es=es,
              policy=policy,
              patient_id=patient_id,
              Initial_Bg=Initial_Bg
              )
          fi.inject_fault()

      ###run fault free cases####################################
      else:
        from tests.run_simulation import Run_simulation

        rs=Run_simulation(
          es=es,
          policy=policy,
          patient_id=patient_id,
          Initial_Bg=Initial_Bg)

        #use static method as there is some problem in transmiting parameters using default method
        rs.run(es=es,
          policy=policy,
          patient_id=patient_id,
          Initial_Bg=Initial_Bg)

        #save
        patient_name =str(Patient_list[patient_id])
        dir_source = './simulation_data'
        if os.path.isdir(dir_source) == True:
          dir_dest = './simulationCollection_faultfree1/'+ patient_name
          if os.path.isdir(dir_dest) != True:
            os.makedirs(dir_dest)
          cmd = 'mv -f {}/{} '.format(dir_source,str(patient_name+'.csv')) + ' ' + dir_dest+'/{}_{}.csv'.format(patient_name,Initial_Bg)
          os.system(cmd)
          # cmd = 'rm -rf ./simulation_data'
          # os.system(cmd)

  print('\n\n Total runtime: %f seconds' %(time.time()-start_time_0))

