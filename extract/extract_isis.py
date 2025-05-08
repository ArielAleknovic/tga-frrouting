import docker
import os


client = docker.from_env()

routers = ['r1', 'r2', 'r3', 'r4']

commands = {
    'isis_summary': 'vtysh -c "show isis summary"',
    'isis_database_detail': 'vtysh -c "show isis database detail"'
    }


output_dir = 'outputs_isis'
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
