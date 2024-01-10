import requests
import locale
from flask import Flask, render_template, flash, redirect, url_for, request, session, jsonify, json
from datetime import date, datetime, timedelta
from models.models import Ops, Movimentos_estoque, Estrutura_op, User, Lote, Saldo_por_posicao
from models.forms import LoginForm, RegisterForm
from flask_login import login_user, logout_user, current_user
from config import app, db, app_key, app_secret, bcrypt, login_manager


locale.setlocale(locale.LC_ALL, 'pt_BR.utf-8')

#============URL DE SISTEMA=============#

url_produtos = "https://app.omie.com.br/api/v1/geral/produtos/"
url_estrutura = "https://app.omie.com.br/api/v1/geral/malha/"
url_consulta_estoque = "https://app.omie.com.br/api/v1/estoque/consulta/"
url_ajuste_estoque = "https://app.omie.com.br/api/v1/estoque/ajuste/"


#============LOCAIS DE ESTOQUE=============# 

A1 = 2436985075
AC = 2511785274
A3 = 4084861665
CQ = 4085565942
SE = 4085566100
AS = 4085566245
MKM = 2407629011

locaisOmie = [A1, AC, A3, CQ, SE, AS]


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


#============== REGISTER ============#
@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm() 
    if current_user.is_authenticated:
         return redirect( url_for('logged'))
    if form.validate_on_submit(): 

        encrypted_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

        new_user = User(email=form.email.data, password=encrypted_password, name=form.name.data)  

        db.session.add(new_user)
        db.session.commit() 

        flash(f'Conta criada com socesso para o usuário {form.email.data}', category='success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

#=============== LOGIN ==============#
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect( url_for('logged'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        logged_user = form.email.data
        session["logged_user"] = logged_user

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("logged"))
        else:
            flash(f'Erro ao logar no usuário {form.email.data}', category='danger')
            
    return render_template('login_page.html', form=form)  

#=============Sessão====================#
@app.route("/logged")
def logged():
    if "logged_user" in session:
        logged_user = session["logged_user"]
        return redirect(url_for('index'))
    else:
        return redirect(url_for("login"))    

#============= Logout ==================#
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))  




#===================Quando usuario estiver logado ==================#
@app.route('/index', methods = ['GET','POST'])
def index():
    if not current_user.is_authenticated:
         return redirect( url_for('login'))
    return render_template('index.html')


@app.route('/busca', methods = ['GET','POST'])
def busca():
    if not current_user.is_authenticated:
         return redirect( url_for('login'))
    if request.method == 'POST':
        item = request.form.get("search")
        data = {
                "call":"ConsultarProduto",
                "app_key": app_key,
                "app_secret": app_secret,
                "param":[{
                    "codigo": item
                    }
                ]}
        response = requests.post(url=url_produtos, json=data)
        busca = response.json()
               

        return  render_template('buscarv2.html',  busca = busca)




@app.route('/estrutura', methods = ['GET','POST'])
def estrutura():
    item = request.form.get("item")
    if not current_user.is_authenticated:
         return redirect( url_for('login'))
    
    if request.method == 'POST':  
        data = {
                "call":"ConsultarEstrutura",
                "app_key": app_key,
                "app_secret": app_secret,
                "param":[{
                    "codProduto": item
                        }
                ]}
        response = requests.post(url=url_estrutura, json=data)
        estrutura = response.json()
        
        return render_template("estrutura.html", estrutura=estrutura)
#===================Todas modificações de diego ==================#    

@app.route('/teste_diego', methods = ['GET','POST'])
def teste_diego():
    item = request.form.get('teste_item')
    data = {
                "call":"ConsultarProduto",
                "app_key": app_key,
                "app_secret": app_secret,
                "param":[{
                    "codigo": item
                        }
                ]}
    response = requests.post(url=url_produtos, json=data)
    teste = response.json()
    
    operacao = teste.get('codigo_familia')
    if operacao == None:
       operacao = 0
    else:
       operacao = operacao * 2

    id_produto = teste.get('codigo_produto')
    if id_produto == None:
       id_produto = 0
    return teste2_diego(id_produto, teste,operacao)       
