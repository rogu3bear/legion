import os

def get_port(name: str, default: int) -> int:
    try:
        with open('.env.ports') as f:
            for line in f:
                if name in line:
                    return int(line.split('=')[1].strip())
    except:
        pass
    return int(os.getenv(name, default)) 