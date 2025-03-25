import datetime, json
from netlab.sync_client import SyncClient

    #argument usage/definitions
    #pod_base is used to decipher which pod # for the specific set
    #parent_pod is the pod to be cloned
    #pod_numbers is the number of pods to clone out
    #pod numbers will be added in the cloning step from the range utilizing the pod_base
    #pod_name_base is the string that is re-used by all pods
    #filename specifies a json file that contains the pc_clone_specs
    #example pod_name_base="Cyber_Patriots_State_Silver/MiddleSchool_Pod-%02d"
    #replacement is used to define if it is replacing an existing pod set, if true removes old pods

def new_pod_striping(pod_base=None,parent_pod=None,pod_numbers=32,pod_name_base=None,replacement=False):

    #moved variables from function call, to be globals maybe?
    filename="./pc_clone_spec.json"
    set1_1="pc_clone_spec1_1"
    set1_2="pc_clone_spec1_2"
    set2_1="pc_clone_spec2_1"
    set2_2="pc_clone_spec2_2"
    set3_1="pc_clone_spec3_1"
    set3_2="pc_clone_spec3_2"
    set4_1="pc_clone_spec4_1"
    set4_2="pc_clone_spec4_2"
    set5_1="pc_clone_spec5_1"
    set5_2="pc_clone_spec5_2"

    with open(filename, 'r') as f:
        pc_specs=json.load(f)

    #host1 & host2 have single datastore!
    pc_clone_specs1_1 = pc_specs[set1_1][0]
    pc_clone_specs1_2 = pc_specs[set1_1][0]
    pc_clone_specs2_1 = pc_specs[set2_1][0]
    pc_clone_specs2_2 = pc_specs[set2_1][0]
    pc_clone_specs3_1 = pc_specs[set3_1][0]
    pc_clone_specs3_2 = pc_specs[set3_2][0]
    pc_clone_specs4_1 = pc_specs[set4_1][0]
    pc_clone_specs4_2 = pc_specs[set4_2][0]
    pc_clone_specs5_1 = pc_specs[set5_1][0]
    pc_clone_specs5_2 = pc_specs[set5_2][0]

    #pod_set is the range of pod destinations to be cloned to
    pod_set=range(pod_base+1,pod_base+(pod_numbers+1))

    #netlab login
    tapi = SyncClient()

    if replacement:
        #Tack Pods Offline
        for pod in pod_set:
            print("Taking pod "+str(pod)+" offline")
            try:
                tapi.pod_state_change(pod_id=pod,state='OFFLINE')
            except Exception as e:
                print("Pod " +str(pod)+" failed to go offline!")
                print(e)

        #Remove Pods
        for pod in pod_set:
                print("removing pod "+str(pod))
                try:
                    tapi.pod_remove_task(pod_id=pod,remove_vms='DISK')
                except Exception as e:
                     print("Pod " +str(pod)+" failed to remove!")
                     print(e)


    #round robin (5 hosts /w datastore alternation)
    for index, pod in enumerate(pod_set[::5]):
        if index % 2 == 0:
            clone_spec = pc_clone_specs1_1
            print("Creating pod %02d"%(pod-pod_base)+ " on "+str(clone_spec['clone_datastore']))
            print("cloning to host vh id "+str(clone_spec['clone_vh_id']))
            tapi.pod_clone_task(source_pod_id=parent_pod,clone_pod_id=pod,clone_pod_name=pod_name_base%(pod-pod_base),pc_clone_specs=clone_spec)
        else:
            clone_spec = pc_clone_specs1_2
            print("Creating pod %02d"%(pod-pod_base)+ " on "+str(clone_spec['clone_datastore']))
            print("cloning to host vh id "+str(clone_spec['clone_vh_id']))
            tapi.pod_clone_task(source_pod_id=parent_pod,clone_pod_id=pod,clone_pod_name=pod_name_base%(pod-pod_base),pc_clone_specs=clone_spec)

    for index, pod in enumerate(pod_set[1::5]):
        if index % 2 == 0:
            clone_spec = pc_clone_specs2_1
            print("Creating pod %02d"%(pod-pod_base)+ " on "+str(clone_spec['clone_datastore']))
            print("cloning to host vh id "+str(clone_spec['clone_vh_id']))
            tapi.pod_clone_task(source_pod_id=parent_pod,clone_pod_id=pod,clone_pod_name=pod_name_base%(pod-pod_base),pc_clone_specs=clone_spec)
        else:
            clone_spec = pc_clone_specs2_2
            print("Creating pod %02d"%(pod-pod_base)+ " on "+str(clone_spec['clone_datastore']))
            print("cloning to host vh id "+str(clone_spec['clone_vh_id']))
            tapi.pod_clone_task(source_pod_id=parent_pod,clone_pod_id=pod,clone_pod_name=pod_name_base%(pod-pod_base),pc_clone_specs=clone_spec)

    for index, pod in enumerate(pod_set[2::5]):
        if index % 2 == 0:
            clone_spec = pc_clone_specs3_1
            print("Creating pod %02d"%(pod-pod_base)+ " on "+str(clone_spec['clone_datastore']))
            print("cloning to host vh id "+str(clone_spec['clone_vh_id']))
            tapi.pod_clone_task(source_pod_id=parent_pod,clone_pod_id=pod,clone_pod_name=pod_name_base%(pod-pod_base),pc_clone_specs=clone_spec)
        else:
            clone_spec = pc_clone_specs3_2
            print("Creating pod %02d"%(pod-pod_base)+ " on "+str(clone_spec['clone_datastore']))
            print("cloning to host vh id "+str(clone_spec['clone_vh_id']))
            tapi.pod_clone_task(source_pod_id=parent_pod,clone_pod_id=pod,clone_pod_name=pod_name_base%(pod-pod_base),pc_clone_specs=clone_spec)

    for index, pod in enumerate(pod_set[3::5]):
        if index % 2 == 0:
            clone_spec = pc_clone_specs4_1
            print("Creating pod %02d"%(pod-pod_base)+ " on "+str(clone_spec['clone_datastore']))
            print("cloning to host vh id "+str(clone_spec['clone_vh_id']))
            tapi.pod_clone_task(source_pod_id=parent_pod,clone_pod_id=pod,clone_pod_name=pod_name_base%(pod-pod_base),pc_clone_specs=clone_spec)
        else:
            clone_spec = pc_clone_specs4_2
            print("Creating pod %02d"%(pod-pod_base)+ " on "+str(clone_spec['clone_datastore']))
            print("cloning to host vh id "+str(clone_spec['clone_vh_id']))
            tapi.pod_clone_task(source_pod_id=parent_pod,clone_pod_id=pod,clone_pod_name=pod_name_base%(pod-pod_base),pc_clone_specs=clone_spec)

    for index, pod in enumerate(pod_set[4::5]):
        if index % 2 == 0:
            clone_spec = pc_clone_specs5_1
            print("Creating pod %02d"%(pod-pod_base)+ " on "+str(clone_spec['clone_datastore']))
            print("cloning to host vh id "+str(clone_spec['clone_vh_id']))
            tapi.pod_clone_task(source_pod_id=parent_pod,clone_pod_id=pod,clone_pod_name=pod_name_base%(pod-pod_base),pc_clone_specs=clone_spec)
        else:
            clone_spec = pc_clone_specs5_2
            print("Creating pod %02d"%(pod-pod_base)+ " on "+str(clone_spec['clone_datastore']))
            print("cloning to host vh id "+str(clone_spec['clone_vh_id']))
            tapi.pod_clone_task(source_pod_id=parent_pod,clone_pod_id=pod,clone_pod_name=pod_name_base%(pod-pod_base),pc_clone_specs=clone_spec)

    #Bringing new pods online
    for pod in pod_set:
            print("taking pod "+str(pod)+" online")
            tapi.pod_state_change(pod_id=pod,state='ONLINE')

if __name__ == '__main__':
     new_pod_striping(pod_base=19000,parent_pod=119,pod_name_base="IOT_RaspberryPi_Pod-%02d",replacement=False)
     print("done")
