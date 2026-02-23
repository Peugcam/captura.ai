# COMO CONFIGURAR A SENHA DO OBS

## PASSO 1: Abrir configurações do OBS

1. Abra o **OBS Studio**
2. No menu superior, clique em: **Ferramentas**
3. Clique em: **Configurações do servidor WebSocket** (ou **WebSocket Server Settings**)

---

## PASSO 2: Ativar e ver a senha

Você verá uma janela assim:

```
☑ Ativar servidor WebSocket
Porta do servidor: 4455
☑ Habilitar autenticação
Senha do servidor: •••••••••••••••
[Gerar senha] [Mostrar informações da conexão]
```

**IMPORTANTE:** A senha aparece escondida com pontinhos (••••••)

---

## PASSO 3: Ver a senha

Clique no botão: **Mostrar informações da conexão**

Você verá algo assim:
```
Endereço remoto: [::1]:63932
Duração da sessão: 130/130
Mensagens: 130/130
Identificada: ✓
```

E embaixo terá a **SENHA COMPLETA** escrita

---

## PASSO 4: Copiar a senha

1. Selecione toda a senha
2. Copie (Ctrl+C)
3. **ANOTE em algum lugar** (bloco de notas, por exemplo)

Exemplo de senha:
```
ZNx3v4LjLVCgbTrO
```

---

## PASSO 5: Colocar a senha no programa

1. Abra o arquivo: **gta-analytics-v2.py**
2. Procure a linha 42 (mais ou menos no começo do arquivo)
3. Você verá algo assim:

```python
OBS_PASSWORD = "ZNx3v4LjLVCgbTrO"
```

4. **SUBSTITUA** a senha entre aspas pela SUA senha que você copiou:

```python
OBS_PASSWORD = "COLE_SUA_SENHA_AQUI"
```

5. Salve o arquivo (Ctrl+S)

---

## PASSO 6: Testar

Agora execute o programa:
```bash
py gta-analytics-v2.py
```

Se aparecer:
```
✅ Conectado ao OBS (localhost:4455)
```

**Funcionou!** ✅

Se aparecer erro de conexão, verifique se:
- OBS está aberto
- WebSocket está ativado
- Porta é 4455
- Senha está correta

---

## DÚVIDAS COMUNS

**P: Não sei abrir o arquivo .py para editar**
R: Clique com botão direito → Abrir com → Bloco de Notas

**P: Não encontro a linha 42**
R: Procure por "OBS_PASSWORD" no arquivo (Ctrl+F)

**P: A senha tem letras e números misturados?**
R: Sim! Maiúsculas, minúsculas e números. Copie EXATAMENTE como está.

**P: Posso mudar a senha no OBS?**
R: Sim! No OBS clique em "Gerar senha" para criar uma nova. Depois atualize no .py

---

✅ **Pronto! Com isso o Luis consegue configurar o próprio OBS dele!**
