import asyncio
import random
from collections import deque

class Semaforo:
    """
    Classe que representa um semáforo como um processo.
    """
    _pid_counter = 1  # Classe para gerar PID automaticamente

    def __init__(self, nome, prioridade):
        self.nome = nome
        self.pid = Semaforo._pid_counter
        Semaforo._pid_counter += 1
        self.prioridade = prioridade  # Quanto menor o valor, maior a prioridade
        self.status = 'vermelho'
        self.ciclos = 0  # Contador de quantas vezes foi verde

    def set_status(self, status):
        """
        Atualiza o status do semáforo.
        """
        self.status = status

    def __str__(self):
        """
        Representação do semáforo para exibição.
        """
        return f'PID: {self.pid} | {self.nome}: {self.status.upper()} | Prioridade: {self.prioridade} | Ciclos: {self.ciclos}'

async def controlador(fila, max_ciclos):
    """
    Controla a troca de status dos semáforos conforme prioridade.
    """
    # Ordena a fila inicialmente conforme prioridade
    fila = deque(sorted(fila, key=lambda s: s.prioridade))

    while fila:  # Continua enquanto houver semáforos a serem processados
        semaforo = fila.popleft()  # Pega o primeiro da fila (inicialmente o de maior prioridade)

        # Verifica se já atingiu o número máximo de ciclos
        if semaforo.ciclos >= max_ciclos:
            print(f'{semaforo.nome} atingiu o número máximo de ciclos. Removendo da fila.')
            continue  # Não processa mais esse semáforo

        # Define status para verde e incrementa ciclos
        semaforo.set_status('verde')
        semaforo.ciclos += 1
        mostrar_status(fila, semaforo)
        await asyncio.sleep(5)  # Mantém verde por 5 segundos (para teste)

        # Define status para amarelo
        semaforo.set_status('amarelo')
        mostrar_status(fila, semaforo)
        await asyncio.sleep(2)  # Mantém amarelo por 2 segundos

        # Define status para vermelho
        semaforo.set_status('vermelho')
        mostrar_status(fila, semaforo)

        # Coloca o semáforo de volta no final da fila, se ainda tiver ciclos restantes
        if semaforo.ciclos < max_ciclos:
            fila.append(semaforo)

    print('Todos os semáforos completaram os ciclos. Encerrando o controlador.')



def mostrar_status(fila, atual):
    """
    Exibe o status atual de todos os semáforos.
    """
    estados = [str(atual)] + [str(s) for s in fila]
    print(' | '.join(estados))
    print('-' * 100)

async def main():
    """
    Função principal.
    """
    # Criar semáforos com prioridades aleatórias entre 1 e 10
    semaforos = [
        Semaforo('S1', random.randint(1, 10)),
        Semaforo('S2', random.randint(1, 10)),
        Semaforo('S3', random.randint(1, 10))
    ]

    # Montar a fila
    fila = deque(semaforos)

    max_ciclos = 3  # Para testar mais rápido

    # Iniciar o controlador
    await controlador(fila, max_ciclos)

if __name__ == '__main__':
    asyncio.run(main())
