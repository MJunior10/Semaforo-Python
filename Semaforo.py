import asyncio
import random
from collections import deque

class Semaforo:
    """
    Classe que representa um semáforo com nome e status.
    """
    def _init_(self, nome):
        self.nome = nome
        self.status = 'vermelho'
        self.ciclos = 0  # Contador de quantas vezes foi verde

    def set_status(self, status):
        """
        Atualiza o status do semáforo.
        """
        self.status = status

    def _str_(self):
        """
        Representação do semáforo para exibição.
        """
        return f'{self.nome}: {self.status.upper()} (Ciclos: {self.ciclos})'

async def controlador(fila, max_ciclos):
    """
    Controla a troca de status dos semáforos conforme as regras:
    - Verde por 25s
    - Amarelo por 5s
    - Depois passa para o próximo semáforo
    O ciclo continua até que cada semáforo tenha atingido 'max_ciclos' ciclos verdes.
    """
    while True:
        semaforo = fila.popleft()  # Pega o semáforo no início da fila

        # Define status para verde e incrementa ciclos
        semaforo.set_status('verde')
        semaforo.ciclos += 1
        mostrar_status(fila, semaforo)
        await asyncio.sleep(25)  # Mantém verde por 25 segundos

        # Define status para amarelo
        semaforo.set_status('amarelo')
        mostrar_status(fila, semaforo)
        await asyncio.sleep(5)  # Mantém amarelo por 5 segundos

        # Define status para vermelho
        semaforo.set_status('vermelho')
        mostrar_status(fila, semaforo)

        # Coloca o semáforo de volta no final da fila
        fila.append(semaforo)

        # Verifica se todos já atingiram o número máximo de ciclos
        if all(s.ciclos >= max_ciclos for s in fila):
            print('Todos os semáforos completaram os ciclos. Encerrando o controlador.')
            break  # Encerra o loop

def mostrar_status(fila, atual):
    """
    Exibe o status atual de todos os semáforos.
    """
    estados = [str(atual)] + [str(s) for s in fila]
    print(' | '.join(estados))
    print('-' * 80)

async def main():
    """
    Função principal:
    - Cria semáforos
    - Define a fila de execução
    - Inicia o controlador com asyncio
    """
    # Criar os três semáforos
    semaforos = [Semaforo('S1'), Semaforo('S2'), Semaforo('S3')]

    # Escolher aleatoriamente o semáforo inicial
    inicial = random.choice(semaforos)

    # Montar a fila começando pelo escolhido
    fila = deque()
    fila.append(inicial)
    for s in semaforos:
        if s != inicial:
            fila.append(s)

    max_ciclos = 5  # Número de vezes que cada semáforo ficará verde

    # Iniciar o controlador
    await controlador(fila, max_ciclos)

if _name_ == '_main_':
    asyncio.run(main())
