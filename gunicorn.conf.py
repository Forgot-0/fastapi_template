from prometheus_client import multiprocess


def child_exit(server, worker) -> None:
    multiprocess.mark_process_dead(worker.pid)
