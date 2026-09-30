import psutil

LOCAL_HOSTS = {"127.0.0.1", "::1", "localhost"}

def _is_external(raddr):
    if not raddr:
        return False
    ip = raddr.ip
    return not (ip in LOCAL_HOSTS or ip.startswith("127."))

def external_connections():
    """Every external TCP connection on the whole machine (background apps included)."""
    external = []
    for c in psutil.net_connections(kind="tcp"):
        if c.status == psutil.CONN_ESTABLISHED and _is_external(c.raddr):
            external.append({"pid": c.pid, "local": f"{c.laddr.ip}:{c.laddr.port}",
                             "remote": f"{c.raddr.ip}:{c.raddr.port}"})
    return external

def process_external_connections(pid):
    """External TCP connections belonging to one specific process (and its children)."""
    try:
        parent = psutil.Process(pid)
        pids = {pid} | {c.pid for c in parent.children(recursive=True)}
    except psutil.NoSuchProcess:
        pids = {pid}

    external = []
    for c in psutil.net_connections(kind="tcp"):
        if c.pid in pids and c.status == psutil.CONN_ESTABLISHED and _is_external(c.raddr):
            external.append({"pid": c.pid, "local": f"{c.laddr.ip}:{c.laddr.port}",
                             "remote": f"{c.raddr.ip}:{c.raddr.port}"})
    return external

def sovereignty_check(pid=None):
    """If pid is given, check only that process. Otherwise check the whole machine."""
    ext = process_external_connections(pid) if pid else external_connections()
    return len(ext) == 0, ext

if __name__ == "__main__":
    import os
    my_pid = os.getpid()
    print(f"Checking this Python process (PID {my_pid}) only...\n")
    is_sovereign, ext = sovereignty_check(pid=my_pid)
    print(f"Zero outbound connections from this process: {is_sovereign}")
    for c in ext:
        print(f"  PID {c['pid']}: {c['local']} -> {c['remote']}")

    print(f"\nFor comparison, whole-machine external connections: {len(external_connections())}")
    print("(This will be non-zero on a normal PC — background apps, browser, etc. "
          "The number that matters for the demo is the process-specific one above.)")