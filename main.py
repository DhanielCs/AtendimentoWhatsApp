from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import requests
import urllib.parse
from datetime import datetime
from supabase import create_client, Client

app = FastAPI()

# 1. CONFIGURAÇÕES DO SUPABASE (Sem o /rest/v1/ no final)
SUPABASE_URL = "https://fqvxitiwhwcpiiertiyr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZxdnhpdGl3aHdjcGlpZXJ0aXlyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTMxMTQyMTksImV4cCI6MjEwODY5MDIxOX0.k2TlF0G8GJ04Gsl_V3BhFP-XG_l3xuqLzZO3aGo8YzQ"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. CONFIGURAÇÕES DO TELEGRAM (Para você receber os alertas de Novo Chamado)
TELEGRAM_BOT_TOKEN = "9063674052:AAHNqqnqZAOoIDChjAeGwckyy5ZP2Onb5v0"
TELEGRAM_CHAT_ID = "6326233839"

# 3. CONFIGURAÇÕES DO CALLMEBOT (Apenas para avisar o CLIENTE no WhatsApp quando concluir)
APIKEY_CALLMEBOT = "4197128"

def enviar_telegram(mensagem):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": mensagem,
            "parse_mode": "Markdown"
        }
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Erro Telegram: {e}")

def enviar_whatsapp(telefone_destino, mensagem):
    try:
        mensagem_formatada = urllib.parse.quote(mensagem)
        url = f"https://api.callmebot.com/whatsapp.php?phone={telefone_destino}&text={mensagem_formatada}&apikey={APIKEY_CALLMEBOT}"
        requests.get(url, timeout=5)
    except Exception as e:
        print(f"Erro WhatsApp: {e}")

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Abertura de Chamado - TI</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f4f6f9; padding: 20px; }
            .container { max-width: 400px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: auto; }
            h2 { color: #333; text-align: center; }
            label { display: block; margin-top: 10px; font-weight: bold; color: #555; }
            input, select, textarea { width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; background: #fff; }
            button { width: 100%; background: #007bff; color: white; border: none; padding: 10px; margin-top: 15px; border-radius: 4px; font-size: 16px; cursor: pointer; }
            button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Abrir Chamado de TI</h2>
            <form action="/enviar" method="POST">
                <label>Seu Nome / Setor:</label>
                <input type="text" name="solicitante" required placeholder="Ex: Recepção - Clínica">
                
                <label>Seu WhatsApp (para receber avisos):</label>
                <input type="text" name="telefone" required placeholder="Ex: 5599988887777">
                
                <label>Categoria do Problema:</label>
                <select name="categoria" required>
                    <option value="" disabled selected>Selecione uma categoria...</option>
                    <option value="Rede / Internet">Rede / Internet</option>
                    <option value="Computador / Hardware">Computador / Hardware</option>
                    <option value="Impressoras / Periféricos">Impressoras / Periféricos</option>
                    <option value="Sistemas / Software">Sistemas / Software</option>
                    <option value="Câmeras de Segurança (CFTV)">Câmeras de Segurança (CFTV)</option>
                    <option value="Telefonia">Telefonia</option>
                    <option value="Outros">Outros</option>
                </select>
                
                <label>Descrição do Problema:</label>
                <textarea name="descricao" rows="4" required placeholder="Descreva o que está acontecendo..."></textarea>
                
                <button type="submit">Enviar Chamado</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/enviar", response_class=HTMLResponse)
def receber_chamado(solicitante: str = Form(...), telefone: str = Form(...), categoria: str = Form(...), descricao: str = Form(...)):
    horario_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")
    
    # Salva no Supabase
    dados_novo = {
        "solicitante": solicitante,
        "telefone": telefone,
        "categoria": categoria,
        "descricao": descricao,
        "horario": horario_atual,
        "status": "🔴 Aberto"
    }
    
    resposta = supabase.table("chamados").insert(dados_novo).execute()
    
    ticket_id = "Novo"
    if resposta.data:
        ticket_id = resposta.data[0].get("id", "Novo")

    # Dispara o alerta para o TÉCNICO instantaneamente no Telegram
    aviso_tecnico = (
        f"🔔 *NOVO CHAMADO #{ticket_id}!*\n\n"
        f"👤 *Solicitante:* {solicitante}\n"
        f"📱 *WhatsApp:* {telefone}\n"
        f"🔧 *Categoria:* {categoria}\n"
        f"⏰ *Horário:* {horario_atual}\n"
        f"📝 *Descrição:* {descricao}"
    )
    enviar_telegram(aviso_tecnico)
    
    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Chamado Enviado</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f4f6f9; text-align: center; padding: 50px; }}
            .card {{ background: white; max-width: 400px; margin: auto; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h2 {{ color: #28a745; }}
            a {{ display: inline-block; margin-top: 15px; color: #007bff; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Chamado Registrado!</h2>
            <p>Sua solicitação foi enviada com sucesso às {horario_atual}. Você receberá atualizações via WhatsApp.</p>
            <a href="/">Abrir outro chamado</a>
        </div>
    </body>
    </html>
    """

@app.get("/admin", response_class=HTMLResponse)
def painel_admin():
    resposta = supabase.table("chamados").select("*").order("id", desc=True).execute()
    chamados_db = resposta.data if resposta.data else []

    linhas_tabela = ""
    for c in chamados_db:
        botao_concluir = ""
        status_atual = c.get('status', '🔴 Aberto')
        c_id = c.get('id')
        
        if "Aberto" in status_atual:
            botao_concluir = f'<a href="/concluir/{c_id}" style="background: #28a745; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-size: 12px;">Concluir</a>'
        else:
            botao_concluir = '<span style="color: #888; font-size: 12px;">Finalizado</span>'
            
        linhas_tabela += f"""
        <tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 10px;">#{c_id}</td>
            <td style="padding: 10px;">{c.get('horario')}<br><b>{c.get('solicitante')}</b></td>
            <td style="padding: 10px;">{c.get('categoria')}<br><small>{c.get('descricao')}</small></td>
            <td style="padding: 10px;">{status_atual}</td>
            <td style="padding: 10px; text-align: center;">{botao_concluir}</td>
        </tr>
        """
        
    if not linhas_tabela:
        linhas_tabela = '<tr><td colspan="5" style="text-align: center; padding: 20px; color: #666;">Nenhum chamado registrado ainda.</td></tr>'

    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Painel do Técnico - Chamados TI</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f4f6f9; padding: 20px; }}
            .container {{ max-width: 800px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: auto; }}
            h2 {{ color: #333; text-align: center; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th {{ background: #007bff; color: white; padding: 10px; text-align: left; font-size: 14px; }}
            .voltar {{ display: inline-block; margin-bottom: 15px; color: #007bff; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="voltar">&larr; Voltar ao Formulário</a>
            <h2>Painel de Controle - Chamados de TI</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Horário / Solicitante</th>
                        <th>Detalhes</th>
                        <th>Status</th>
                        <th style="text-align: center;">Ação</th>
                    </tr>
                </thead>
                <tbody>
                    {linhas_tabela}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

@app.get("/concluir/{ticket_id}")
def concluir_chamado(ticket_id: int):
    # Atualiza no Supabase
    supabase.table("chamados").update({"status": "🟢 Concluído"}).eq("id", ticket_id).execute()
    
    # Busca os dados do chamado para mandar o WhatsApp para o cliente
    resposta = supabase.table("chamados").select("*").eq("id", ticket_id).execute()
    
    if resposta.data:
        c = resposta.data[0]
        mensagem_cliente = (
            f"✅ *SEU CHAMADO FOI CONCLUÍDO!*\n\n"
            f"Olá, {c['solicitante']}! O seu chamado *#{c['id']}* ({c['categoria']}) foi atendido e finalizado pela equipe de TI.\n\n"
            f"Caso o problema persista, abra um novo chamado. Obrigado!"
        )
        enviar_whatsapp(c['telefone'], mensagem_cliente)
            
    return RedirectResponse(url="/admin", status_code=303)