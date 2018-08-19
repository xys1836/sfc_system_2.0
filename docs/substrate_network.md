# Substrate Network
## Data structure   

The substrate network data structure is same as graph in networkx. The class SubstrateNetwork extends nx.graph.   

Substrate network node structure:  
a dict contains  
```
{  
    cpu_capacity: int number,  
    cpu_used: int number,    
    sfc_vnf_list: [(sfc_id, vnf),...]    
}    
``` 
Substrate network edge structure:  
a dict contains 
```
{
    bandwidth_capacity: int number,  
    bandwidth_used: int number,    
    latency: int number,
}    
```