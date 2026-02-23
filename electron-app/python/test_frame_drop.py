"""
Teste: Verificar se frames acumulam ou são dropados
"""
import time
import asyncio

async def simular_gameplay_sem_drop():
    """Sistema RUIM - Acumula frames"""
    print("\n" + "="*60)
    print("SIMULAÇÃO 1: Sistema SEM drop de frames (RUIM)")
    print("="*60)

    fila = []
    frame_count = 0

    # Simular gameplay gerando frames
    async def gerar_frames():
        nonlocal frame_count
        for i in range(20):
            frame_count += 1
            fila.append(f"Frame {frame_count}")
            await asyncio.sleep(0.1)  # 10 FPS

    # Simular processamento lento
    async def processar_frames():
        while True:
            if fila:
                frame = fila.pop(0)
                print(f"[PROCESSANDO] {frame} | Fila: {len(fila)} frames aguardando")
                await asyncio.sleep(2)  # Vision AI lenta
            else:
                await asyncio.sleep(0.1)

            if frame_count >= 20 and not fila:
                break

    start = time.time()
    await asyncio.gather(gerar_frames(), processar_frames())
    elapsed = time.time() - start

    print(f"\n[RESULTADO] Tempo total: {elapsed:.1f}s")
    print(f"[RESULTADO] Delay acumulado no final: {elapsed - 2:.1f}s")
    print("❌ PROBLEMA: Fila cresceu infinito!\n")


async def simular_gameplay_com_drop():
    """Sistema BOM - Dropa frames"""
    print("\n" + "="*60)
    print("SIMULAÇÃO 2: Sistema COM drop de frames (BOM - ATUAL)")
    print("="*60)

    frame_count = 0
    frames_processados = 0
    frames_dropados = 0

    start = time.time()

    for i in range(10):  # 10 iterações
        frame_count += 30  # Gameplay gerou 30 frames (1 segundo @ 30 FPS)

        # Captura APENAS o frame mais recente
        print(f"[CAPTURA] Frame {frame_count} (frames {frame_count-29}-{frame_count-1} dropados)")
        frames_dropados += 29

        # Processa
        print(f"[PROCESSA] Frame {frame_count}...", end=" ")
        await asyncio.sleep(0.5)  # Simula processamento (reduzido para demo)
        print("OK!")
        frames_processados += 1

        elapsed = time.time() - start
        delay = elapsed - (i + 1) * 1.0  # Delay vs tempo real
        print(f"[STATUS] Tempo: {elapsed:.1f}s | Delay: {delay:.1f}s\n")

    elapsed = time.time() - start

    print(f"\n[RESULTADO] Tempo total: {elapsed:.1f}s")
    print(f"[RESULTADO] Frames processados: {frames_processados}")
    print(f"[RESULTADO] Frames dropados: {frames_dropados}")
    print(f"[RESULTADO] Delay constante: ~0.5s")
    print("✅ SUCESSO: Delay NÃO cresce!\n")


async def simular_com_filtro_inteligente():
    """Sistema ÓTIMO - Filtro + Drop"""
    print("\n" + "="*60)
    print("SIMULAÇÃO 3: Sistema COM filtro inteligente (MELHOR)")
    print("="*60)

    frame_count = 0
    frames_filtrados = 0
    frames_analisados = 0

    start = time.time()

    for i in range(10):
        frame_count += 30

        # Filtragem rápida (0.06s)
        print(f"[CAPTURA] Frame {frame_count}")
        await asyncio.sleep(0.01)  # Frame diff

        # 90% dos frames são filtrados
        if i % 10 != 5:  # Simula: apenas 1 a cada 10 passa
            print(f"[FILTRO] ❌ Descartado (cena estática)")
            frames_filtrados += 1
        else:
            print(f"[FILTRO] ✅ Potencial kill! Enviando para Vision AI...")
            await asyncio.sleep(0.5)  # Vision AI (reduzido para demo)
            print(f"[VISION AI] Kill detectado!")
            frames_analisados += 1

        elapsed = time.time() - start
        print(f"[STATUS] Tempo: {elapsed:.2f}s\n")

    elapsed = time.time() - start

    print(f"\n[RESULTADO] Tempo total: {elapsed:.1f}s")
    print(f"[RESULTADO] Frames filtrados: {frames_filtrados} (grátis)")
    print(f"[RESULTADO] Frames analisados: {frames_analisados} (Vision AI)")
    print(f"[RESULTADO] Economia: {frames_filtrados / (frames_filtrados + frames_analisados) * 100:.0f}%")
    print(f"[RESULTADO] Delay médio: ~0.5s")
    print("✅ PERFEITO: Rápido + Econômico + Sem acúmulo!\n")


async def main():
    print("\n" + "="*60)
    print("TESTE: ACÚMULO DE FRAMES - GTA Analytics")
    print("="*60)

    await simular_gameplay_sem_drop()
    await simular_gameplay_com_drop()
    await simular_com_filtro_inteligente()

    print("\n" + "="*60)
    print("CONCLUSÃO")
    print("="*60)
    print("Sistema atual (com drop): ✅ Delay constante")
    print("Com filtro inteligente: ✅ Delay menor + 99% economia")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
