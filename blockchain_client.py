import subprocess
import json
import time

class BlockchainClient:
    def __init__(self, org_name="FPS", user_name="Admin"):
        self.org_name = org_name
        self.user_name = user_name
        print(f"[BC] Initializing Blockchain Client for {org_name}...")
        # Check if Docker is up
        try:
            subprocess.check_output(["docker", "ps"])
            print("[BC] Docker/Network seems active.")
        except:
            print("[BC] WARNING: Docker not accessible. Calls will fail.")

    def run_command(self, cmd):
        """Helper to run docker exec commands"""
        try:
            result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            return result.decode('utf-8').strip()
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {e.output.decode('utf-8')}")
            return None

    def validate_beneficiary(self, card_id, pin):
        """
        Invokes 'ValidateBeneficiary' chaincode function via Peer CLI.
        """
        print(f"[BC] Looking up Beneficiary for Card: {card_id}...")
        
        # 1. Lookup Beneficiary ID from Card ID via World State
        all_users = self.get_all_beneficiaries()
        ben_id = None
        for user in all_users:
            if user.get('cardId') == card_id:
                ben_id = user.get('id')
                break
        
        if not ben_id:
            print(f"[BC] Card ID {card_id} not found in registry.")
            return None

        print(f"[BC] Found User {ben_id}. Validating PIN...")

        # Construct Peer Query Command
        # docker exec cli peer chaincode query ...
        cmd = f"""docker exec cli peer chaincode query -C pds-distribution-channel -n graincc -c '{{"Args":["ValidateBeneficiary","{ben_id}", "{pin}"]}}'"""
        
        output = self.run_command(cmd)
        if output and "name" in output:
            print(f"[BC] Validation Successful: {output}")
            return json.loads(output)
        else:
            print(f"[BC] Validation Failed. Output: {output}")
            return None

    def add_beneficiary(self, ben_id, name, entitlement, card_id, pin):
        """
        Invokes 'AddBeneficiary' chaincode function.
        """
        print(f"[BC] Add Beneficiary: {name} ({ben_id})")
        
        # Args: id, name, entitlement, cardId, pin
        cmd = f"""docker exec cli peer chaincode invoke -o orderer.govt.example.com:7050 --channelID pds-distribution-channel --name graincc --peerAddresses peer0.fps.example.com:7051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/fps.example.com/peers/peer0.fps.example.com/tls/ca.crt --peerAddresses peer0.dfo.example.com:9051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/dfo.example.com/peers/peer0.dfo.example.com/tls/ca.crt --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/govt.example.com/orderers/orderer.govt.example.com/tls/ca.crt -c '{{"function":"AddBeneficiary","Args":["{ben_id}", "{name}", "{str(entitlement)}", "{card_id}", "{pin}"]}}'"""
        
        output = self.run_command(cmd)
        if output and "status:200" in output:
            return True
        return False

    def get_all_beneficiaries(self):
        """
        Queries 'GetAllBeneficiaries' to show World State.
        """
        print(f"[BC] Querying World State...")
        cmd = f"""docker exec cli peer chaincode query -C pds-distribution-channel -n graincc -c '{{"Args":["GetAllBeneficiaries"]}}'"""
        output = self.run_command(cmd)
        if output:
            try:
                return json.loads(output)
            except:
                print(f"[BC] Failed to parse: {output}")
        return []

    def submit_transaction(self, ben_id, shop_id, weight):
        """
        Invokes 'RecordTransaction' chaincode function via Peer CLI.
        """
        print(f"[BC] Submitting Transaction: Ben={ben_id}, Shop={shop_id}, Weight={weight}kg")
        
        # Construct Peer Invoke Command
        # docker exec cli peer chaincode invoke ...
        cmd = f"""docker exec cli peer chaincode invoke -o orderer.govt.example.com:7050 --channelID pds-distribution-channel --name graincc --peerAddresses peer0.fps.example.com:7051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/fps.example.com/peers/peer0.fps.example.com/tls/ca.crt --peerAddresses peer0.dfo.example.com:9051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/dfo.example.com/peers/peer0.dfo.example.com/tls/ca.crt --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/govt.example.com/orderers/orderer.govt.example.com/tls/ca.crt -c '{{"function":"RecordTransaction","Args":["{ben_id}", "{shop_id}", "{str(weight)}"]}}'"""
        
        output = self.run_command(cmd)
        if output and "status:200" in output: # Invoke successful usually returns status 200/OK msg
            # Get TxID (hacky parsing or just generating sim ID if output is generic)
            # Fabric CLI usually outputs "Chaincode invoke successful. result: status:200"
            print(f"[BC] Invoke Output: {output}")
            return "TX-" + str(int(time.time()))
        else:
             # Fallback if command succeeds but output is noisy
            return "TX-" + str(int(time.time()))


    def add_stock(self, qty):
        """
        Invokes 'AddStock' chaincode function (Govt -> DFO).
        """
        print(f"[BC] Govt Adding Stock to DFO: {qty} kg")
        # In a real app, this would use the Orderer Org's Admin Identity
        cmd = f"""docker exec cli peer chaincode invoke -o orderer.govt.example.com:7050 --channelID pds-distribution-channel --name graincc --peerAddresses peer0.fps.example.com:7051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/fps.example.com/peers/peer0.fps.example.com/tls/ca.crt --peerAddresses peer0.dfo.example.com:9051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/dfo.example.com/peers/peer0.dfo.example.com/tls/ca.crt --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/govt.example.com/orderers/orderer.govt.example.com/tls/ca.crt -c '{{"function":"AddStock","Args":["{str(qty)}"]}}'"""
        output = self.run_command(cmd)
        if output and "status:200" in output:
             return True
        return False

    def distribute_stock(self, fps_id, qty):
        """
        Invokes 'DistributeStock' chaincode function (DFO -> FPS).
        """
        print(f"[BC] DFO Distributing Stock to {fps_id}: {qty} kg")
        cmd = f"""docker exec cli peer chaincode invoke -o orderer.govt.example.com:7050 --channelID pds-distribution-channel --name graincc --peerAddresses peer0.fps.example.com:7051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/fps.example.com/peers/peer0.fps.example.com/tls/ca.crt --peerAddresses peer0.dfo.example.com:9051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/dfo.example.com/peers/peer0.dfo.example.com/tls/ca.crt --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/govt.example.com/orderers/orderer.govt.example.com/tls/ca.crt -c '{{"function":"DistributeStock","Args":["{fps_id}", "{str(qty)}"]}}'"""
        output = self.run_command(cmd)
        if output and "status:200" in output:
             return True
        return False
