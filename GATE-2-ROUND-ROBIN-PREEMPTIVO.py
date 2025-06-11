import asyncio
import random
import time
from collections import deque

# Gate 1: Semáforo Simulation
TEMPO_VERDE_TESTE = 5  # segundos
TEMPO_AMARELO_TESTE = 2  # segundos

class Semaforo:
    """Classe que representa um semáforo como um processo."""
    _pid_counter = 1

    def __init__(self, nome, prioridade):
        self.nome = nome
        self.pid = Semaforo._pid_counter
        Semaforo._pid_counter += 1
        self.prioridade = prioridade
        self.status = 'vermelho'
        self.ciclos = 0

    def set_status(self, status):
        self.status = status

    def __str__(self):
        return (f'PID: {self.pid} | {self.nome}: {self.status.upper()} | '
                f'Prioridade: {self.prioridade} | Ciclos: {self.ciclos}')

def mostrar_status_geral(outros_semaforos_na_fila, semaforo_ativo, etapa=""):
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    print(f"[{timestamp}] {etapa}")
    print(f"  Ativo -> {semaforo_ativo}")
    if outros_semaforos_na_fila:
        print("  Fila de Espera:")
        for i, s in enumerate(outros_semaforos_na_fila, start=1):
            print(f"    {i}. {s}")
    else:
        print("  Fila de Espera: Vazia")
    print("-" * 100)

async def controlador(fila_semaforos, max_ciclos, tempo_verde, tempo_amarelo):
    """
    Controla a troca de status dos semáforos conforme prioridade e ciclo.
    """
    # Ordena inicialmente por prioridade
    lista_ordenada = deque(sorted(list(fila_semaforos), key=lambda s: s.prioridade))
    fila_semaforos.clear()
    for s in lista_ordenada:
        fila_semaforos.append(s)

    print(f"Iniciando controlador. Ordem inicial por prioridade: {[str(s) for s in fila_semaforos]}")
    print("-" * 100)

    while any(s.ciclos < max_ciclos for s in fila_semaforos):
        if not fila_semaforos:
            await asyncio.sleep(0.1)
            continue

        semaforo_atual = fila_semaforos.popleft()
        if semaforo_atual.ciclos >= max_ciclos:
            continue

        print(f"\nProcessando: {semaforo_atual.nome} (PID: {semaforo_atual.pid}) - Ciclo {semaforo_atual.ciclos + 1}/{max_ciclos}")
        # Verde
        semaforo_atual.set_status('verde')
        mostrar_status_geral(list(fila_semaforos), semaforo_atual, "INÍCIO VERDE")
        await asyncio.sleep(tempo_verde)
        # Amarelo
        semaforo_atual.set_status('amarelo')
        mostrar_status_geral(list(fila_semaforos), semaforo_atual, "INÍCIO AMARELO")
        await asyncio.sleep(tempo_amarelo)
        # Vermelho
        semaforo_atual.set_status('vermelho')
        semaforo_atual.ciclos += 1
        mostrar_status_geral(list(fila_semaforos), semaforo_atual, f"FIM CICLO {semaforo_atual.ciclos}")

        if semaforo_atual.ciclos < max_ciclos:
            fila_semaforos.append(semaforo_atual)
            print(f"{semaforo_atual.nome} retorna para o fim da fila.")
        else:
            print(f"{semaforo_atual.nome} atingiu {max_ciclos} ciclos. Removido da simulação.")

        await asyncio.sleep(0.01)

    print("\nTodos os semáforos completaram os ciclos. Encerrando o controlador.")

# Gate 2: Round-Robin preemptivo com prioridades
QUANTUM = 3  # unidades de tempo do round-robin

class Processo:
    def __init__(self, pid, nome, prioridade, burst_time):
        self.pid = pid
        self.nome = nome
        self.prioridade = prioridade
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.arrival_time = 0
        self.start_time = None
        self.completion_time = None

    def __str__(self):
        return (f"PID {self.pid} | {self.nome} | Prio {self.prioridade} | "
                f"Rem {self.remaining_time}/{self.burst_time}")

def simulate_round_robin(processos, quantum):
    max_prio = max(p.prioridade for p in processos)
    filas_proc = {prio: deque() for prio in range(max_prio + 1)}
    for p in processos:
        filas_proc[p.prioridade].append(p)

    time = 0
    cpu_busy = 0
    ordem_log = []

    while any(p.remaining_time > 0 for p in processos):
        for prio in sorted(filas_proc):
            if filas_proc[prio]:
                current = filas_proc[prio].popleft()
                break
        else:
            time += 1
            continue

        if current.start_time is None:
            current.start_time = time

        run = min(current.remaining_time, quantum)
        ordem_log.append((time, current.pid, run, prio))
        current.remaining_time -= run
        time += run
        cpu_busy += run

        if current.remaining_time > 0:
            filas_proc[current.prioridade].append(current)
        else:
            current.completion_time = time

    waiting = {p.pid: (p.completion_time - p.arrival_time - p.burst_time)
               for p in processos}
    turnaround = {p.pid: (p.completion_time - p.arrival_time)
                  for p in processos}
    utilization = cpu_busy / time * 100

    return waiting, turnaround, utilization, ordem_log

async def main():
    # Criar semáforos (Gate 1)
    semaforos = [
        Semaforo('Semaforo Norte', random.randint(1,3)),
        Semaforo('Semaforo Leste', random.randint(1,3)),
        Semaforo('Semaforo Sul', random.randint(1,3)),
        Semaforo('Semaforo Oeste', random.randint(1,3)),
    ]
    print("Semáforos Criados:")
    for s in semaforos:
        print(s)
    print("-" * 100)

    # Gate 2: converter semáforos em processos e simular escalonamento
    processos = [Processo(s.pid, s.nome, s.prioridade, TEMPO_VERDE_TESTE + TEMPO_AMARELO_TESTE) for s in semaforos]
    waiting, turnaround, util, log = simulate_round_robin(processos, QUANTUM)

    print("=== LOG DE ESCALONAMENTO Round-Robin ===")
    for t, pid, run, prio in log:
        print(f"t={t:3d} → PID{pid} rodou {run}u (prio {prio})")

    print("\n=== ESTATÍSTICAS de Escalonamento ===")
    for p in processos:
        print(f"PID {p.pid}: Waiting = {waiting[p.pid]:2d}, Turnaround = {turnaround[p.pid]:2d}")
    print(f"CPU Utilization: {util:.2f}%\n")

    # Gate 1: iniciar controlador original
    fila_principal = deque(semaforos)
    max_ciclos_por_semaforo = 2
    await controlador(fila_principal, max_ciclos_por_semaforo, TEMPO_VERDE_TESTE, TEMPO_AMARELO_TESTE)

if __name__ == '__main__':
    asyncio.run(main())