def teste2_diego(id_produto, teste,operacao, methods = ['GET','POST']):       
    
    data = {
                "call":"PosicaoEstoque",
                "app_key": app_key,
                "app_secret": app_secret,
                "param":[{
                      "id_prod": id_produto
                        }
                ]}
    response = requests.post(url=url_consulta_estoque, json=data)
    teste2 = response.json()

    saldoFisico = teste2.get('fisico')
    if saldoFisico == None:
       saldoFisico = 2

    
    
    return render_template('teste.html',teste = teste,teste2 = teste2,id_produto = id_produto,saldoFisico = saldoFisico, operacao = operacao)


@app.route('/teste_saldo', methods = ['GET','POST'])
def teste_saldo():       
    id_prod = request.form.get('teste_saldo')
    data = {
                "call":"PosicaoEstoque",
                "app_key": app_key,
                "app_secret": app_secret,
                "param":[{
                      "id_prod": id_prod
                        }
                ]}
    response = requests.post(url=url_consulta_estoque, json=data)
    saldo = response.json()

    saldoFisico = saldo.get('saldo')
    if saldoFisico == None:
       saldoFisico = 3

    
    
    return render_template('saldo.html',saldo = saldo, id_prod = id_prod, saldoFisico = saldoFisico)

#===================Fim de todas modificações de diego ==================#

@app.route('/itens', methods = ['GET','POST'])
def itens():
    if not current_user.is_authenticated:
         return redirect( url_for('login'))
    pagina = 1
    data = {
        "call":"ListarProdutos",
        "app_key": app_key,
        "app_secret":app_secret,
        "param":[{
            "pagina": pagina,
            "registros_por_pagina": 20,
            "apenas_importado_api": "N",
            "filtrar_apenas_omiepdv": "N"	
            }
        ]}
    response = requests.post(url=url_produtos, json=data)
    lista_itens = response.json()

    return  render_template('itens.html',  lista_itens = lista_itens  )


@app.route('/update', methods=['GET', 'POST'])
def update():
        if not current_user.is_authenticated:
            return redirect( url_for('login'))
        data = {
                "call":"AlterarProduto",
                "app_key":app_key,
                "app_secret":app_secret,
                "param":[{
                    "codigo":"teste1235",
                    "descricao":"Produto de teste",
                    "unidade":"UN"
                    }
            ]}

        return redirect(url_for('itens'))


@app.route('/consulta_estoque', methods = ['GET','POST'])
def consulta_estoque(): 
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    return  render_template('consulta_estoque.html')

@app.route('/estoque', methods = ['GET','POST'])
def estoque():
    if not current_user.is_authenticated: # tipo, saldoFisico, unidade, valor_unitario, descricao, item
        return redirect( url_for('login'))
    item = request.form.get("estoque")
    estoqueprod = cadastro_prod(item,A1)
    saldoFisico=estoqueprod[2]
    tipo = estoqueprod[1]
    unidade = estoqueprod[3]
    valor_unitario = estoqueprod[4]
    descricao = estoqueprod[5]
    item = estoqueprod[6]

               

    return  render_template('estoquer2.html', saldoFisico = saldoFisico, tipo = tipo, unidade = unidade, valor_unitario = valor_unitario, descricao = descricao, item = item)


@app.route('/lista_movimento', methods = ['GET','POST'])
def lista_movimento():
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    page = request.args.get('page', 1, type=int)
    dados = Movimentos_estoque.query.paginate(page=page,per_page=20)
    return  render_template('lista_movimento.html',  movimentos = dados)

@app.route('/lista_movimento_filtro', methods = ['GET','POST'])
def lista_movimento_filtro():
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    data_movimento = request.form.get("data_movimento")
    filtro = Movimentos_estoque.query.filter_by(data_movimento = data_movimento).all()
    
    return  render_template('lista_movimento_filtro.html', filtro = filtro)

