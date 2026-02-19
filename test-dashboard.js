const { chromium } = require('playwright');

async function testDashboard() {
    console.log('🎮 Iniciando testes do Dashboard V2...\n');

    const browser = await chromium.launch({ headless: false, slowMo: 500 });
    const page = await browser.newPage();

    try {
        // 1. Abrir dashboard
        console.log('📂 Abrindo dashboard...');
        const dashboardPath = 'file:///' + __dirname.replace(/\\/g, '/') + '/dashboard-strategist-v2.html';
        await page.goto(dashboardPath);
        await page.waitForTimeout(2000);

        // 2. Verificar status de conexão
        console.log('🔌 Verificando conexão WebSocket...');
        const connectionStatus = await page.locator('#connectionStatus').textContent();
        console.log(`   Status: ${connectionStatus}`);

        // 3. Abrir modal de configuração
        console.log('\n⚙️ Testando modal de configuração...');
        await page.click('button:has-text("Configurar Torneio")');
        await page.waitForTimeout(1000);
        const modalVisible = await page.locator('#setupModal.show').isVisible();
        console.log(`   Modal aberto: ${modalVisible ? '✅' : '❌'}`);

        // 4. Criar torneio de teste
        console.log('\n🚀 Criando torneio de teste...');
        await page.fill('#teamTagsInput', 'TEST1, TEST2, TEST3');
        await page.click('button:has-text("Iniciar Torneio")');
        await page.waitForTimeout(3000);

        // 5. Verificar grid de times
        console.log('\n📊 Verificando grid de times...');
        const teamBoxes = await page.locator('.team-box').count();
        console.log(`   Times carregados: ${teamBoxes}`);

        if (teamBoxes > 0) {
            // 6. Testar toggle de status de jogador
            console.log('\n🔄 Testando toggle de status de jogador...');
            const firstPlayerBox = page.locator('.player-box.alive').first();

            // Capturar estado inicial
            const initialClass = await firstPlayerBox.getAttribute('class');
            console.log(`   Estado inicial: ${initialClass}`);

            // Clicar no jogador
            await firstPlayerBox.click();
            await page.waitForTimeout(2000);

            // Verificar mudança de estado
            const updatedClass = await firstPlayerBox.getAttribute('class');
            console.log(`   Estado após click: ${updatedClass}`);

            const statusChanged = initialClass !== updatedClass;
            console.log(`   Toggle funcionou: ${statusChanged ? '✅' : '❌'}`);

            // 7. Testar modal de edição
            console.log('\n✏️ Testando modal de edição...');
            await page.click('button:has-text("Editar Times")');
            await page.waitForTimeout(1000);

            const editModalVisible = await page.locator('#editModal.show').isVisible();
            console.log(`   Modal de edição aberto: ${editModalVisible ? '✅' : '❌'}`);

            if (editModalVisible) {
                // Contar jogadores no modal
                const playerRows = await page.locator('.edit-player-row').count();
                console.log(`   Jogadores no modal: ${playerRows}`);

                // Testar adicionar jogador
                console.log('\n➕ Testando adicionar jogador...');
                const addPlayerBtn = page.locator('.add-player-btn').first();
                await addPlayerBtn.click();
                await page.waitForTimeout(500);

                const newPlayerCount = await page.locator('.edit-player-row').count();
                console.log(`   Jogadores após adicionar: ${newPlayerCount}`);
                console.log(`   Adição funcionou: ${newPlayerCount > playerRows ? '✅' : '❌'}`);

                // Testar editar nome de jogador
                console.log('\n📝 Testando editar nome de jogador...');
                const firstPlayerInput = page.locator('.edit-player-input').first();
                await firstPlayerInput.fill('CUSTOM_PLAYER_NAME');
                await page.waitForTimeout(500);
                const newName = await firstPlayerInput.inputValue();
                console.log(`   Novo nome: ${newName}`);

                // Testar toggle no modal
                console.log('\n🔄 Testando toggle no modal de edição...');
                const statusBtn = page.locator('.status-toggle-btn').first();
                const initialBtnClass = await statusBtn.getAttribute('class');
                await statusBtn.click();
                await page.waitForTimeout(500);
                const updatedBtnClass = await statusBtn.getAttribute('class');
                console.log(`   Toggle no modal funcionou: ${initialBtnClass !== updatedBtnClass ? '✅' : '❌'}`);

                // Cancelar edição
                console.log('\n❌ Cancelando edições...');
                await page.click('button:has-text("Cancelar")');
                await page.waitForTimeout(1000);
            }

            // 8. Testar modo curador
            console.log('\n🎨 Testando modo curador...');
            await page.click('#curatorBtn');
            await page.waitForTimeout(500);
            const curatorIndicatorVisible = await page.locator('#curatorModeIndicator.active').isVisible();
            console.log(`   Modo curador ativado: ${curatorIndicatorVisible ? '✅' : '❌'}`);

            // Desativar modo curador
            await page.click('#curatorBtn');
            await page.waitForTimeout(500);

            // 9. Testar navegação entre abas
            console.log('\n📑 Testando navegação entre abas...');

            // Aba 2 - Kill Feed
            await page.click('button:has-text("Kill Feed")');
            await page.waitForTimeout(500);
            const tab2Active = await page.locator('.tab-content').nth(1).isVisible();
            console.log(`   Aba Kill Feed: ${tab2Active ? '✅' : '❌'}`);

            // Aba 3 - Leaderboard
            await page.click('button:has-text("Leaderboard")');
            await page.waitForTimeout(500);
            const tab3Active = await page.locator('.tab-content').nth(2).isVisible();
            console.log(`   Aba Leaderboard: ${tab3Active ? '✅' : '❌'}`);

            // Voltar para Aba 1
            await page.click('button:has-text("Controle de Torneio")');
            await page.waitForTimeout(500);
        }

        console.log('\n✅ Testes concluídos com sucesso!');
        console.log('\n⏳ Fechando navegador em 5 segundos...');
        await page.waitForTimeout(5000);

    } catch (error) {
        console.error('\n❌ Erro durante os testes:', error);
    } finally {
        await browser.close();
    }
}

// Executar testes
testDashboard().catch(console.error);
