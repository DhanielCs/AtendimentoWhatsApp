from fastapi import FastAPI, Form, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import requests
import urllib.parse
from datetime import datetime
from supabase import create_client, Client

app = FastAPI()

# Libera a pasta 'static' para servir arquivos (como a logo)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Segurança do Painel Admin
security = HTTPBasic()
ADMIN_USER = "admin"
ADMIN_PASS = "techdhan2026" # Altere se desejar

def verificar_senha(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USER)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASS)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais incorretas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# 1. CONFIGURAÇÕES DO SUPABASE
SUPABASE_URL = "https://fqvxitiwhwcpiiertiyr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZxdnhpdGl3aHdjcGlpZXJ0aXlyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTMxMTQyMTksImV4cCI6MjEwODY5MDIxOX0.k2TlF0G8GJ04Gsl_V3BhFP-XG_l3xuqLzZO3aGo8YzQ"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. CONFIGURAÇÕES DO TELEGRAM
TELEGRAM_BOT_TOKEN = "7575317781:AAFFZ-jYnIqL_HnL7v_exemplo_token"
TELEGRAM_CHAT_ID = "123456789"

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
        <title>TechDhan - Suporte de TI</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; padding: 20px; color: #f8fafc; }
            .container { max-width: 480px; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); margin: auto; border: 1px solid #334155; text-align: center; }
            .header { margin-bottom: 25px; }
            .logo-img { max-width: 200px; width: 100%; height: auto; border-radius: 10px; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.4); border: 1px solid #475569; }
            h2 { color: #f8fafc; margin: 0; font-size: 22px; font-weight: 700; }
            p.subtitle { color: #94a3b8; font-size: 11px; margin-top: 6px; line-height: 1.4; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; }
            form { text-align: left; }
            label { display: block; margin-top: 15px; font-weight: 600; font-size: 13px; color: #cbd5e1; }
            input, select, textarea { width: 100%; padding: 10px; margin-top: 6px; border: 1px solid #475569; border-radius: 6px; box-sizing: border-box; background: #0f172a; color: #f8fafc; font-size: 14px; transition: border 0.2s; }
            input:focus, select:focus, textarea:focus { border-color: #38bdf8; outline: none; box-shadow: 0 0 0 3px rgba(56,189,248,0.15); }
            button { width: 100%; background: #0284c7; color: white; border: none; padding: 12px; margin-top: 20px; border-radius: 6px; font-size: 16px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
            button:hover { background: #0369a1; }
            .footer-links { text-align: center; margin-top: 20px; font-size: 13px; }
            .footer-links a { color: #38bdf8; text-decoration: none; }
            .footer-links a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="/static/logo.jpg" alt="TechDhan Logo" class="logo-img">
                <h2>TECHDHAN</h2>
                <p class="subtitle">Suporte de TI, Manutenção de Computadores e Assistência Técnica</p>
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
    
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Chamado Enviado</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; text-align: center; padding: 50px; color: #f8fafc; }
            .card { background: #1e293b; max-width: 420px; margin: auto; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); border: 1px solid #334155; }
            h2 { color: #4ade80; margin-top: 15px; }
            p { color: #94a3b8; font-size: 14px; line-height: 1.5; }
            a { display: inline-block; margin-top: 20px; color: #38bdf8; text-decoration: none; font-weight: 600; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Chamado Registrado!</h2>
            <p>Sua solicitação foi enviada com sucesso. Nossa equipe foi notificada e em breve entrará em contato.</p>
            <a href="/">&larr; Abrir outro chamado</a>
        </div>
    </body>
    </html>
    """

@app.get("/admin", response_class=HTMLResponse)
def painel_admin(username: str = Depends(verificar_senha)):
    resposta = supabase.table("chamados").select("*").order("id", desc=True).execute()
    chamados_db = resposta.data if resposta.data else []

    linhas_tabela = ""
    for c in chamados_db:
        c_id = c.get('id')
        solicitante = c.get('solicitante', '')
        telefone = c.get('telefone', '')
        categoria = c.get('categoria', '')
        prio = c.get('prioridade', 'Normal')
        status_atual = c.get('status', '🔴 Aberto')
        
        # Limpa o telefone para garantir apenas números
        telefone_limpo = "".join(filter(str.isdigit, str(telefone)))
        
        botoes_acao = f'<div style="display: flex; gap: 6px; justify-content: center; flex-wrap: wrap;">'
        
        if telefone_limpo:
            if "Aberto" in status_atual:
                # Mensagem inicial de atendimento
                msg_inicio = f"Olá {solicitante}, aqui é da TechDhan! Recebemos o seu chamado sobre *{categoria}* (Prioridade: {prio}) e já estamos verificando. Em breve daremos retorno!"
                link_whatsapp = f"https://wa.me/{telefone_limpo}?text={urllib.parse.quote(msg_inicio)}"
                botoes_acao += f'<a href="{link_whatsapp}" target="_blank" style="background: #25d366; color: white; padding: 6px 10px; border-radius: 4px; text-decoration: none; font-size: 11px; font-weight: 600;">WhatsApp</a>'
            else:
                # Mensagem de encerramento / pós-atendimento
                msg_fim = f"Olá {solicitante}, o seu chamado #{c_id} sobre *{categoria}* foi concluído com sucesso pela TechDhan! Ficou tudo certinho por aí?"
                link_whatsapp_fim = f"https://wa.me/{telefone_limpo}?text={urllib.parse.quote(msg_fim)}"
                botoes_acao += f'<a href="{link_whatsapp_fim}" target="_blank" style="background: #25d366; color: white; padding: 6px 10px; border-radius: 4px; text-decoration: none; font-size: 11px; font-weight: 600;">Avisar Fim</a>'
        
        if "Aberto" in status_atual:
            botoes_acao += f'<a href="/concluir/{c_id}" style="background: #16a34a; color: white; padding: 6px 10px; border-radius: 4px; text-decoration: none; font-size: 11px; font-weight: 600;">Concluir</a>'
        else:
            botoes_acao += '<span style="color: #4ade80; font-size: 11px; font-weight: 600;">Finalizado</span>'
            
        botoes_acao += '</div>'
            
        linhas_tabela += f"""
        <tr style="border-bottom: 1px solid #334155;">
            <td style="padding: 12px; font-weight: bold;">#{c_id}</td>
            <td style="padding: 12px;">{c.get('horario')}<br><b>{solicitante}</b><br><small style="color:#94a3b8;">📱 {telefone}</small></td>
            <td style="padding: 12px;">{categoria}<br><small style="color:#94a3b8;">{c.get('descricao')}</small></td>
            <td style="padding: 12px;">{prio}</td>
            <td style="padding: 12px;">{status_atual}</td>
            <td style="padding: 12px; text-align: center;">{botoes_acao}</td>
        </tr>
        """
        
    if not linhas_tabela:
        linhas_tabela = '<tr><td colspan="6" style="text-align: center; padding: 30px; color: #94a3b8;">Nenhum chamado registrado ainda.</td></tr>'

    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Painel do Técnico - TechDhan</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; padding: 20px; color: #f8fafc; }}
            .container {{ max-width: 1050px; background: #1e293b; padding: 25px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); margin: auto; border: 1px solid #334155; }}
            h2 {{ color: #f8fafc; text-align: center; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14px; }}
            th {{ background: #0284c7; color: white; padding: 12px; text-align: left; font-size: 13px; }}
            .voltar {{ display: inline-block; margin-bottom: 15px; color: #38bdf8; text-decoration: none; font-weight: 600; }}
            .voltar:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="voltar">&larr; Voltar ao Formulário</a>
            <h2>Painel de Controle - TechDhan (Técnico)</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Horário / Solicitante / Tel</th>
                        <th>Detalhes</th>
                        <th>Prioridade</th>
                        <th>Status</th>
                        <th style="text-align: center;">Ações</th>
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
def concluir_chamado(ticket_id: int, username: str = Depends(verificar_senha)):
    supabase.table("chamados").update({"status": "🟢 Concluído"}).eq("id", ticket_id).execute()
    return RedirectResponse(url="/admin", status_code=303)