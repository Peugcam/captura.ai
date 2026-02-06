"""
Excel Exporter for GTA Battle Royale
=====================================

Exporta dados do jogo para Excel no formato de planilha manual.
Substitui o trabalho de pessoa anotando manualmente.

Author: Paulo Eugenio Campos
Cliente: Luis Otavio
"""

from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ExcelExporter:
    """
    Exportador de dados para Excel.

    Formatos suportados:
    - Formato padrão (genérico)
    - Formato Luis (personalizado conforme planilha dele)
    - Formato avançado (com estatísticas extras)
    """

    def __init__(self):
        """Inicializa o exportador."""
        self.workbook = None
        self.worksheet = None

    def export_match(
        self,
        match_data: Dict,
        filepath: str,
        format: str = 'standard'
    ) -> bool:
        """
        Exporta dados de uma partida para Excel.

        Args:
            match_data: Dados da partida (do GameStateManager)
            filepath: Caminho do arquivo Excel
            format: 'standard', 'luis', ou 'advanced'

        Returns:
            True se exportou com sucesso
        """
        try:
            # Try to import xlsxwriter
            try:
                import xlsxwriter
            except ImportError:
                logger.error("xlsxwriter não instalado. Execute: pip install xlsxwriter")
                return False

            # Create workbook
            workbook = xlsxwriter.Workbook(filepath)

            if format == 'standard':
                self._export_standard(workbook, match_data)
            elif format == 'luis':
                self._export_luis_format(workbook, match_data)
            elif format == 'advanced':
                self._export_advanced(workbook, match_data)

            workbook.close()
            logger.info(f"Match data exported to: {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            return False

    def _export_standard(self, workbook, match_data: Dict):
        """Formato padrão de exportação."""
        worksheet = workbook.add_worksheet("Partida")

        # Formatos
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })

        alive_format = workbook.add_format({
            'bg_color': '#C6EFCE',
            'font_color': '#006100'
        })

        dead_format = workbook.add_format({
            'bg_color': '#FFC7CE',
            'font_color': '#9C0006'
        })

        # Headers
        headers = ['Nome', 'Time', 'Kills', 'Deaths', 'K/D', 'Status', 'Primeira Kill', 'Última Atualização']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        # Largura das colunas
        worksheet.set_column(0, 0, 20)  # Nome
        worksheet.set_column(1, 1, 15)  # Time
        worksheet.set_column(2, 4, 10)  # Kills, Deaths, K/D
        worksheet.set_column(5, 5, 12)  # Status
        worksheet.set_column(6, 7, 20)  # Timestamps

        # Dados dos jogadores
        row = 1
        for team_name, team_data in match_data.get('teams', {}).items():
            for player in team_data.get('players', []):
                # Status format
                status = 'VIVO' if player['alive'] else 'MORTO'
                cell_format = alive_format if player['alive'] else dead_format

                # K/D ratio
                kd = player['kills'] / max(player['deaths'], 1)

                # Write data
                worksheet.write(row, 0, player['name'])
                worksheet.write(row, 1, player['team'] or '?')
                worksheet.write(row, 2, player['kills'])
                worksheet.write(row, 3, player['deaths'])
                worksheet.write(row, 4, f"{kd:.2f}")
                worksheet.write(row, 5, status, cell_format)
                worksheet.write(row, 6, player.get('first_seen', ''))
                worksheet.write(row, 7, player.get('last_seen', ''))

                row += 1

        # Resumo da partida
        summary_worksheet = workbook.add_worksheet("Resumo")

        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'bg_color': '#D9D9D9'
        })

        summary_worksheet.write(0, 0, "RESUMO DA PARTIDA", title_format)
        summary_worksheet.write(2, 0, "Total de Jogadores:")
        summary_worksheet.write(2, 1, match_data.get('total_players', 0))
        summary_worksheet.write(3, 0, "Jogadores Vivos:")
        summary_worksheet.write(3, 1, match_data.get('total_alive', 0))
        summary_worksheet.write(4, 0, "Jogadores Mortos:")
        summary_worksheet.write(4, 1, match_data.get('total_dead', 0))
        summary_worksheet.write(5, 0, "Total de Kills:")
        summary_worksheet.write(5, 1, match_data.get('total_kills', 0))
        summary_worksheet.write(6, 0, "Total de Teams:")
        summary_worksheet.write(6, 1, match_data.get('total_teams', 0))

        # Teams
        row = 9
        summary_worksheet.write(row, 0, "ESTATÍSTICAS POR TIME", title_format)
        row += 2

        for team_name, stats in match_data.get('teams', {}).items():
            summary_worksheet.write(row, 0, f"{team_name}:")
            summary_worksheet.write(row, 1, f"{stats['alive']}/{stats['total']} vivos")
            summary_worksheet.write(row, 2, f"{stats['total_kills']} kills")
            row += 1

    def _export_luis_format(self, workbook, match_data: Dict):
        """
        Formato EXATO do Luis Otavio.

        3 Abas:
        1. VIVOS - Grid de times com checks
        2. RANKING - Leaderboard de kills
        3. KILL FEED - Histórico de mortes
        """
        # ABA 1: VIVOS (formato exato que Luis usa)
        self._create_vivos_sheet(workbook, match_data)

        # ABA 2: RANKING
        self._create_ranking_sheet(workbook, match_data)

        # ABA 3: KILL FEED
        self._create_killfeed_sheet(workbook, match_data)

    def _create_vivos_sheet(self, workbook, match_data: Dict):
        """Aba VIVOS - Grid com checks MELHORADO (baseado no formato Luis)"""
        worksheet = workbook.add_worksheet("VIVOS")

        # 🎨 FORMATOS EXATOS DA PLANILHA DO LUIS
        header_black_yellow = workbook.add_format({
            'bold': True,
            'bg_color': '#000000',  # Preto
            'font_color': '#FFFF00',  # Amarelo
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 13,
            'font_name': 'Arial'
        })

        header_black_green = workbook.add_format({
            'bold': True,
            'bg_color': '#000000',  # Preto
            'font_color': '#00FF00',  # Verde
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 13,
            'font_name': 'Arial'
        })

        team_format = workbook.add_format({
            'bold': True,
            'bg_color': '#000000',  # Preto igual ao header
            'font_color': '#FFFF00',  # Amarelo
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 12,
            'font_name': 'Arial'
        })

        # Check verde para VIVO
        check_alive_format = workbook.add_format({
            'bg_color': '#E8F5E9',  # Verde claro
            'font_color': '#2E7D32',  # Verde escuro
            'border': 2,
            'border_color': '#4CAF50',  # Borda verde
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 18,
            'bold': True
        })

        # X vermelho para MORTO
        check_dead_format = workbook.add_format({
            'bg_color': '#FFEBEE',  # Vermelho claro
            'font_color': '#C62828',  # Vermelho escuro
            'border': 2,
            'border_color': '#EF5350',  # Borda vermelha
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 18,
            'bold': True
        })

        # Vazio (sem jogador)
        check_empty_format = workbook.add_format({
            'bg_color': '#F5F5F5',
            'border': 1,
            'border_color': '#BDBDBD'
        })

        alive_count_format = workbook.add_format({
            'bold': True,
            'bg_color': '#1B5E20',  # Verde escuro
            'font_color': '#00FF00',
            'border': 2,
            'border_color': '#4CAF50',
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 16,
            'font_name': 'Arial'
        })

        # Formato para nomes de jogadores
        player_name_format = workbook.add_format({
            'bg_color': '#F5F5F5',
            'font_color': '#212121',
            'border': 1,
            'border_color': '#BDBDBD',
            'align': 'left',
            'valign': 'vcenter',
            'font_size': 10,
            'font_name': 'Arial'
        })

        # 📋 HEADERS - Nova estrutura com NOMES
        worksheet.write(0, 0, "TIMES", header_black_yellow)
        worksheet.write(0, 1, "JOGADOR 1", header_black_yellow)
        worksheet.write(0, 2, "ST", header_black_yellow)  # Status
        worksheet.write(0, 3, "JOGADOR 2", header_black_yellow)
        worksheet.write(0, 4, "ST", header_black_yellow)
        worksheet.write(0, 5, "JOGADOR 3", header_black_yellow)
        worksheet.write(0, 6, "ST", header_black_yellow)
        worksheet.write(0, 7, "JOGADOR 4", header_black_yellow)
        worksheet.write(0, 8, "ST", header_black_yellow)
        worksheet.write(0, 9, "JOGADOR 5", header_black_yellow)
        worksheet.write(0, 10, "ST", header_black_yellow)
        worksheet.write(0, 11, "VIVOS", header_black_green)

        # 📏 Larguras otimizadas
        worksheet.set_column(0, 0, 12)     # TIMES
        worksheet.set_column(1, 1, 16)     # JOGADOR 1
        worksheet.set_column(2, 2, 4)      # ST 1
        worksheet.set_column(3, 3, 16)     # JOGADOR 2
        worksheet.set_column(4, 4, 4)      # ST 2
        worksheet.set_column(5, 5, 16)     # JOGADOR 3
        worksheet.set_column(6, 6, 4)      # ST 3
        worksheet.set_column(7, 7, 16)     # JOGADOR 4
        worksheet.set_column(8, 8, 4)      # ST 4
        worksheet.set_column(9, 9, 16)     # JOGADOR 5
        worksheet.set_column(10, 10, 4)    # ST 5
        worksheet.set_column(11, 11, 10)   # VIVOS

        # Altura da linha header
        worksheet.set_row(0, 30)

        # 📊 Dados dos times com NOMES e STATUS
        row = 1
        teams = match_data.get('teams', {})

        for team_name, team_data in sorted(teams.items()):
            # Nome do time
            worksheet.write(row, 0, team_name, team_format)

            # Players (até 5) - agora com NOMES
            players = team_data.get('players', [])[:5]

            for i in range(5):
                name_col = 1 + (i * 2)      # Coluna do nome (1, 3, 5, 7, 9)
                status_col = name_col + 1    # Coluna do status (2, 4, 6, 8, 10)

                if i < len(players):
                    player = players[i]
                    player_name = player.get('name', f'Player{i+1}')
                    is_alive = player.get('alive', True)

                    # Nome do jogador
                    worksheet.write(row, name_col, player_name, player_name_format)

                    # Status visual
                    if is_alive:
                        worksheet.write(row, status_col, "✓", check_alive_format)
                    else:
                        worksheet.write(row, status_col, "✗", check_dead_format)
                else:
                    # Slots vazios
                    worksheet.write(row, name_col, "", check_empty_format)
                    worksheet.write(row, status_col, "", check_empty_format)

            # Contador de vivos com destaque
            alive_count = team_data.get('alive', len(players))
            worksheet.write(row, 11, alive_count, alive_count_format)

            worksheet.set_row(row, 28)  # Altura maior para melhor visualização
            row += 1

        # 📝 LEGENDA ao final
        row += 1
        legend_format = workbook.add_format({
            'italic': True,
            'font_size': 9,
            'font_color': '#666666'
        })
        worksheet.write(row, 0, "Legenda:", legend_format)
        worksheet.write(row, 1, "✓ = Vivo", check_alive_format)
        worksheet.write(row, 2, "✗ = Morto", check_dead_format)

    def _create_ranking_sheet(self, workbook, match_data: Dict):
        """Aba RANKING - Leaderboard PROFISSIONAL com destaques"""
        worksheet = workbook.add_worksheet("RANKING")

        # 🎨 FORMATOS
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#000000',
            'font_color': '#FFFF00',
            'border': 2,
            'border_color': '#444444',
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 12,
            'font_name': 'Arial'
        })

        # TOP 1 - OURO
        top1_format = workbook.add_format({
            'bg_color': '#FFD700',  # Dourado
            'font_color': '#000000',
            'border': 2,
            'border_color': '#FFA000',
            'align': 'center',
            'bold': True,
            'font_size': 11
        })

        # TOP 2 - PRATA
        top2_format = workbook.add_format({
            'bg_color': '#C0C0C0',  # Prata
            'font_color': '#000000',
            'border': 2,
            'border_color': '#9E9E9E',
            'align': 'center',
            'bold': True,
            'font_size': 11
        })

        # TOP 3 - BRONZE
        top3_format = workbook.add_format({
            'bg_color': '#CD7F32',  # Bronze
            'font_color': '#FFFFFF',
            'border': 2,
            'border_color': '#A0522D',
            'align': 'center',
            'bold': True,
            'font_size': 11
        })

        # Normal
        data_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'font_size': 10
        })

        # Status cores
        alive_status = workbook.add_format({
            'bg_color': '#C8E6C9',
            'font_color': '#2E7D32',
            'border': 1,
            'align': 'center',
            'bold': True
        })

        dead_status = workbook.add_format({
            'bg_color': '#FFCDD2',
            'font_color': '#C62828',
            'border': 1,
            'align': 'center',
            'bold': True
        })

        # 📋 Headers
        headers = ['🏆', 'JOGADOR', 'TEAM', 'KILLS', 'MORTES', 'K/D', 'STATUS']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        # 📏 Larguras
        worksheet.set_column(0, 0, 6)   # 🏆
        worksheet.set_column(1, 1, 20)  # JOGADOR
        worksheet.set_column(2, 2, 12)  # TEAM
        worksheet.set_column(3, 5, 10)  # KILLS, MORTES, K/D
        worksheet.set_column(6, 6, 12)  # STATUS

        worksheet.set_row(0, 30)

        # 📊 Pega todos os jogadores e ordena por kills
        all_players = []
        for team_data in match_data.get('teams', {}).values():
            all_players.extend(team_data.get('players', []))

        all_players.sort(key=lambda p: p.get('kills', 0), reverse=True)

        # 🏅 Dados com destaques para TOP 3
        for i, player in enumerate(all_players, 1):
            kills = player.get('kills', 0)
            deaths = player.get('deaths', 0)
            kd = kills / max(deaths, 1)
            is_alive = player.get('alive', True)

            # Escolhe formato baseado na posição
            if i == 1:
                row_format = top1_format
                medal = "🥇"
            elif i == 2:
                row_format = top2_format
                medal = "🥈"
            elif i == 3:
                row_format = top3_format
                medal = "🥉"
            else:
                row_format = data_format
                medal = str(i)

            worksheet.write(i, 0, medal, row_format)
            worksheet.write(i, 1, player['name'], row_format)
            worksheet.write(i, 2, player.get('team', '?'), row_format)
            worksheet.write(i, 3, kills, row_format)
            worksheet.write(i, 4, deaths, row_format)
            worksheet.write(i, 5, f"{kd:.2f}", row_format)

            # Status com cores
            status_format = alive_status if is_alive else dead_status
            status_text = '✓ VIVO' if is_alive else '✗ MORTO'
            worksheet.write(i, 6, status_text, status_format)

            # Altura das linhas TOP 3
            if i <= 3:
                worksheet.set_row(i, 28)
            else:
                worksheet.set_row(i, 22)

    def _create_killfeed_sheet(self, workbook, match_data: Dict):
        """Aba KILL FEED - Histórico DETALHADO de kills com cores"""
        worksheet = workbook.add_worksheet("KILL FEED")

        # 🎨 FORMATOS
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#000000',
            'font_color': '#FFFF00',
            'border': 2,
            'border_color': '#444444',
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 12,
            'font_name': 'Arial'
        })

        # Killer (verde - quem matou)
        killer_format = workbook.add_format({
            'bg_color': '#C8E6C9',
            'font_color': '#1B5E20',
            'border': 1,
            'align': 'center',
            'bold': True,
            'font_size': 11
        })

        # Victim (vermelho - quem morreu)
        victim_format = workbook.add_format({
            'bg_color': '#FFCDD2',
            'font_color': '#B71C1C',
            'border': 1,
            'align': 'center',
            'bold': True,
            'font_size': 11
        })

        # Team
        team_format = workbook.add_format({
            'bg_color': '#FFF9C4',
            'font_color': '#F57F17',
            'border': 1,
            'align': 'center',
            'font_size': 10
        })

        # Arrow
        arrow_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'font_size': 14,
            'bold': True,
            'font_color': '#FF0000'
        })

        # Timestamp e outros
        data_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'font_size': 10
        })

        # 📋 Headers
        headers = ['#', 'HORA', '🔫 MATOU', 'TIME', '💀', '☠️ MORREU', 'TIME', 'ARMA']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        # 📏 Larguras
        worksheet.set_column(0, 0, 5)   # #
        worksheet.set_column(1, 1, 12)  # HORA
        worksheet.set_column(2, 2, 18)  # KILLER
        worksheet.set_column(3, 3, 12)  # TEAM KILLER
        worksheet.set_column(4, 4, 5)   # 💀
        worksheet.set_column(5, 5, 18)  # VICTIM
        worksheet.set_column(6, 6, 12)  # TEAM VICTIM
        worksheet.set_column(7, 7, 15)  # ARMA

        worksheet.set_row(0, 30)

        # 📊 Dados dos eventos com cores
        events = match_data.get('recent_events', [])
        row = 1

        kill_number = 1
        for event in events:
            if event.get('event_type') == 'kill':
                data = event.get('data', {})
                timestamp = event.get('timestamp', '')

                # Formata timestamp
                if len(timestamp) > 19:
                    timestamp = timestamp[:19]

                # Número da kill
                worksheet.write(row, 0, kill_number, data_format)

                # Hora
                worksheet.write(row, 1, timestamp, data_format)

                # KILLER (verde)
                worksheet.write(row, 2, data.get('killer', '?'), killer_format)
                worksheet.write(row, 3, data.get('killer_team', '?'), team_format)

                # Arrow/Skull
                worksheet.write(row, 4, '💀', arrow_format)

                # VICTIM (vermelho)
                worksheet.write(row, 5, data.get('victim', '?'), victim_format)
                worksheet.write(row, 6, data.get('victim_team', '?'), team_format)

                # Arma
                weapon = data.get('weapon', '-')
                worksheet.write(row, 7, weapon, data_format)

                worksheet.set_row(row, 24)
                row += 1
                kill_number += 1

        # 📝 Resumo ao final
        if row > 1:
            row += 1
            summary_format = workbook.add_format({
                'bold': True,
                'bg_color': '#E0E0E0',
                'border': 2,
                'align': 'center',
                'font_size': 11
            })

            worksheet.merge_range(row, 0, row, 3, f"TOTAL DE KILLS: {kill_number - 1}", summary_format)

            # Conta kills por time
            team_kills = {}
            for event in events:
                if event.get('event_type') == 'kill':
                    team = event.get('data', {}).get('killer_team', '?')
                    team_kills[team] = team_kills.get(team, 0) + 1

            # Top killer team
            if team_kills:
                top_team = max(team_kills.items(), key=lambda x: x[1])
                worksheet.merge_range(row, 4, row, 7,
                    f"TOP KILLER: {top_team[0]} ({top_team[1]} kills)",
                    summary_format)

    def _export_advanced(self, workbook, match_data: Dict):
        """Formato avançado com estatísticas extras."""
        # Chama formato padrão
        self._export_standard(workbook, match_data)

        # Adiciona aba de gráficos/estatísticas
        stats_worksheet = workbook.add_worksheet("Estatísticas Avançadas")

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white'
        })

        # Top 5 Killers
        stats_worksheet.write(0, 0, "TOP 5 KILLERS", header_format)

        leaderboard = match_data.get('leaderboard', [])[:5]
        for i, player in enumerate(leaderboard, 1):
            stats_worksheet.write(i, 0, f"{i}. {player['name']}")
            stats_worksheet.write(i, 1, f"{player['kills']} kills")
            stats_worksheet.write(i, 2, player['team'] or '?')

        # Kill Timeline (últimos eventos)
        stats_worksheet.write(8, 0, "KILL TIMELINE", header_format)

        events = match_data.get('recent_events', [])
        row = 9
        for event in events[-10:]:  # Últimos 10
            if event['event_type'] == 'kill':
                data = event['data']
                text = f"{data['killer']} -> {data['victim']}"
                stats_worksheet.write(row, 0, text)
                row += 1

    def export_to_csv(self, match_data: Dict, filepath: str) -> bool:
        """Exporta para CSV simples."""
        try:
            import csv

            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Header
                writer.writerow(['Nome', 'Time', 'Kills', 'Deaths', 'Status'])

                # Data
                for team_data in match_data.get('teams', {}).values():
                    for player in team_data.get('players', []):
                        writer.writerow([
                            player['name'],
                            player['team'] or '?',
                            player['kills'],
                            player['deaths'],
                            'VIVO' if player['alive'] else 'MORTO'
                        ])

            logger.info(f"CSV exported to: {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            return False


def test_exporter():
    """Testa o exportador com dados simulados."""
    # Dados simulados
    match_data = {
        'match_start': datetime.now().isoformat(),
        'total_players': 10,
        'total_alive': 4,
        'total_dead': 6,
        'total_teams': 2,
        'total_kills': 6,
        'teams': {
            'Team A': {
                'total': 4,
                'alive': 3,
                'dead': 1,
                'total_kills': 5,
                'players': [
                    {'name': 'Alpha', 'team': 'Team A', 'kills': 3, 'deaths': 0, 'alive': True, 'first_seen': '2026-02-03', 'last_seen': '2026-02-03'},
                    {'name': 'Bravo', 'team': 'Team A', 'kills': 1, 'deaths': 0, 'alive': True, 'first_seen': '2026-02-03', 'last_seen': '2026-02-03'},
                    {'name': 'Charlie', 'team': 'Team A', 'kills': 1, 'deaths': 0, 'alive': True, 'first_seen': '2026-02-03', 'last_seen': '2026-02-03'},
                    {'name': 'Xray', 'team': 'Team A', 'kills': 0, 'deaths': 1, 'alive': False, 'first_seen': '2026-02-03', 'last_seen': '2026-02-03'},
                ]
            },
            'Team B': {
                'total': 6,
                'alive': 1,
                'dead': 5,
                'total_kills': 1,
                'players': [
                    {'name': 'Zeta', 'team': 'Team B', 'kills': 0, 'deaths': 1, 'alive': False, 'first_seen': '2026-02-03', 'last_seen': '2026-02-03'},
                    {'name': 'Yankee', 'team': 'Team B', 'kills': 0, 'deaths': 1, 'alive': False, 'first_seen': '2026-02-03', 'last_seen': '2026-02-03'},
                    {'name': 'Whiskey', 'team': 'Team B', 'kills': 0, 'deaths': 1, 'alive': False, 'first_seen': '2026-02-03', 'last_seen': '2026-02-03'},
                    {'name': 'Victor', 'team': 'Team B', 'kills': 0, 'deaths': 1, 'alive': False, 'first_seen': '2026-02-03', 'last_seen': '2026-02-03'},
                    {'name': 'Uniform', 'team': 'Team B', 'kills': 0, 'deaths': 1, 'alive': False, 'first_seen': '2026-02-03', 'last_seen': '2026-02-03'},
                    {'name': 'Delta', 'team': 'Team B', 'kills': 1, 'deaths': 0, 'alive': True, 'first_seen': '2026-02-03', 'last_seen': '2026-02-03'},
                ]
            }
        },
        'leaderboard': [
            {'name': 'Alpha', 'team': 'Team A', 'kills': 3, 'deaths': 0, 'alive': True},
            {'name': 'Bravo', 'team': 'Team A', 'kills': 1, 'deaths': 0, 'alive': True},
            {'name': 'Charlie', 'team': 'Team A', 'kills': 1, 'deaths': 0, 'alive': True},
            {'name': 'Delta', 'team': 'Team B', 'kills': 1, 'deaths': 0, 'alive': True},
        ],
        'recent_events': [
            {'event_type': 'kill', 'timestamp': '2026-02-03', 'data': {'killer': 'Alpha', 'victim': 'Zeta', 'killer_team': 'Team A', 'victim_team': 'Team B'}},
            {'event_type': 'kill', 'timestamp': '2026-02-03', 'data': {'killer': 'Bravo', 'victim': 'Yankee', 'killer_team': 'Team A', 'victim_team': 'Team B'}},
        ]
    }

    exporter = ExcelExporter()

    print("Testing Excel export...")
    print("- Standard format")
    exporter.export_match(match_data, "test_match_standard.xlsx", format='standard')

    print("- Luis format (template)")
    exporter.export_match(match_data, "test_match_luis.xlsx", format='luis')

    print("- Advanced format")
    exporter.export_match(match_data, "test_match_advanced.xlsx", format='advanced')

    print("- CSV format")
    exporter.export_to_csv(match_data, "test_match.csv")

    print("\nFiles created:")
    print("  - test_match_standard.xlsx")
    print("  - test_match_luis.xlsx")
    print("  - test_match_advanced.xlsx")
    print("  - test_match.csv")
    print("\nOpen them to see the results!")


if __name__ == "__main__":
    test_exporter()