# ================================== OPS ===============================================#


@app.route('/ordens_producao', methods = ['GET','POST'])
def ordens_producao():
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    page = request.args.get('page', 1, type=int)
    dados = Ops.query.paginate(page=page,per_page=10) 
    return render_template('ordens_producao.html', itens = dados)

@app.route('/insert_op', methods=['POST'])
def insert_op():     
    data_atual = date.today().strftime("%Y-%m-%d")
    hora_atual = datetime.now().strftime("%H:%M")
     
    ano_dia = date.today().strftime("%Y%d")
    hora_minuto = datetime.now().strftime("%H%M")
    numero_op = ano_dia + hora_minuto

    if request.method == 'POST':
        item = request.form.get("item")
        data = {
                "call":"ConsultarProduto",
                "app_key": app_key,
                "app_secret": app_secret,
                "param":[{
                    "codigo": item
                    }
                ]}
        response = requests.post(url=url_produtos, json=data)
        data_resp = response.json()
        numero_op = numero_op
        situação = "Aberta"       
        descrição = data_resp.get("descricao")
        quantidade = float(request.form.get("quantidade"))
        data_abertura = data_atual
        hora_abertura = hora_atual

        novo_item = Ops(numero_op=numero_op, situação=situação, item=item, descrição=descrição, quantidade=quantidade, data_abertura = data_abertura, hora_abertura = hora_abertura)

        db.session.add(novo_item)
        db.session.commit()

        flash (f'OP para o item {item} Aberta com sucesso', category='soccess')

   


    return redirect(url_for('ordens_producao'))

@app.route('/update_op', methods=['GET', 'POST'])
def update_op():
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    
    if request.method == 'POST':
        edit_item = Ops.query.get(request.form.get('id'))  
        edit_item.item = request.form.get("item")
        edit_item.descrição = request.form.get("descricao")
        edit_item.quantidade = request.form.get("quantidade")

        db.session.commit()
        
        flash (f'Op editada com sucesso', category='soccess')

        return redirect(url_for('ordens_producao'))
        


@app.route('/delete_op/<id>', methods=['GET', 'POST'])
def delete(id):
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    item = Ops.query.get(id)

    db.session.delete(item)
    db.session.commit()

    flash (f'Op deletada com sucesso', category='soccess')

    return redirect(url_for('ordens_producao'))



# ================================== LOTES ==============================================================

@app.route('/op/<numero_op>', methods = ['GET','POST'])
def op(numero_op):
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    op = numero_op
    item = request.form.get("item")
    descricao = request.form.get("descricao")
    op_qtd = request.form.get("op_qtd")
    ref = [op, item, descricao, op_qtd]
    lotes = Lote.query.filter_by(op_referencia = op).all()   
    op_info = Ops.query.filter_by(numero_op = op).all()

    data = {
                "call":"ConsultarEstrutura",
                "app_key": app_key,
                "app_secret": app_secret,
                "param":[{
                    "codProduto": item
                        }
                ]}
    response = requests.post(url=url_estrutura, json=data)
    estrutura_op = response.json()

    item_recomendado_estrutura = Estrutura_op.query.filter_by(op_referencia = op).all()
     
    

    return render_template("lotes.html", lotes=lotes, ref=ref, op_info=op_info, op=op, item_recomendado_estrutura=item_recomendado_estrutura,  estrutura_op= estrutura_op)


