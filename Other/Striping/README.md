# Striping scripts for NDGs netlab.
## Ryan's updated script for five hosts and two datastores per host

- First edit pc_clone_spec.json to match your netlab hosts. (clone_vh_id & clone_datastore are critical)
  -    **clone_role** should remain unchanged at "NORMAL"
  
  -    **clone_storage_alloc** should remain unchanged at "ONDEMAND"

  -    **clone_type** should remain unchanged at "LINKED"

  -    **clone_vh_id** is the id for the host, found with the tapi.vm_host_find(ip) function 

  -    **source_snapshot** should be the name of the golden snapshot 

  -    **clone_snapshot** leave the same as source_snapshot

  -    **clone_datastore** change to the name of the hosts datastore you want the clone stored on 


- Then change the variables in command given at the bottom of Pod_striping.py to match the pods your are cloning.
  -    **pod_base** is used to decipher which pod # for the specific set

  -    **parent_pod** is the pod to be cloned

  -    **pod_numbers** is the number of pods to clone out

  -    **pod numbers** will be added in the cloning step from the range utilizing the pod_base

  -    **pod_name_base** is the string that is re-used by all pods

       - **example** pod_name_base="Cyber_Patriots_State_Silver/MiddleSchool_Pod-%02d"     (%02d is a two digit limit, 01-99)

  -    **replacement** is used to define if it is replacing an existing pod set, if true removes old pods

## David's original scripts (three hosts, single datastore per host)
https://github.com/cenobyter/NETLABve


## Netlab striping app (WIP!)

Both scripts need to be heavliy edited to work with each netlab (hosts, datastores, etc). The goal with this app is to allow anyone to clone pods after filling out an options window. Those settings will be saved for the next time the app is used. 

<img width="1189" alt="apppreview" src="https://github.com/user-attachments/assets/3efbd329-6d0b-4dac-9afa-4156d74a0e6a" />

