from fastapi import FastAPI, Form, Request, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import requests
import urllib.parse
from datetime import datetime
from supabase import create_client, Client

# Importações para geração do PDF com ReportLab
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
import os

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
TELEGRAM_BOT_TOKEN = "9063674052:AAHNqqnqZAOoIDChjAeGwckyy5ZP2Onb5v0"
TELEGRAM_CHAT_ID = " 6326233839"

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

def formatar_telefone(tel_str):
    apenas_nums = "".join(filter(str.isdigit, str(tel_str)))
    if len(apenas_nums) in [10, 11]:
        apenas_nums = "55" + apenas_nums
    return apenas_nums

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
                
                <label>Seu WhatsApp (com DDD):</label>
                <input type="text" name="telefone" required placeholder="Ex: 99 98888-7777">
                
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
    telefone_formatado = formatar_telefone(telefone)
    
    dados_novo = {
        "solicitante": solicitante,
        "telefone": telefone_formatado,
        "categoria": categoria,
        "prioridade": prioridade,
        "descricao": descricao,
        "horario": horario_atual,
        "status": "🔴 Aberto",
        "observacao": ""
    }
    
    resposta = supabase.table("chamados").insert(dados_novo).execute()
    
    ticket_id = "Novo"
    if resposta.data:
        ticket_id = resposta.data[0].get("id", "Novo")

    aviso_tecnico = (
        f"🔔 *NOVO CHAMADO #{ticket_id}!*\n\n"
        f"👤 *Solicitante:* {solicitante}\n"
        f"📱 *WhatsApp:* {telefone_formatado}\n"
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
def painel_admin(
    username: str = Depends(verificar_senha),
    status_filtro: str = Query("", alias="status"),
    busca: str = Query("", alias="busca")
):
    # Puxa todos para contagem de abertos
    todos_resposta = supabase.table("chamados").select("*").execute()
    todos_chamados = todos_resposta.data if todos_resposta.data else []
    
    total_abertos = sum(1 for c in todos_chamados if "Aberto" in c.get('status', ''))

    # Consulta com filtro
    query = supabase.table("chamados").select("*").order("id", desc=True)
    if status_filtro:
        query = query.eq("status", status_filtro)
    
    resposta = query.execute()
    chamados_db = resposta.data if resposta.data else []

    if busca:
        busca_lower = busca.lower()
        chamados_db = [c for c in chamados_db if busca_lower in c.get('solicitante', '').lower() or busca_lower in c.get('categoria', '').lower() or busca_lower in c.get('descricao', '').lower()]

    linhas_tabela = ""
    for c in chamados_db:
        c_id = c.get('id')
        solicitante = c.get('solicitante', '')
        telefone = c.get('telefone', '')
        categoria = c.get('categoria', '')
        prio = c.get('prioridade', 'Normal')
        status_atual = c.get('status', '🔴 Aberto')
        obs = c.get('observacao', '')
        
        telefone_limpo = formatar_telefone(telefone)
        botoes_acao = f'<div style="display: flex; gap: 6px; justify-content: center; flex-wrap: wrap;">'
        
        if telefone_limpo:
            if "Aberto" in status_atual:
                msg_inicio = f"Olá {solicitante}, aqui é da TechDhan! Recebemos o seu chamado sobre *{categoria}* (Prioridade: {prio}) e já estamos verificando. Em breve daremos retorno!"
                link_whatsapp = f"https://wa.me/{telefone_limpo}?text={urllib.parse.quote(msg_inicio)}"
                botoes_acao += f'<a href="{link_whatsapp}" target="_blank" style="background: #25d366; color: white; padding: 6px 10px; border-radius: 4px; text-decoration: none; font-size: 11px; font-weight: 600;">WhatsApp</a>'
            else:
                msg_fim = f"Olá {solicitante}, o seu chamado #{c_id} sobre *{categoria}* foi concluído com sucesso pela TechDhan! Ficou tudo certinho por aí?"
                link_whatsapp_fim = f"https://wa.me/{telefone_limpo}?text={urllib.parse.quote(msg_fim)}"
                botoes_acao += f'<a href="{link_whatsapp_fim}" target="_blank" style="background: #25d366; color: white; padding: 6px 10px; border-radius: 4px; text-decoration: none; font-size: 11px; font-weight: 600;">Avisar Fim</a>'
        
        if "Aberto" in status_atual:
            botoes_acao += f'<a href="/concluir-form/{c_id}" style="background: #16a34a; color: white; padding: 6px 10px; border-radius: 4px; text-decoration: none; font-size: 11px; font-weight: 600;">Concluir</a>'
        else:
            botoes_acao += '<span style="color: #4ade80; font-size: 11px; font-weight: 600;">Finalizado</span>'
            
        botoes_acao += '</div>'
            
        detalhes_html = f"{categoria}<br><small style='color:#94a3b8;'>{c.get('descricao')}</small>"
        if obs:
            detalhes_html += f"<br><small style='color:#38bdf8;'><b>Nota Técnica:</b> {obs}</small>"

        linhas_tabela += f"""
        <tr style="border-bottom: 1px solid #334155;">
            <td style="padding: 12px; font-weight: bold;">#{c_id}</td>
            <td style="padding: 12px;">{c.get('horario')}<br><b>{solicitante}</b><br><small style="color:#94a3b8;">📱 {telefone}</small></td>
            <td style="padding: 12px;">{detalhes_html}</td>
            <td style="padding: 12px;">{prio}</td>
            <td style="padding: 12px;">{status_atual}</td>
            <td style="padding: 12px; text-align: center;">{botoes_acao}</td>
        </tr>
        """
        
    if not linhas_tabela:
        linhas_tabela = '<tr><td colspan="6" style="text-align: center; padding: 30px; color: #94a3b8;">Nenhum chamado encontrado com esses filtros.</td></tr>'

    badge_html = f'<span style="background: #dc2626; color: white; padding: 4px 10px; border-radius: 20px; font-size: 13px; font-weight: 600;">🔴 {total_abertos} Chamados Abertos</span>' if total_abertos > 0 else '<span style="background: #16a34a; color: white; padding: 4px 10px; border-radius: 20px; font-size: 13px; font-weight: 600;">🟢 Tudo em dia!</span>'

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
            .topo-acoes {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px; }}
            .filtros {{ display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin-bottom: 15px; }}
            input, select {{ padding: 8px; border: 1px solid #475569; border-radius: 6px; background: #0f172a; color: #f8fafc; font-size: 13px; }}
            button, .btn-pdf {{ background: #0284c7; color: white; border: none; padding: 8px 14px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; }}
            button:hover, .btn-pdf:hover {{ background: #0369a1; }}
            .btn-pdf {{ background: #16a34a; }}
            .btn-pdf:hover {{ background: #15803d; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }}
            th {{ background: #0284c7; color: white; padding: 12px; text-align: left; font-size: 13px; }}
            .voltar {{ color: #38bdf8; text-decoration: none; font-weight: 600; }}
            .voltar:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="topo-acoes">
                <a href="/" class="voltar">&larr; Voltar ao Formulário</a>
                <div>{badge_html}</div>
                <a href="/admin/pdf?status={status_filtro}&busca={busca}" target="_blank" class="btn-pdf">📄 Baixar Relatório em PDF</a>
            </div>
            <h2>Painel de Controle - TechDhan (Técnico)</h2>
            
            <form method="GET" action="/admin" class="filtros">
                <input type="text" name="busca" placeholder="Buscar solicitante/categoria..." value="{busca}">
                <select name="status">
                    <option value="">Todos os Status</option>
                    <option value="🔴 Aberto" {"selected" if status_filtro == "🔴 Aberto" else ""}>Abertos</option>
                    <option value="🟢 Concluído" {"selected" if status_filtro == "🟢 Concluído" else ""}>Concluídos</option>
                </select>
                <button type="submit">Filtrar</button>
                <a href="/admin" style="color: #94a3b8; font-size: 13px; text-decoration: none; padding: 8px;">Limpar</a>
            </form>

            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Horário / Solicitante / Tel</th>
                        <th>Detalhes / Nota Técnica</th>
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

# Página intermediária para digitar a Nota Técnica ao concluir
@app.get("/concluir-form/{ticket_id}", response_class=HTMLResponse)
def concluir_form(ticket_id: int, username: str = Depends(verificar_senha)):
    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Concluir Chamado #{ticket_id}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; padding: 50px; color: #f8fafc; }}
            .card {{ background: #1e293b; max-width: 450px; margin: auto; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); border: 1px solid #334155; }}
            h2 {{ color: #38bdf8; margin-top: 0; }}
            label {{ display: block; margin-top: 15px; font-weight: 600; font-size: 13px; color: #cbd5e1; }}
            textarea {{ width: 100%; padding: 10px; margin-top: 6px; border: 1px solid #475569; border-radius: 6px; box-sizing: border-box; background: #0f172a; color: #f8fafc; font-size: 14px; }}
            button {{ width: 100%; background: #16a34a; color: white; border: none; padding: 12px; margin-top: 20px; border-radius: 6px; font-size: 16px; font-weight: 600; cursor: pointer; }}
            button:hover {{ background: #15803d; }}
            a {{ display: inline-block; margin-top: 15px; color: #94a3b8; text-decoration: none; font-size: 13px; text-align: center; width: 100%; }}
            a:hover {{ color: white; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Concluir Chamado #{ticket_id}</h2>
            <form action="/concluir-salvar/{ticket_id}" method="POST">
                <label>Nota Técnica / O que foi feito:</label>
                <textarea name="observacao" rows="4" required placeholder="Ex: Substituído o cabo de rede e reconfigurado o switch..."></textarea>
                <button type="submit">Salvar e Concluir</button>
            </form>
            <a href="/admin">&larr; Voltar ao Painel</a>
        </div>
    </body>
    </html>
    """

@app.post("/concluir-salvar/{ticket_id}")
def concluir_salvar(ticket_id: int, observacao: str = Form(...), username: str = Depends(verificar_senha)):
    supabase.table("chamados").update({
        "status": "🟢 Concluído",
        "observacao": observacao
    }).eq("id", ticket_id).execute()
    return RedirectResponse(url="/admin", status_code=303)

@app.get("/admin/pdf")
def gerar_relatorio_pdf(
    username: str = Depends(verificar_senha),
    status_filtro: str = Query("", alias="status"),
    busca: str = Query("", alias="busca")
):
    query = supabase.table("chamados").select("*").order("id", desc=True)
    if status_filtro:
        query = query.eq("status", status_filtro)
    
    resposta = query.execute()
    chamados_db = resposta.data if resposta.data else []

    if busca:
        busca_lower = busca.lower()
        chamados_db = [c for c in chamados_db if busca_lower in c.get('solicitante', '').lower() or busca_lower in c.get('categoria', '').lower() or busca_lower in c.get('descricao', '').lower()]

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elementos = []

    styles = getSampleStyleSheet()
    
    logo_path = os.path.join("static", "logo.jpg")
    if os.path.exists(logo_path):
        img = RLImage(logo_path, width=70, height=70)
        elementos.append(img)
    
    titulo_estilo = ParagraphStyle('TituloRelatorio', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0f172a'), spaceAfter=4)
    sub_estilo = ParagraphStyle('SubRelatorio', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#64748b'), spaceAfter=15)

    elementos.append(Paragraph("RELATÓRIO DE ATENDIMENTOS - TECHDHAN", titulo_estilo))
    data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")
    filtro_txt = f"Filtros: Status: {status_filtro or 'Todos'} | Busca: {busca or 'Nenhuma'}"
    elementos.append(Paragraph(f"Emitido em: {data_geracao} | {filtro_txt}", sub_estilo))
    elementos.append(Spacer(1, 10))

    dados_tabela = [["ID", "Data/Horário", "Solicitante", "Categoria / Nota Técnica", "Prioridade", "Status"]]
    
    for c in chamados_db:
        detalhes_pdf = f"{c.get('categoria', '')}\nDesc: {c.get('descricao', '')}"
        if c.get('observacao'):
            detalhes_pdf += f"\nObs: {c.get('observacao')}"

        dados_tabela.append([
            f"#{c.get('id')}",
            c.get('horario', ''),
            c.get('solicitante', ''),
            detalhes_pdf,
            c.get('prioridade', ''),
            c.get('status', '')
        ])

    tabela = Table(dados_tabela, colWidths=[30, 90, 110, 150, 65, 65])
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284c7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    elementos.append(tabela)
    doc.build(elementos)
    
    buffer.seek(0)
    return Response(content=buffer.getvalue(), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=relatorio_techdhan.pdf"})