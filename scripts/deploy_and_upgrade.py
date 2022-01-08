from scripts.helpful_scripts import get_account, encode_function_data, upgrade
from brownie import (
    Box,
    network,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    BoxV2,
)


def main():
    account = get_account()
    print(f"deploying to {network.show_active()}")
    box = Box.deploy({"from": account}, publish_source=True)
    print(box.retrieve())

    proxy_admin = ProxyAdmin.deploy({"from": account}, publish_source=True)

    # initializer = box.store, 1
    box_encoded_initializer_function = encode_function_data()
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {
            "from": account,
            "gas_limit": 1000000,
        },
        publish_source=True,
    )
    print(f"proxy deployed to {proxy}, can now upgrade to v2")
    # call function using proxy
    # assigning proxy addres abi of box contract, as proxy delegating everything to box address
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    proxy_box.store(1, {"from": account})
    print(proxy_box.retrieve())

    # upgrade to V2
    box_v2 = BoxV2.deploy({"from": account}, publish_source=True)
    upgrade_xn = upgrade(account, proxy, box_v2, proxy_admin_contract=proxy_admin)
    upgrade_xn.wait(1)
    print("proxy upgraded")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    proxy_box.increment({"from": account})
    print(proxy_box.retrieve())
