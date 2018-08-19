import sys
import unittest
from src.sfc.substrate_network.substrate_network import SubstrateNetwork

class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.substrate_network = SubstrateNetwork()

    def test_net_node(self):
        self.substrate_network.init_node_cpu_capacity(1, 100)
        self.assertEqual(self.substrate_network.get_node_cpu_capacity(1), 100)
        self.assertEqual(self.substrate_network.get_node_cpu_available(1), 100)
        self.assertEqual(self.substrate_network.get_node_cpu_used(1), 0)
        self.assertTrue(self.substrate_network.allocate_cpu_resource(1, 10))
        self.assertEqual(self.substrate_network.get_node_cpu_capacity(1), 100)
        self.assertEqual(self.substrate_network.get_node_cpu_available(1), 90)
        self.assertEqual(self.substrate_network.get_node_cpu_used(1), 10)
        self.assertFalse(self.substrate_network.allocate_cpu_resource(1, 95))
        self.substrate_network.init_node_cpu_capacity(1, 200)
        self.assertEqual(self.substrate_network.get_node_cpu_capacity(1), 200)
        self.assertEqual(self.substrate_network.get_node_cpu_available(1), 200)
        self.assertEqual(self.substrate_network.get_node_cpu_used(1), 0)

    def test_net_link(self):
        self.substrate_network.init_bandwidth_capacity(1, 2, 100)
        self.assertEqual(self.substrate_network.get_link_bandwidth_capacity(1, 2), 100)
        self.assertEqual(self.substrate_network.get_link_bandwidth_used(1, 2), 0)
        self.assertEqual(self.substrate_network.get_link_bandwidth_available(1, 2), 100)
        self.assertTrue(self.substrate_network.allocate_bandwidth_resource(1, 2, 80))
        self.assertFalse(self.substrate_network.allocate_bandwidth_resource(1, 2, 90))
        self.assertEqual(self.substrate_network.get_link_bandwidth_used(1, 2), 80)
        self.assertEqual(self.substrate_network.get_link_bandwidth_available(1, 2), 20)
        self.substrate_network.init_link_latency(1, 2, 2)
        self.assertEqual(self.substrate_network.get_link_latency(1, 2, ), 2)


if __name__ == '__main__':
    unittest.main()
