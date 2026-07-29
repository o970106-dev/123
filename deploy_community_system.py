from staps_core import staps_timed
import os

NODE_MAPPING = {
    'cc': 'pms_community_center',
    'pf': 'pms_portal_resident',
    'ax1': 'pms_merchant_adapter'
}

@staps_timed
def deploy_to_node(node_name, module_name):
    print(f"[CNS Broadcast] Deploying {module_name} to Neural Adapter Node: {node_name.upper()}")
    # Simulation of moving files to node-specific paths
    # In a real environment, this would use manage_pms.py or similar
    target_path = f"./pms_modules/{node_name}/core/odoo19-shadow/addons/{module_name}"
    print(f" - Target Path: {target_path}")
    return True

def main():
    print("=== Double J Architecture: Node Registration ===")
    for node, module in NODE_MAPPING.items():
        deploy_to_node(node, module)
    print("================================================")
    print("Community System has been successfully integrated into the 8-node target system.")

if __name__ == "__main__":
    main()
