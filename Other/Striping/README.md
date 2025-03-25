# Striping scripts for NDGs netlab.
## Ryan's updated script for five hosts and two datastores per host

- First edit pc_clone_spec.json to match your netlab hosts.
- Then change the variables in command given at the bottom of Pod_striping.py to match the pods your are cloning.
- make sure to turn replacements to false if you are not trying to update/replace old pods.

## David's original scripts (three hosts, single datastore per host)
https://github.com/cenobyter/NETLABve


## Netlab striping app (WIP!)
<img width="1189" alt="apppreview" src="https://github.com/user-attachments/assets/3efbd329-6d0b-4dac-9afa-4156d74a0e6a" />

Both scripts need to be heavliy edited to work with each netlab (hosts, datastores, etc). The goal with this app is to allow anyone to clone pods after filling out an options window. Those settings will be saved for the next time the app is used. 
