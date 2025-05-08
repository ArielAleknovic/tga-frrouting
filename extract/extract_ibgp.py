import docker
import os
client = docker.from_env()

routers = ['r1', 'r2', 'r3', 'r4']
commands = {
    'bgp_summary': 'vtysh -c "show bgp ipv4 unicast summary"',
    'bgp_routes': 'vtysh -c "show bgp ipv4 unicast"'
}


output_dir = 'outputs_bgp'
os.makedirs(output_dir, exist_ok=True)


for router in routers:
    try:
        container = client.containers.get(router)
        for cmd_name, cmd in commands.items():
            exec_log = container.exec_run(cmd, stdout=True, stderr=True, demux=True)
            stdout, stderr = exec_log.output
            output = ''
            if stdout:
                output += stdout.decode()
            if stderr:
                output += stderr.decode()
            filename = f"{output_dir}/{router}_{cmd_name}.txt"
            with open(filename, 'w') as file:
                file.write(output)
            print(f"Saída do comando '{cmd_name}' do roteador '{router}' salva em '{filename}'.")
    except Exception as e:
        print(f"Erro ao processar o roteador '{router}': {e}")

routers = ['r1', 'r2', 'r3', 'r4']
ips = ["10.0.4.4", "10.0.3.3", "10.0.3.2","10.0.1.11"]

output_dir = 'outputs'
os.makedirs(output_dir, exist_ok=True)
for source in routers:
    try:
        container = client.containers.get(source)
        for target in ips:
            if source == target:
                continue
            cmd = f'ping -c 4 {target}'
            exec_log = container.exec_run(cmd, stdout=True, stderr=True, demux=True)
            stdout, stderr = exec_log.output
            output = ''
            if stdout:
                output += stdout.decode()
            if stderr:
                output += stderr.decode()
            filename = f"{output_dir}/{source}_ping_{target}.txt"
            with open(filename, 'w') as file:
                file.write(output)
            print(f"Resultado do ping de '{source}' para '{target}' salvo em '{filename}'.")
    except Exception as e:
        print(f"Erro ao processar o roteador '{source}': {e}")