@app.route('/adicionar_lote', methods=['POST'])
def adicionar_lote():
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    item = request.form.get("item")
    op_referencia = request.form.get("op_referencia")
    lote = str(int(db.session.query(db.func.max(Lote.lote)).scalar() or 0) + 1)
    numero_lote = "".join([op_referencia, "/", lote ])
    quantidade = request.form.get("quantidade")
    data_fabricacao = datetime.now().strftime('%d/%m/%Y')
    data_validade = (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')
    novo_lote = Lote(op_referencia=op_referencia, lote=lote, numero_lote=numero_lote, quantidade=quantidade, data_fabricacao=data_fabricacao, data_validade=data_validade)
    data = {
                    "call":"ConsultarEstrutura",
                    "app_key": app_key,
                    "app_secret": app_secret,
                    "param":[{
                        "codProduto": item
                            }
                    ]}
    response = requests.post(url=url_estrutura, json=data)
    estrutura_op = response.json()

    for row in estrutura_op["itens"]:
        qtd_unitaria = float(row.get('quantProdMalha'))
        nova_estrutura = Estrutura_op(op_referencia=op_referencia, 
                                    item_estrutura=row.get("codProdMalha"), 
                                    descricao_item=row.get("descrProdMalha"),
                                    quantidade_item=float(quantidade) * float(qtd_unitaria))

    db.session.add(nova_estrutura)    
    db.session.add(novo_lote)
    db.session.commit()

    
    return redirect(request.referrer)

@app.route('/deleta_lote', methods=['GET', 'POST'])
def deleta_lote():
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    id = request.form.get("id")
    lote = Lote.query.get(id)

    db.session.delete(lote)
    db.session.commit()   


    return redirect(request.referrer)


@app.route('/estrutura_op/<numero_op>/<numero_lote>', methods = ['GET','POST'])
def estrutura_op(numero_op, numero_lote):
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    op = numero_op
    lote = numero_op + "/" + numero_lote
    itens_movimentados = Movimentos_estoque.query.filter_by(op_referencia = op).all()   
    op_dados = Ops.query.filter_by(numero_op = op).all()

    item_recomendado_estrutura = Estrutura_op.query.filter_by(op_referencia = op).all()  
    

  
    return render_template("estrutura_op.html", itens_movimentados=itens_movimentados, lote=lote, op=op, op_dados=op_dados, item_recomendado_estrutura=item_recomendado_estrutura)


@app.route('/movimento_estoque', methods = ['GET','POST'])
def movimento_estoque():
    if not current_user.is_authenticated:
        return redirect( url_for('login'))

    data_atual = date.today().strftime("%d/%m/%Y")
    hora_atual = datetime.now().strftime("%H:%M")
    if request.method == 'POST':
        op_referencia = request.form.get("op")
        id = request.form.get("id")
        numero_lote = request.form.get("numero_lote")
        item_movimento = request.form.get("item")
        quantidade_movimento = float(request.form.get("quantidade"))
        item_referencia = request.form.get("item_referencia")

        data = {
                    "call":"ConsultarProduto",
                    "app_key": app_key,
                    "app_secret": app_secret,
                    "param":[{
                        "codigo": item_movimento
                        }
                    ]}

        response = requests.post(url=url_produtos, json=data)
        data_resp = response.json()

        descricao = data_resp.get("descricao")

        saldo = {"call":"ObterEstoqueProduto",
                "app_key":app_key,
                "app_secret":app_secret,
                "param":[{
                    "cCodigo":item_movimento,
                    "dDia":data_atual
                    }]
                }

        response = requests.post(url=url_consulta_estoque, json=saldo)
        saldo_resp = response.json()
        saldo = 10000
        saldo_anterior = saldo
        
        novo_movimento = Movimentos_estoque(item_movimento = item_movimento, 
                                            numero_lote = numero_lote,
                                            descricao=descricao, 
                                            op_referencia=op_referencia, 
                                            item_referencia=item_referencia, 
                                            saldo_anterior=saldo_anterior, 
                                            quantidade_movimento=quantidade_movimento, 
                                            saldo_atual = saldo_anterior - quantidade_movimento,
                                            data_movimento = data_atual,
                                            hora_movimento = hora_atual)
        if id != None:
            try:
                deleta_item = Estrutura_op.query.get(id)
                db.session.delete(deleta_item)
            except:
                pass

        db.session.add(novo_movimento)  
        db.session.commit()
            
        return redirect(request.referrer)


@app.route('/encerra_op', methods=['GET', 'POST'])
def encerra_op():
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    if request.method == 'POST':
        id = request.form.get('id')
        situacao = request.form.get('situacao')
        encerra = Ops.query.get(id)  
        encerra.situação = situacao
        db.session.commit()
        if situacao == "Aberta":
            flash (f'Op Reaberta com sucesso', category='soccess')
        else:
            flash (f'Op Encerrada com sucesso', category='soccess')
    return redirect(url_for('ordens_producao'))


@app.route('/deleta_movimento_item', methods=['GET', 'POST'])
def deleta_movimento_item():
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    id = request.form.get("id")
    movimento = Movimentos_estoque.query.get(id)

    db.session.delete(movimento)
    db.session.commit()   


    return redirect(request.referrer)



@app.route('/movimentos_posicaos', methods=['GET', 'POST'])
def movimentos_posicaos():
    if not current_user.is_authenticated:
        return redirect( url_for('login'))

    if request.method == 'POST':
        item = request.form.get("item")
        descricao = request.form.get("descricao")
        quantidade = request.form.get("quantidade_lote")
        op = request.form.get("op_lote")
        lote = request.form.get("lote")
        operador = request.form.get("operador")
        posicao = request.form.get("posicao")

        saldo_movimento = Saldo_por_posicao(item=item, descricao=descricao, quantidade=quantidade, op=op, lote=lote, operador=operador, posicao=posicao)

        db.session.add(saldo_movimento)  
        db.session.commit()

    return redirect(url_for('posicoes_estoque'))    

@app.route('/transferir_saldo_posicao', methods=['GET', 'POST'])
def transferir_saldo_posicao():
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    
    if request.method == 'POST':
        transf_lote = Saldo_por_posicao.query.get(request.form.get('id'))
        transf_lote.posicao = request.form.get("posicao")

        db.session.commit()
        
        flash (f'Lote transferido com sucesso', category='soccess')

        return redirect(url_for('posicoes_estoque'))


@app.route('/posicoes_estoque', methods=['GET', 'POST'])
def posicoes_estoque():
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    page = request.args.get('page', 1, type=int)
    dados = Saldo_por_posicao.query.paginate(page=page,per_page=20)
    return  render_template('posicoes_estoque2.html',  posicoes = dados)

@app.route('/posicoes_estoque_omie', methods=['GET', 'POST'])
def posicoes_estoque_omie():
    if not current_user.is_authenticated: # tipo, saldoFisico, unidade, valor_unitario, descricao, item
        return redirect( url_for('login'))
    item = request.form.get("estoque")
    prodlocal = []
    for y in locaisOmie:
        for x in cadastro_prod(item,y):
            loc=[y,x]
            prodlocal.append(loc)
    prodlocal = tuple(prodlocal)

    saldototal = prodlocal[2][1] + prodlocal[11][1] + prodlocal[38][1] + prodlocal[29][1] + prodlocal[47][1]
    
    unidadeI = prodlocal[3][1]

    convert =  Convert_Unidade("Consulta", unidadeI)
    unidade = convert[0]
    fator = convert[2]
    qtda1 = prodlocal[2][1] * fator
    qtdac = prodlocal[11][1] * fator 
    qtdse = prodlocal[38][1] * fator
    qtdcq = prodlocal[29][1] * fator
    qtdas = prodlocal[47][1] * fator

    qtdtol = qtda1 + qtdac + qtdse + qtdcq + qtdas

    if saldototal == 0:
        frase = ""
    else:    
        frase = (f'Saldo Total do Item: {prodlocal[6][1]} = {qtdtol:.0f} {unidade}  _____||_____ Omie = {locale.format("%1.3f", saldototal, grouping=True)} {prodlocal[3][1]}')




    return  render_template('posicoes_estoque.html', prodlocal = prodlocal, frase = frase,
                             qtda1 = qtda1,qtdac = qtdac, qtdse = qtdse, qtdcq = qtdcq,
                              qtdas = qtdas, unidade = unidade)

#===================Todas definições do diego ==================#  
@app.route('/cadastro_prod', methods = ['GET','POST'])
def cadastro_prod(item, local):
    item = item
  
   # item = request.form.get('item')
    
    data = {
                "call":"ConsultarProduto",
                "app_key": app_key,
                "app_secret": app_secret,
                "param":[{
                    "codigo": item
                        }
                ]}
    response = requests.post(url=url_produtos, json=data)
    cadastro = response.json()
    
    tipo = cadastro.get('tipoItem')
    if tipo == None:
       tipo = "-"
    else:

      if (tipo == "00") or (tipo == "01") or (tipo == "03") or (tipo == "04") or (tipo == "05") or (tipo == "06"):
        tipo = "Produtivo"
      else:
        tipo = "Não Produtivo"      
    unidade = cadastro.get('unidade')
    if unidade == None:
       unidade = "-"

    id_produto = cadastro.get('codigo_produto')
    if id_produto == None:
       id_produto = 0

    valor_unitario = cadastro.get('valor_unitario')
    if valor_unitario == None:
       valor_unitario = 0

    descricao = cadastro.get('descricao')
    if descricao == None:
       descricao = "-"
    item = cadastro.get('codigo')
    if item == None:
       item = "-"
    
    cliente = cadastro.get('marca')
    if cliente == None:
       cliente = "-"
    codigo_cliente = cadastro.get('obs_internas')
    if codigo_cliente == None:
       codigo_cliente = "-"

   
    return cadastro_prod2(id_produto, tipo, unidade, valor_unitario, descricao,item, local, cliente, codigo_cliente)       
def cadastro_prod2(id_produto, tipo, unidade, valor_unitario, descricao, item, local, cliente, codigo_cliente, methods = ['GET','POST']):       
    
    data = {
                "call":"PosicaoEstoque",
                "app_key": app_key,
                "app_secret": app_secret,
                "param":[{
                      "codigo_local_estoque": local,
                      "id_prod": id_produto
                        }
                ]}
    response = requests.post(url=url_consulta_estoque, json=data)
    cadastro_saldo = response.json()

    saldoFisico = cadastro_saldo.get('saldo')
    if saldoFisico == None:
       saldoFisico = 0

    
    #return render_template('temp1.html',cadastro = cadastro, cadastro_saldo = cadastro_saldo ,id_produto = id_produto, saldoFisico = saldoFisico, tipo = tipo)
    return [id_produto, tipo, saldoFisico, unidade, valor_unitario, descricao, item, cliente, codigo_cliente]
@app.route('/cadastro_prod', methods = ['GET','POST'])

#===================definição de ajuste de estoque ==================#

def ajuste_estoque(item,quan,tipomov,local):
    item = item
  
   # item = request.form.get('item')
    
    data = {
                "call":"ConsultarProduto",
                "app_key": app_key,
                "app_secret": app_secret,
                "param":[{
                    "codigo": item
                        }
                ]}
    response = requests.post(url=url_produtos, json=data)
    cadastro = response.json()
    
    tipo = cadastro.get('tipoItem')
    if tipo == None:
       tipo = "-"
    else:

      if (tipo == "00") or (tipo == "01") or (tipo == "03") or (tipo == "04") or (tipo == "05") or (tipo == "06"):
        tipo = "Produtivo"
      else:
        tipo = "Não Produtivo"      
    unidade = cadastro.get('unidade')
    if unidade == None:
       unidade = "-"

    id_produto = cadastro.get('codigo_produto')
    if id_produto == None:
       id_produto = 0

    valor_unitario = cadastro.get('valor_unitario')
    if valor_unitario == None:
       valor_unitario = 0

    
    return ajuste_estoque2(id_produto, quan, local, tipomov, tipo, unidade, valor_unitario)       
def ajuste_estoque2(id_produto, quan, local, tipomov, tipo, unidade, valor_unitario, methods = ['GET','POST']):       
    
    data = {
                "call":"IncluirAjusteEstoque",
                "app_key": app_key,
                "app_secret": app_secret,
                "param":[{
                            "codigo_local_estoque": local,
                            "id_prod": id_produto,
                            "data": date.today().strftime("%d/%m/%Y"),
                            "quan": quan,
                            "obs": "Ajuste feito pelo Vipro.AI",
                            "origem": "AJU",
                            "tipo": tipomov,
                            "motivo": "OPE",
                            "valor": valor_unitario
                            }
                ]}
    response = requests.post(url=url_ajuste_estoque, json=data)
    ajuste_estoque2 = response.json()

    status = ajuste_estoque2.get('codigo_status')
    if status == None:
       status = "erro"
    elif status == 0:
       status = "OK"

    
    #return render_template('temp1.html',cadastro = cadastro, cadastro_saldo = cadastro_saldo ,id_produto = id_produto, saldoFisico = saldoFisico, tipo = tipo)
    return [id_produto, tipo, status, unidade, valor_unitario, ajuste_estoque2]
#================definição de converção de Unidade================#
def Convert_Unidade(tipomov, unidade):
    fatoromie = 1
    fatorvisual = 1

    if tipomov == "Entrada":
      if unidade == "MIL":
          unidade = "PC"
          fatoromie = 1 / 1000
          fatorvisual = 1

      if unidade == "PC":
          unidade = "PC"
          fatoromie = 1
          fatorvisual = 1

      if unidade == "UN":
          unidade = "PC"
          fatoromie = 1
          fatorvisual = 1

      if unidade == "KG":
          unidade = "GR"
          fatoromie = 1 / 1000
          fatorvisual = 1
        
    if tipomov == "Saida":
      if unidade == "MIL":
          unidade = "PC"
          fatoromie = 1 / 1000
          fatorvisual = 1
         
      if unidade == "PC":
          unidade = "PC"
          fatoromie = 1
          fatorvisual = 1

      if unidade == "UN":
          unidade = "PC"
          fatoromie = 1
          fatorvisual = 1

      if unidade == "KG":
          unidade = "GR"
          fatoromie = 1 / 1000
          fatorvisual = 1
    if tipomov == "Consulta":
      
      if unidade == "PC":
          unidade = "PC"
          fatoromie = 1
          fatorvisual = 1

      if unidade == "UN":
          unidade = "PC"
          fatoromie = 1
          fatorvisual = 1

      if unidade == "KG":
          unidade = "GR"
          fatoromie = 1 # não usa
          fatorvisual = 1000
      
      if unidade == "MIL":
          unidade = "PC"
          fatoromie = 1 # não usa
          fatorvisual = 1000
          
          

    
    return [unidade, fatoromie, fatorvisual]

#===================fim das definições do diego ==================#
#===================definições simples do diego ==================#
@app.route('/temp')
def temp_prod():
 return f" descrição = {cadastro_prod('CBA-4000',A1)[5]} saldo = {cadastro_prod('CBA-4000',A1)[2]}"

@app.route('/temp2')
def temp_ajust():
 return f" id_produto = {ajuste_estoque('TESTE1235',33,'ENT',AC)[0]} status = {ajuste_estoque('TESTE1235',33,'ENT',AS)[2]} erro = {ajuste_estoque('TESTE1235',33,'ENT',AS)[5]}"


def id_produto(item):
 return cadastro_prod("item,A1")[0]

def tipo(item):
 return cadastro_prod("item,A1")[1]

def saldoFisico(item):
 return cadastro_prod("item,A1")[2]

def unidade(item):
 return cadastro_prod("item,A1")[3]

def valor_unitario(item):
 return cadastro_prod("item,A1")[4]

def descricao(item):
 return cadastro_prod("item,A1")[5]





if __name__ == "__main__":
    app.run(port=3333, debug=True)

