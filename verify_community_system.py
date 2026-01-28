from staps_core import staps_timed, STAPS_MULTIPLIER, get_staps_coordinate
import time

class MockCommunitySystem:
    def __init__(self):
        self.residents = {"Resident A": {"balance": 100, "vouchers": []}}
        self.merchants = {"Merchant X": {"templates": ["Coffee Voucher"]}}
        self.delivery_pool = []

    @staps_timed
    def purchase_voucher(self, resident_name, voucher_name, cost):
        print(f" > Processing purchase: {resident_name} buying {voucher_name} for {cost} coins")
        if self.residents[resident_name]["balance"] >= cost:
            self.residents[resident_name]["balance"] -= cost
            self.residents[resident_name]["vouchers"].append(voucher_name)
            return True
        return False

    @staps_timed
    def create_delivery_order(self, resident_name, pickup, delivery):
        print(f" > Creating delivery order for {resident_name}")
        order_id = get_staps_coordinate(f"{resident_name}-{time.time()}")[:8]
        order = {"id": order_id, "from": pickup, "to": delivery, "status": "pending"}
        self.delivery_pool.append(order)
        return order_id

    @staps_timed
    def merchant_redeem_voucher(self, qr_code):
        print(f" > Validating QR Code: {qr_code}")
        # Simulation of O(1) lookup via STAPS
        coordinate = get_staps_coordinate(qr_code)
        print(f" > CNS Routing to coordinate: {coordinate}")
        return True

    @staps_timed
    def complete_delivery(self, order_id, volunteer_name):
        print(f" > Completing delivery {order_id} by {volunteer_name}")
        # Award coins
        if volunteer_name not in self.residents:
            self.residents[volunteer_name] = {"balance": 0, "vouchers": []}
        self.residents[volunteer_name]["balance"] += 10
        return True

def run_verification():
    print("=== Double J Community Ecosystem Verification ===")
    system = MockCommunitySystem()

    # 1. Resident purchases voucher
    system.purchase_voucher("Resident A", "Coffee Voucher", 20)

    # 2. Resident requests delivery
    system.create_delivery_order("Resident A", "Central Plaza", "Block B, Room 302")

    # 3. Merchant validates voucher
    system.merchant_redeem_voucher("v-code-12345")

    # 4. Volunteer completes delivery and earns coins
    order_id = system.delivery_pool[0]["id"]
    system.complete_delivery(order_id, "Volunteer B")

    print("\n=== System Status ===")
    print(f"Resident A Balance: {system.residents['Resident A']['balance']} Coins")
    print(f"Volunteer B Balance: {system.residents['Volunteer B']['balance']} Coins")
    print(f"Delivery Orders Pending: {len(system.delivery_pool)}")
    print("================================================")

if __name__ == "__main__":
    run_verification()
