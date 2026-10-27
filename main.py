from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import requests
import urllib.parse
from datetime import datetime
from supabase import create_client, Client

app = FastAPI()

# 1. CONFIGURAÇÕES DO SUPABASE
SUPABASE_URL = "https://fqvxitiwhwcpiiertiyr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZxdnhpdGl3aHdjcGlpZXJ0aXlyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTMxMTQyMTksImV4cCI6MjEwODY5MDIxOX0.k2TlF0G8GJ04Gsl_V3BhFP-XG_l3xuqLzZO3aGo8YzQ"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. CONFIGURAÇÕES DO TELEGRAM
TELEGRAM_BOT_TOKEN = "9063674052:AAHNqqnqZAOoIDChjAeGwckyy5ZP2Onb5v0" # (Mantenha o seu token atual)
TELEGRAM_CHAT_ID = "6326233839" # (Mantenha o seu chat_id atual)

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

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Suporte Técnico - Abertura de Chamado</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; padding: 20px; color: #333; }
            .container { max-width: 480px; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin: auto; }
            .header { text-align: center; margin-bottom: 25px; }
            .header svg { width: 48px; height: 48px; color: #007bff; margin-bottom: 10px; }
            h2 { color: #1a1a1a; margin: 0; font-size: 22px; }
            p.subtitle { color: #666; font-size: 14px; margin-top: 5px; }
            label { display: block; margin-top: 15px; font-weight: 600; font-size: 13px; color: #444; }
            input, select, textarea { width: 100%; padding: 10px; margin-top: 6px; border: 1px solid #d1d5db; border-radius: 6px; box-sizing: border-box; background: #f9fafb; font-size: 14px; transition: border 0.2s; }
            input:focus, select:focus, textarea:focus { border-color: #007bff; outline: none; background: #fff; box-shadow: 0 0 0 3px rgba(0,123,255,0.1); }
            button { width: 100%; background: #007bff; color: white; border: none; padding: 12px; margin-top: 20px; border-radius: 6px; font-size: 16px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
            button:hover { background: #0056b3; }
            .footer-links { text-align: center; margin-top: 20px; font-size: 13px; }
            .footer-links a { color: #007bff; text-decoration: none; }
            .footer-links a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M11.42 15.17L17.25 21A2.652 2.652 0 0021 17.25l-5.83-5.83m-3.75 3.75l-3.5-3.5a2.121 2.121 0 013-3l3.5 3.5m-3.75 3.75l6.5-6.5m-11.5 8.5l3.5-3.5" />
                </svg>
                <h2>Central de Suporte TI</h2>
                <p class="subtitle">Preencha os dados abaixo para abrir sua solicitação</p>
            </div>
            <form action="/enviar" method="POST">
                <label>Seu Nome / Setor:</label>
                <input type="text" name="solicitante" required placeholder="Ex: Recepção - Consultório 02">
                
                <label>Seu WhatsApp (para contato):</label>
                <input type="text" name="telefone" required placeholder="Ex: 5599988887777">
                
                <label>Categoria do Problema:</label>
                <select name="categoria" required>
                    <option value="" disabled selected>Selecione o tipo de ocorrência...</option>
                    <option value="Rede / Internet">Rede / Internet</option>
                    <option value="Computador / Hardware">Computador / Hardware</option>
                    <option value="Impressoras / Periféricos">Impressoras / Periféricos</option>
                    <option value="Sistemas / Software">Sistemas / Software</option>
                    <option value="Câmeras de Segurança (CFTV)">Câmeras de Segurança (CFTV)</option>
                    <option value="Telefonia">Telefonia</option>
                    <option value="Outros">Outros</option>
                </select>

                <label>Nível de Urgência:</label>
                <select name="prioridade" required>
                    <option value="🟢 Baixa">Baixa (Pode aguardar)</option>
                    <option value="🟡 Normal" selected>Normal (Atendimento padrão)</option>
                    <option value="🟠 Alta">Alta (Impactando parcialmente)</option>
                    <option value="🔴 Crítica">Crítica (Parado / Emergência)</option>
                </select>
                
                <label>Descrição Detalhada do Problema:</label>
                <textarea name="descricao" rows="4" required placeholder="Descreva o que está acontecendo com detalhes..."></textarea>
                
                <button type="submit">Enviar Chamado</button>
            </form>
            <div class="footer-links">
                <a href="/admin">Acessar Painel do Técnico &rarr;</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/enviar", response_class=HTMLResponse)
def receber_chamado(solicitante: str = Form(...), telefone: str = Form(...), categoria: str = Form(...), prioridade: str = Form(...), descricao: str = Form(...)):
    horario_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")
    
    dados_novo = {
        "solicitante": solicitante,
        "telefone": telefone,
        "categoria": categoria,
        "prioridade": prioridade,
        "descricao": descricao,
        "horario": horario_atual,
        "status": "🔴 Aberto"
    }
    
    resposta = supabase.table("chamados").insert(dados_novo).execute()
    
    ticket_id = "Novo"
    if resposta.data:
        ticket_id = resposta.data[0].get("id", "Novo")

    aviso_tecnico = (
        f"🔔 *NOVO CHAMADO #{ticket_id}!*\n\n"
        f"👤 *Solicitante:* {solicitante}\n"
        f"📱 *WhatsApp:* {telefone}\n"
        f"🔧 *Categoria:* {categoria}\n"
        f"⚡ *Prioridade:* {prioridade}\n"
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
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; text-align: center; padding: 50px; }}
            .card {{ background: white; max-width: 420px; margin: auto; padding: 40px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
            h2 {{ color: #16a34a; margin-top: 15px; }}
            p {{ color: #555; font-size: 14px; line-height: 1.5; }}
            a {{ display: inline-block; margin-top: 20px; color: #007bff; text-decoration: none; font-weight: 600; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Chamado Registrado!</h2>
            <p>Sua solicitação foi enviada com sucesso às <b>{horario_atual}</b>. Nossa equipe foi notificada e em breve entrará em contato.</p>
            <a href="/">&larr; Abrir outro chamado</a>
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
        prio = c.get('prioridade', 'Normal')
        
        if "Aberto" in status_atual:
            botao_concluir = f'<a href="/concluir/{c_id}" style="background: #16a34a; color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; font-size: 12px; font-weight: 600;">Concluir</a>'
        else:
            botao_concluir = '<span style="color: #888; font-size: 12px;">Finalizado</span>'
            
        linhas_tabela += f"""
        <tr style="border-bottom: 1px solid #e5e7eb;">
            <td style="padding: 12px; font-weight: bold;">#{c_id}</td>
            <td style="padding: 12px;">{c.get('horario')}<br><b>{c.get('solicitante')}</b></td>
            <td style="padding: 12px;">{c.get('categoria')}<br><small style="color:#666;">{c.get('descricao')}</small></td>
            <td style="padding: 12px;">{prio}</td>
            <td style="padding: 12px;">{status_atual}</td>
            <td style="padding: 12px; text-align: center;">{botao_concluir}</td>
        </tr>
        """
        
    if not linhas_tabela:
        linhas_tabela = '<tr><td colspan="6" style="text-align: center; padding: 30px; color: #666;">Nenhum chamado registrado ainda.</td></tr>'

    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Painel do Técnico - Chamados TI</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; padding: 20px; }}
            .container {{ max-width: 950px; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin: auto; }}
            h2 {{ color: #1a1a1a; text-align: center; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14px; }}
            th {{ background: #007bff; color: white; padding: 12px; text-align: left; font-size: 13px; }}
            .voltar {{ display: inline-block; margin-bottom: 15px; color: #007bff; text-decoration: none; font-weight: 600; }}
            .voltar:hover {{ text-decoration: underline; }}
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
                        <th>Prioridade</th>
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
    supabase.table("chamados").update({"status": "🟢 Concluído"}).eq("id", ticket_id).execute()
    return RedirectResponse(url="/admin", status_code=303)