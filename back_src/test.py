import subprocess

adres = "fc94:40d4:4574:7b91:da05:db42:45bb:f6ab"

def check_if_conection_p2p(addr):
    result = subprocess.run("sudo husarnet status", capture_output=True, shell=True, text=True)
    start = result.stdout.find("Peer "+addr)
    end = result.stdout.find("Peer ", start)
    if start == -1 or end == -1:
        return False
    found = result.stdout.find("tunnelled", start, end)
    if found == -1:
        return False
    return True


print(check_if_conection_p2p(adres))