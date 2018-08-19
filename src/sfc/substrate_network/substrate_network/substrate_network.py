from networkx import networkx as nx
from basic_object import BasicObject
import math
"""
node data structure:

network
sfc_dict = {sfc_id: sfc_object}

route_info
{
    sfc_id : 
        {
            src:  [1, 2, 3],
            vnf1: [3, 4, 5],
            vnf2: [5, 6, 7],
            vnf3: [7, 8 ,9],
            dst:  []
        }        
}

node
{
    cpu_capacity: xx,
    cpu_used: xx,
    cpu_free: xx,
    #vnf_list: [vnfObject]
    sfc_vnf_list: [(sfc_id, vnf),...]
}

"""


class SubstrateNetwork(nx.Graph):
    def __init__(self):
        nx.Graph.__init__(self)
        self.sfc_dict = {}
        self.sfc_route_info = {} # sfc_id, route_info
        self.whole_network_cpu_used = 0
        self.whole_network_bandwidth_used = 0
        self.whole_network_cpu_capacity = 0
        self.whole_network_bandwidth_capacity = 0

    def get_sfc_by_id(self, sfc_id):
        return self.sfc_dict[sfc_id]

    def set_sfc(self, sfc):
        self.sfc_dict[sfc.id] = sfc

    def _get_node_attribute(self, node_id, attr):
        return self.nodes[node_id][attr]

    def _set_node_attribute(self, node_id, **attr):
        self.add_node(node_id, **attr)

    def _reset_node_cpu_capacity(self, node_id, cpu_capacity):
        self.set_node_cpu_capacity(node_id, cpu_capacity)
        self.set_node_cpu_used(node_id, 0)
        # self.set_node_cpu_free(node_id, cpu_capacity)
        self.nodes[node_id]['sfc_vnf_list'] = []

    def init_node_cpu_capacity(self, node_id, cpu_capacity):
        self._reset_node_cpu_capacity(node_id, cpu_capacity)

    def set_node_cpu_capacity(self, node_id, cpu_capacity):
        self._set_node_attribute(node_id, cpu_capacity=cpu_capacity)

    def set_node_cpu_used(self, node_id, cpu_used):
        return self._set_node_attribute(node_id, cpu_used = cpu_used)

    def get_node_cpu_capacity(self, node_id):
        return self._get_node_attribute(node_id, "cpu_capacity")

    def get_node_cpu_used(self, node_id):
        return self._get_node_attribute(node_id, "cpu_used")

    def get_node_cpu_available(self, node_id):
        return self.get_node_cpu_capacity(node_id) - self.get_node_cpu_used(node_id)

    def get_node_sfc_vnf_list(self, node_id):
        return self._get_node_attribute(node_id, "sfc_vnf_list")

    def allocate_cpu_resource(self, node_id, cpu_amount):
        cpu_free = self.get_node_cpu_available(node_id)
        cpu_used = self.get_node_cpu_used(node_id)
        if cpu_amount > cpu_free:
            return False
        else:
            self.set_node_cpu_used(node_id, cpu_used+cpu_amount)
            return True

    def deallocate_cpu_resource(self, node_id, cpu_amount):
        cpu_capacity = self.get_node_cpu_capacity(node_id)
        cpu_free = self.get_node_cpu_available(node_id)
        cpu_used = self.get_node_cpu_used(node_id)
        if cpu_amount > cpu_free:
            return False
        else:
            # self.set_node_cpu_free(node_id, cpu_free+cpu_amount)
            self.set_node_cpu_used(node_id, cpu_used-cpu_amount)
            return True

    def change_node_cpu_capacity(self, node_id):
        pass

    def _set_link_attribute(self, u, v, **attr):
        self.add_edge(u, v, **attr)

    def _get_link_attribute(self, u, v, attr):
        return self.edges[u, v][attr]

    def get_link_bandwidth_capacity(self, u, v):
        return self._get_link_attribute(u, v, 'bandwidth_capacity')

    def get_link_bandwidth_used(self, u, v):
        return self._get_link_attribute(u, v, 'bandwidth_used')

    def get_link_bandwidth_available(self, u, v):
        return self._get_link_attribute(u, v, 'bandwidth_capacity') - self._get_link_attribute(u, v, 'bandwidth_used')

    def reset_bandwidth_capacity(self,u, v, bw_c):
        self.set_link_bandwidth_capacity(u, v, bw_c)
        self.set_link_bandwidth_used(u, v, 0)
        return bw_c

    def init_bandwidth_capacity(self, u, v, bw_c):
        return self.reset_bandwidth_capacity(u, v, bw_c)

    def _reset_bandwidth(self, u, v):
        capacity = self.get_link_bandwidth_capacity(u, v)
        self.set_link_bandwidth_used(u, v, 0)

    def set_link_bandwidth_capacity(self, u, v, bw_c):
        self._set_link_attribute(u, v, bandwidth_capacity=bw_c)

    def set_link_bandwidth_used(self, u, v, bw_u):
        self._set_link_attribute(u, v, bandwidth_used=bw_u)

    def allocate_bandwidth_resource(self, u, v, bw_amount):
        bw_u = self.get_link_bandwidth_used(u, v)
        bw_f = self.get_link_bandwidth_available(u, v)
        if bw_amount > bw_f:
            return False
        else:
            self.set_link_bandwidth_used(u, v, bw_u+bw_amount)
            return True

    def allocate_bandwidth_resource_path(self, path, bw_amount):
        length = len(path)
        for i in range(0, length-1):
            self.allocate_bandwidth_resource(path[i], path[i+1], bw_amount)

    def deallocate_bandwidth_resource(self, u, v, bw_amount):
        bw_c = self.get_link_bandwidth_capacity(u, v)
        bw_u = self.get_link_bandwidth_used(u, v)
        bw_f = self.get_link_bandwidth_available(u, v)
        if bw_amount > bw_f:
            return False
        else:
            self.set_link_bandwidth_used(u, v, bw_u - bw_amount)
            return True

    def deallocate_bandwidth_resource_path(self, path, bw_amount):
        length = len(path)
        for i in range(0, length-1):
            self.deallocate_bandwidth_resource(path[i], path[i+1], bw_amount)

    def get_link_latency(self, u, v):
        return self._get_link_attribute(u, v, 'latency')

    def set_link_latency(self, u, v, bw_l):
        self._set_link_attribute(u, v, latency=bw_l)

    def init_link_latency(self, u, v, bw_l):
        self.set_link_latency(u, v, bw_l)

    def get_neighbours(self, node_id):
        return self.neighbors(node_id)

    def all_shortest_paths(self, weight='latency'):
        r = nx.all_pairs_dijkstra(self, weight=weight)
        print [n for n in r]
        print "This is not realized!"

    def get_shortest_paths(self, src, dst, weight):
        try:
            return nx.shortest_path(self, src, dst, weight=weight)
        except:
            return None

    def get_minimum_latency_path(self, src, dst):
        return self.get_shortest_paths(src, dst, 'latency')

    def get_minimum_available_bandwidth(self, path):
        length = len(path)
        minimum_available_bandwidth = float('inf')
        for i in range(0, length-1):
            available_bandwidth = self.get_link_bandwidth_available(path[i], path[i + 1])
            if available_bandwidth < minimum_available_bandwidth:
                minimum_available_bandwidth = available_bandwidth
        return minimum_available_bandwidth

    def get_single_source_minimum_latency_path(self, src):
        return nx.single_source_dijkstra(self, source=src, cutoff=None, weight='latency')

    def get_shortest_latency_path(self, src, dst):
        try:
            return nx.shortest_path(self, src, dst, weight='latency')
        except:
            print "There is no shortest path!!!!"
            return []

    def deploy_sfc(self, sfc, route_info):
        if not route_info:
            print "route info is None"
            return
        if sfc.id not in self.sfc_dict:
            self.sfc_dict[sfc.id] = sfc
        if sfc.id not in self.sfc_route_info:
            self.sfc_route_info[sfc.id] = route_info
        for vnf_id, path in route_info.items():
            if vnf_id == 'dst':
                self.nodes[sfc.dst.substrate_node]['sfc_vnf_list'].append((sfc.id, sfc.dst))
                continue
            vnf = sfc.get_vnf_by_id(vnf_id)
            self.nodes[path[0]]['sfc_vnf_list'].append((sfc.id, vnf))
        # sfc.start()

    def undeploy_sfc(self, sfc_id):
        # after undeployed sfc, sfc need to be deleted from following dicts
        route_info = self.sfc_route_info[sfc_id]
        sfc = self.sfc_dict[sfc_id]
        # sfc.stop()

        # recovery cpu resources
        # no need to actually modify used and free cpu resource.
        # the substrate network will be updated once the vnf removed from node
        for vnf_id, path in route_info.items():
            if vnf_id == 'dst':
                self.nodes[sfc.dst.substrate_node]['sfc_vnf_list'].remove((sfc_id, sfc.dst))
                continue
            self.nodes[sfc.get_substrate_node(sfc.get_vnf_by_id(vnf_id))]['sfc_vnf_list'].remove((sfc_id, sfc.get_vnf_by_id(vnf_id)))
        self.sfc_route_info.pop(sfc_id, None)
        self.sfc_dict.pop(sfc_id, None)

        # recovery bandwidth resources






    def update_network_state(self):
        self.update_nodes_state()
        self.update_bandwidth_state()

    def update_nodes_state(self):
        for node in self.nodes():
            cpu_used = 0
            for sfc_vnf in self.get_node_sfc_vnf_list(node):
                cpu_used += sfc_vnf[1].get_cpu_request()
            self.set_node_cpu_used(node, cpu_used)
            # cpu_free = self.get_node_cpu_capacity(node) - cpu_used
            # self.set_node_cpu_free(node, cpu_free)
        total_cpu_capacity = 0
        total_cpu_used = 0
        for node in self.nodes():
            total_cpu_used += self.get_node_cpu_used(node)
            total_cpu_capacity += self.get_node_cpu_capacity(node)
        self.whole_network_cpu_used = total_cpu_used
        self.whole_network_cpu_capacity = total_cpu_capacity
        # print self.print_out_nodes_information()

    def update_bandwidth_state(self):
        for edge in self.edges():
            self._reset_bandwidth(edge[0], edge[1])

        for node in self.nodes():
           for sfc_vnf in self.get_node_sfc_vnf_list(node):
               sfc_id = sfc_vnf[0]
               sfc = self.get_sfc_by_id(sfc_id)
               vnf = sfc_vnf[1]
               if vnf.id == 'dst':
                   continue
               route_info = self.sfc_route_info[sfc_id]
               path = route_info[vnf.id]
               self.allocate_bandwidth_resource_path(path, sfc.get_link_bandwidth_request(vnf.id, vnf.next_vnf.id))
        total_bandwidth_used = 0
        total_bandwidth_capacity = 0
        for edge in self.edges():
            total_bandwidth_used += self.get_link_bandwidth_used(edge[0], edge[1])
            total_bandwidth_capacity += self.get_link_bandwidth_capacity(edge[0], edge[1])
        self.whole_network_bandwidth_capacity = total_bandwidth_capacity
        self.whole_network_bandwidth_used = total_bandwidth_used

    def print_out_nodes_information(self):
        for node in self.nodes():
            node_id = node
            cpu_used = self.get_node_cpu_used(node)
            cpu_free = self.get_node_cpu_available(node)
            cpu_capacity = self.get_node_cpu_capacity(node)
            sfc_vnf_list = self.get_node_sfc_vnf_list(node)
            # print "node id:", node_id, ":", "CPU: used:", cpu_used, "free:", cpu_free, "capacity:", cpu_capacity, "vnf", sfc_vnf_list
        # print "total cpu used: ", self.total_cpu_used, "total cpu capacity: ", self.total_cpu_capacity
        print "CPU utilization: ", str(self.whole_network_cpu_used * 1.0 / self.whole_network_cpu_capacity * 100) + '%'

    def print_out_edges_information(self):
        for edge in self.edges():
            cp = self.get_link_bandwidth_capacity(edge[0], edge[1])
            fr = self.get_link_bandwidth_available(edge[0], edge[1])
            ud = self.get_link_bandwidth_used(edge[0], edge[1])
            lt = self.get_link_latency(edge[0], edge[1])
            # print "edge:", edge, ":", "BW: used:", ud, "free:", fr, "capacity:", cp, "latency:", lt
        # print "total bandwidth used: ", self.total_bandwidth_used, "total bandwidth capacity: ", self.total_bandwidth_capacity
        print "Bandwidth utilization: ", str(self.whole_network_bandwidth_used * 1.0 / self.whole_network_bandwidth_capacity * 100) + '%'

    def update(self):
        self.update_network_state()

    def get_cpu_utilization_rate(self):
        self.update()
        return self.whole_network_cpu_used * 1.0 / self.whole_network_cpu_capacity
    def get_bandwidth_utilization_rate(self):
        self.update()
        return self.whole_network_bandwidth_used * 1.0 / self.whole_network_bandwidth_capacity