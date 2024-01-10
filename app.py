import requests
import locale
from sqlalchemy import desc
from flask import Flask, render_template, flash, redirect, url_for, request, session, jsonify, json
from datetime import date, datetime, timedelta
from models.models import Ops_visual, Movimentos_estoque, Estrutura_op, User, Lote_visual, Sequencia_op, Sequencia_lote, Saldo_por_posicao
from models.forms import LoginForm, RegisterForm
from flask_login import login_user, logout_user, current_user
from config import app, db, app_key, app_secret, bcrypt, login_manager
from operator import neg



locale.setlocale(locale.LC_ALL, 'pt_BR.utf-8')

#============URL DE SISTEMA=============#

url_produtos = "https://app.omie.com.br/api/v1/geral/produtos/"
url_estrutura = "https://app.omie.com.br/api/v1/geral/malha/"
url_consulta_estoque = "https://app.omie.com.br/api/v1/estoque/consulta/"
url_ajuste_estoque = "https://app.omie.com.br/api/v1/estoque/ajuste/"
url_caracter = "https://app.omie.com.br/api/v1/geral/prodcaract/"


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
        item = request.form.get("item")
        status = Def_item_ok(item)
        if status[0] == "ok":
            item = status[1]

            Busca = Def_cadastro_prod(item, A1)
            flash (f'Busca do item: {item} realizada com sucesso', category='success')
        else:
            flash (f' Código: {item} - não cadastrado - ERRO={status}', category='success')
       

        return  render_template('busca.html',  busca = busca)

        #return  render_template('buscarv2.html',  busca = busca)



@app.route('/estrutura', methods = ['GET','POST'])
def estrutura():
    item = request.form.get("item")
    if not current_user.is_authenticated:
         return redirect( url_for('login'))
    

    if request.method == 'POST':  
        
        estrutura = Def_consulta_estrutura(item)
        
        return render_template("estrutura.html", estrutura=estrutura)

@app.route('/itens', methods = ['GET','POST'])
def itens():
    if not current_user.is_authenticated:
         return redirect( url_for('login'))
    item = request.form.get("item")

    dados = Def_cadastro_prod(item,A1)
    
    return  render_template('itens.html',  dados = dados  )


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


@app.route('/gerenciar_estoque', methods = ['GET','POST'])
def gerenciar_estoque(): 
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    return  render_template('gerenciar_estoque.html')

@app.route('/estoque', methods = ['GET','POST'])
def estoque():
    if not current_user.is_authenticated: # tipo, saldoFisico, unidade, valor_unitario, descricao, item
        return redirect( url_for('login'))
    item = request.form.get("item")
    if item != None:
        status = Def_item_ok(item)

        if status[0] == "ok":
            item = status[1]
            flash (f'Consulta do item {item} = {status[0]}, Realizada com Sucesso', category='success')
        else:
            flash (f' Código: {item} = vazio / erro: {status}', category='danger')

    consulta = Lote_visual.query.filter_by(item = item).all()
    # consulta = Lote_visual.query.get(item).all()
    unidade = Def_unidade(item)[0]
    
    setor_all = 0
    peso_all = 0
    setor_a1 = 0
    setor_ac = 0
    setor_se = 0
    setor_cq = 0
    setor_as = 0
    setor_a3 = 0
    setor_mkm = 0
   
    
    for row in consulta:
        if row.local == 2436985075:
            setor_a1 = (setor_a1 + row.quantidade)
        elif row.local == 2511785274:
            setor_ac = (setor_ac + row.quantidade)
        elif row.local == 4085566100:
            setor_se = (setor_se + row.quantidade)
        elif row.local == 4085565942:
            setor_cq = (setor_cq + row.quantidade)
        elif row.local == 4085566245:
            setor_as = (setor_as + row.quantidade)
        elif row.local == 4084861665:
            setor_a3 = (setor_a3 + row.quantidade)
        elif row.local == 2407629011:
            setor_mkm = (setor_mkm + row.quantidade)
        
        setor_all = (setor_all + row.quantidade)
        peso_all = (peso_all + row.peso)
    

    return  render_template('estoquer2.html', consulta = consulta, unidade = unidade,
                             item = item, setor_a1 = setor_a1, setor_ac = setor_ac, setor_se = setor_se,
                              setor_cq = setor_cq, setor_as = setor_as, setor_a3 = setor_a3,
                               setor_mkm = setor_mkm, setor_all = setor_all, peso_all = peso_all)

    
    


@app.route('/lista_movimento', methods = ['GET','POST'])
def lista_movimento():
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    page = request.args.get('page', 1, type=int)
    item = request.form.get("item")
    if item == None:
        dados = Movimentos_estoque.query.order_by(Movimentos_estoque.id.desc()).paginate(page=page,per_page=20)
    else:
        dados = Movimentos_estoque.query.order_by(Movimentos_estoque.id.desc()).filter_by(item = item).paginate(page=page,per_page=20)
    return  render_template('lista_movimento.html',  movimentos = dados)

@app.route('/lista_movimento_filtro', methods = ['GET','POST'])
def lista_movimento_filtro():
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    page = request.args.get('page', 1, type=int)
    data_movimento = request.form.get("data")
    if data_movimento == None:
        filtro = Movimentos_estoque.query.order_by(Movimentos_estoque.id.desc()).paginate(page=page,per_page=20)
    else:
        filtro = Movimentos_estoque.query.order_by(Movimentos_estoque.id.desc()).filter_by(data_movimento = data_movimento).paginate(page=page,per_page=20)
    
    return  render_template('lista_movimento_filtro.html', filtro = filtro, data_movimento = data_movimento)

# ================================== OPS ===============================================#


# @app.route('/ordens_producao', methods = ['GET','POST'])
# def ordens_producao():
#     if not current_user.is_authenticated:
#         return redirect( url_for('login'))
#     page = request.args.get('page', 1, type=int)
#     dados = Ops_visual.query.paginate(page=page,per_page=10) 
#     return render_template('ordens_producao_visual.html', itens = dados)


# @app.route('/insert_op', methods=['POST'])
# def insert_op():     
#     data_atual = date.today().strftime("%Y-%m-%d")
#     hora_atual = datetime.now().strftime("%H:%M")
     
#     ano_dia = date.today().strftime("%Y%d")
#     hora_minuto = datetime.now().strftime("%H%M")
#     numero_op_visual = Def_numero_op()

#     if request.method == 'POST':
#         item = request.form.get("item")
#         #numero_op = numero_op
#         situação = "Aberta"       
#         descrição = Def_descricao(item)
#         quantidade = float(request.form.get("quantidade"))
#         data_abertura = data_atual
#         hora_abertura = hora_atual
#         peso_enviado = 0
#         fino_enviado = 0
#         peso_retornado = 0
#         fino_retornado = 0

#         novo_item = Ops_visual(numero_op_visual=numero_op_visual, situação=situação, item=item, descrição=descrição, quantidade=quantidade, peso_enviado=peso_enviado, peso_retornado=peso_retornado, fino_enviado=fino_enviado, fino_retornado=fino_retornado, data_abertura = data_abertura, hora_abertura = hora_abertura)

#         db.session.add(novo_item)
#         db.session.commit()

#         flash (f'OP para o item {item} Aberta com sucesso', category='success')

   


#     return redirect(url_for('ordens_producao_visual'))

@app.route('/update_op', methods=['GET', 'POST'])
def update_op():
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    
    if request.method == 'POST':
        edit_item = Ops_visual.query.get(request.form.get('id'))  
        edit_item.item = request.form.get("item")
        edit_item.descrição = request.form.get("descricao")
        edit_item.quantidade = request.form.get("quantidade")

        db.session.commit()
        
        flash (f'Op editada com sucesso', category='success')

        return redirect(url_for('ordens_producao_visual'))
        


@app.route('/delete_op/<id>', methods=['GET', 'POST'])
def delete(id):
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    item = Ops_visual.query.get(id)

    db.session.delete(item)
    db.session.commit()

    flash (f'Op deletada com sucesso', category='success')

    return redirect(url_for('ordens_producao_visual'))


# ===============================Ordem de produção Visual================================================
@app.route('/ordens_producao_visual', methods = ['GET','POST'])
def ordens_producao_visual():
    filtro = request.form.get("filtro_op")
    filtro_cod = request.form.get("codigo_op")
    if not current_user.is_authenticated:
     return redirect( url_for('login'))
    if filtro == "":
        filtro = None
    
    if filtro_cod == "":
        filtro_cod = None
    
    page = request.args.get('page', 1, type=int)
    itens_ordered = Ops_visual.query.order_by(Ops_visual.numero_op_visual.desc()).all()

    dados = Ops_visual.query.order_by(Ops_visual.numero_op_visual.desc()).paginate(page=page,per_page=10)
    


    return render_template('ordens_producao_visual.html', itens = dados, filtro = filtro, filtro_cod = filtro_cod)

@app.route('/insert_op_Visual', methods=['POST'])
def insert_op_visual():     
    data_atual = date.today().strftime("%Y-%m-%d")
    hora_atual = datetime.now().strftime("%H:%M")
     
    # ano_dia = date.today().strftime("%Y%d")
    # hora_minuto = datetime.now().strftime("%H%M")
    numero_op_visual = Def_numero_op()

    if request.method == 'POST':
        item = request.form.get("item")
        status = Def_item_ok(item)
        if status[0] == "ok":
            item = status[1]


            situação = "Aberta"       
            descrição = Def_descricao(item)
            quantidade = float(request.form.get("quantidade"))
            data_abertura = data_atual
            hora_abertura = hora_atual
            peso_enviado = 0
            fino_enviado = 0
            peso_retornado = 0
            fino_retornado = 0

            novo_item = Ops_visual(numero_op_visual=numero_op_visual, situação=situação, item=item, descrição=descrição, quantidade=quantidade, peso_enviado=peso_enviado, peso_retornado=peso_retornado, fino_enviado=fino_enviado, fino_retornado=fino_retornado, data_abertura = data_abertura, hora_abertura = hora_abertura)

            db.session.add(novo_item)
            db.session.commit()

            flash (f'OP para o item {item} Aberta com sucesso', category='success')
        else:
             flash (f' Código: {item} - não cadastrado - ERRO={status}', category='success')
                

    return redirect(url_for('ordens_producao_visual'))




# ================================== LOTES ==============================================================

@app.route('/op/<numero_op_visual>', methods = ['GET','POST'])
def op(numero_op_visual):
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    op = numero_op_visual
    item = request.form.get("item")
    descricao = request.form.get("descricao")
    op_qtd = request.form.get("op_qtd")
    ref = [op, item, descricao, op_qtd]
    mov_op = Estrutura_op.query.filter_by(op_referencia = op).all()
    lotes = Lote_visual.query.filter_by(referencia = op).all()   
    op_info = Ops_visual.query.filter_by(numero_op_visual = op).all()
    estrutura_op = Def_consulta_estrutura(item)
    
    return render_template("lotes.html", lotes=lotes, ref=ref, op_info=op_info, op=op, estrutura_op= estrutura_op, mov_op = mov_op)


@app.route('/adicionar_lote', methods = ['GET','POST'])
def adicionar_lote():
    nova_estrutura = ""

    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    item = request.form.get("item")
    status = Def_item_ok(item)
    if status[0] == "ok":
        item = status[1]

    
        op_referencia = request.form.get("op_referencia")
        # lote = str(int(db.session.query(db.func.max(Lote.lote)).scalar() or 0) + 1)
        lote = Def_numero_lote(op_referencia)
        numero_lote = lote # "".join([op_referencia, "/", lote ])
        quantidade = request.form.get("quantidade")
        data_criacao = datetime.now().strftime('%d/%m/%Y')
        #data_validade = (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')
        tipo = "visual"
        peso = 1
        fino = 0.050
        local = A1
        novo_lote = Lote_visual(referencia=op_referencia, tipo=tipo, lote_visual=lote, numero_lote=numero_lote, quantidade=quantidade, peso=peso, fino=fino, local=local, data_criacao=data_criacao,)
        
        estrutura_op = Def_consulta_estrutura(item)

        if estrutura_op.get('ident') == None:
            for row in estrutura_op["itens"]:
                qtd_unitaria = float(row.get('quantProdMalha'))
                nova_estrutura = Estrutura_op(op_referencia=op_referencia, 
                item_estrutura=row.get("codProdMalha"), 
                descricao_item=row.get("descrProdMalha"),
                quantidade_item=float(quantidade) * float(qtd_unitaria))
                db.session.add(nova_estrutura) 

        
        db.session.add(novo_lote)
        db.session.commit()
        flash (f'Lote para o item {item} criado com sucesso', category='success')
    else:
        flash (f' Código: {item} - não cadastrado - ERRO={status}', category='success')

    
    return redirect(request.referrer)


@app.route('/adicionar_lote_geral', methods = ['GET','POST'])
def adicionar_lote_geral():
    
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    
    item = request.form.get("item")
    if item != None:
        status = Def_item_ok(item)

    
        if status[0] == "ok":
            item = status[1]
            referencia = request.form.get("referencia")
            # lote = str(int(db.session.query(db.func.max(Lote.lote)).scalar() or 0) + 1)
            lote = Def_numero_lote(referencia)
            numero_lote = lote # "".join([op_referencia, "/", lote ])
            quantidade = request.form.get("quantidade")
            quantidade = float(quantidade)
            data_criacao = datetime.now().strftime('%d/%m/%Y')
            #data_validade = (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')
            tipo = request.form.get("tipo")
            peso = request.form.get("peso")
            idprod =Def_id_produto(item)
            tempfino = Def_Caracter(idprod)
            fino = float(peso) * (float(tempfino[0].replace(",",".")) / float(tempfino[1].replace(",",".")) )
            local = request.form.get("local")
            fino = int(fino)
            obs = request.form.get("obs")
            um_omie =Def_unidade(item)[1]

            novo_lote = Lote_visual(referencia=referencia, tipo=tipo, item=item, lote_visual=lote, numero_lote=numero_lote, quantidade=quantidade, peso=peso, fino=fino, local=local, obs=obs, data_criacao=data_criacao,)
            
            db.session.add(novo_lote)
            db.session.commit()
            tipomov = "Lote manual"
            Def_movimento_estoque(item, tipomov, lote, referencia, quantidade, obs)
            status_omie = Def_ajuste_estoque(item,quantidade,"ENT",local)
            flash (f'Lote: {lote}/{referencia} Lançado para o item: {item} = {status[0]}, Quantidade Omie = {status_omie[2] * quantidade} {um_omie}', category='success')
    else:
        flash (f' Código: {item} = vazio / erro: {status}', category='danger')

    return  render_template('gerenciar_estoque.html', item = item)

    
    
    


   # return redirect(request.referrer)




@app.route('/deleta_lote', methods=['GET', 'POST'])
def deleta_lote():
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    id = request.form.get("id")
    id_lote = Lote_visual.query.get(id)
    if id_lote == None:
        flash (f'Lote com id: {id}, não identificado -- Lote não Deletado!', category='success')
        return redirect(request.referrer)
    else:
        item = request.form.get("item")
        lote = request.form.get("lote_visual")
        referencia = request.form.get("referencia")
        quantidade = request.form.get("quantidade")
        quantidade = int(quantidade)
        quantidade = neg(quantidade)
        obs = request.form.get("obs")
        tipomov = "Baixa Manual"
        local = request.form.get("local")
        db.session.delete(id_lote)
        db.session.commit()
        Def_movimento_estoque(item, tipomov, lote, referencia, quantidade, obs)
        Def_ajuste_estoque(item,quantidade,"SAI",local)
        flash (f'Lote com id: {id}, excluido com sucesso', category='success')
        consulta = Lote_visual.query.filter_by(item = item).all()
   
        info = Def_cadastro_prod(item,A1)
    
    return  render_template('estoquer2.html', consulta = consulta, info=info, item = item)
    #return redirect(request.referrer)


@app.route('/estrutura_op/<numero_op_visual>/<numero_lote>', methods = ['GET','POST'])
def estrutura_op(numero_op_visual, numero_lote):
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    op = numero_op_visual
    lote = numero_op_visual + "/" + numero_lote
    itens_movimentados = Movimentos_estoque.query.filter_by(op_referencia = op).all()   
    op_dados = Ops_visual.query.filter_by(numero_op_visual = op).all()

    mov_op = Estrutura_op.query.filter_by(op_referencia = op).all()  
      
    return render_template("estrutura_op.html", itens_movimentados=itens_movimentados, lote=lote, op=op, op_dados=op_dados, mov_op=mov_op)


@app.route('/encerra_op', methods=['GET', 'POST'])
def encerra_op():
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    if request.method == 'POST':
        id = request.form.get('id')
        situacao = request.form.get('situacao')
        encerra = Ops_visual.query.get(id)  
        encerra.situação = situacao
        db.session.commit()
        if situacao == "Aberta":
            flash (f'Op Reaberta com sucesso', category='success')
        else:
            flash (f'Op Encerrada com sucesso', category='success')
    return redirect(url_for('ordens_producao_visual'))


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

    if  request.method == 'POST':
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
        
        flash (f'Lote transferido com sucesso', category='success')

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
    if not current_user.is_authenticated:
        return redirect( url_for('login'))
    item = request.form.get("estoque")
 
    Tqtda1 = Def_cadastro_prod(item,A1)
    Tqtdac = Def_cadastro_prod(item,AC) 
    Tqtdse = Def_cadastro_prod(item,SE)
    Tqtdcq = Def_cadastro_prod(item,CQ)
    Tqtdas = Def_cadastro_prod(item,AS)
    
    qtda1 = Tqtda1[2]
    qtdac = Tqtdac[2] 
    qtdse = Tqtdse[2]
    qtdcq = Tqtdcq[2]
    qtdas = Tqtdas[2]

    saldototal =  qtda1 + qtdac + qtdse + qtdcq + qtdas
    
    unidadeI = Tqtda1[3]

    convert =  Def_Convert_Unidade("Consulta", unidadeI)
    unidade = convert[0]
    fator = convert[2]
    qtda1 = qtda1 * fator
    qtdac = qtdac * fator 
    qtdse = qtdse * fator
    qtdcq = qtdcq * fator
    qtdas = qtdas * fator
    
    qtda1 = int(qtda1)
    qtdac = int(qtdac)
    qtdse = int(qtdse)
    qtdcq = int(qtdcq)
    qtdas = int(qtdas)

    qtdtol = qtda1 + qtdac + qtdse + qtdcq + qtdas

    if saldototal == 0:
        frase = ""
    else:    
        frase = (f'Saldo Total do Item: {item} = {qtdtol:.0f} {unidade} _ _||_ _ Omie = {locale.format_string("%1.3f", saldototal, grouping=True)} {unidadeI}')

    return  render_template('posicoes_estoque.html', frase = frase, Tqtda1 = Tqtda1,
                             qtda1 = qtda1, qtdac = qtdac, qtdse = qtdse, qtdcq = qtdcq,
                              qtdas = qtdas, unidade = unidade)

#=============================definições do diego =================================#    

@app.route('/teste_diego', methods = ['GET','POST'])
def teste_diego():
    item = request.form.get('teste_item')
    
    teste = Def_cadastro_prod(item, A1)
    
    id_produto = teste[0]
    if id_produto == None:
       id_produto = 0
    
    saldoFisico = teste[2]
    if saldoFisico == None:
       saldoFisico = 2
       
    caracter = Def_Caracter(id_produto)
    fino = caracter[0]
    peso = caracter[1]
    
    return render_template('teste.html',item = item, teste = teste, id_produto = id_produto,saldoFisico = saldoFisico, fino = fino, peso = peso)

# <=========================teste de saldo por ID===============================>
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

#===================Todas definições do diego prodx==================#  

def Def_cadastro_prod(item, local):
   item = item

    
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
   
   liga = cadastro.get('modelo')
   if liga == None:
       liga = "-"
   
   imagens = cadastro.get('modelo')
   if imagens == None:
       imagens = "-"
   

   
    
   data2 = {
                "call":"PosicaoEstoque",
                "app_key": app_key,
                "app_secret": app_secret,
                "param":[{
                      "codigo_local_estoque": local,
                      "id_prod": id_produto
                        }
                ]}
   response = requests.post(url=url_consulta_estoque, json=data2)
   cadastro_saldo = response.json()

   saldoFisico = cadastro_saldo.get('saldo')
   if saldoFisico == None:
       saldoFisico = 0

    
   return [id_produto, tipo, saldoFisico, unidade, valor_unitario, descricao, item, cliente, codigo_cliente, liga, imagens]

#===================definição de ajuste de estoque ==================#

def Def_ajuste_estoque(item,quan,tipomov,local):
    item = item
  
    cadastro = Def_cadastro_prod(item, local)
    
    tipo = cadastro[1]
    if tipo == None:
       tipo = "-"
                
    unidade = cadastro[3]
    if unidade == None:
       unidade = "-"

    id_produto = cadastro[0]
    if id_produto == None:
       id_produto = 0

    valor_unitario = cadastro[4]
    if valor_unitario == None:
       valor_unitario = 0.0001

    if valor_unitario == 0:
       valor_unitario = 0.0001

    if tipomov == "SAI":
        tipom = "Saida"
    else:
        tipom = "Entrada"

    convert = Def_Convert_Unidade(tipom, unidade)
        
    quan = quan * convert[1]
    
    
    if tipo == "Produtivo":
        data2 = {
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
        response = requests.post(url=url_ajuste_estoque, json=data2)
        ajuste = response.json()

        status = ajuste.get('codigo_status')
    else:
        status = "Não Produtivo"
    
    if status == None:
       status = "erro"
    elif status == "0":
       status = convert[1]

    
    #return render_template('temp1.html',cadastro = cadastro, cadastro_saldo = cadastro_saldo ,id_produto = id_produto, saldoFisico = saldoFisico, tipo = tipo)
    return [id_produto, tipo, status, unidade, valor_unitario]
#================definição de converção de Unidade================#
def Def_Convert_Unidade(tipom, unidade):
    fatoromie = 1
    fatorvisual = 1

    if tipom == "Entrada":
      if unidade == "MIL":
          unidadef = "PC"
          fatoromie = 1 / 1000
          fatorvisual = 1

      if unidade == "PC":
          unidadef = "PC"
          fatoromie = 1
          fatorvisual = 1

      if unidade == "UN":
          unidadef = "PC"
          fatoromie = 1
          fatorvisual = 1

      if unidade == "KG":
          unidadef = "GR"
          fatoromie = 1 / 1000
          fatorvisual = 1
        
    if tipom == "Saida":
      if unidade == "MIL":
          unidadef = "PC"
          fatoromie = 1 / 1000
          fatorvisual = 1
         
      if unidade == "PC":
          unidadef = "PC"
          fatoromie = 1
          fatorvisual = 1

      if unidade == "UN":
          unidadef = "PC"
          fatoromie = 1
          fatorvisual = 1

      if unidade == "KG":
          unidadef = "GR"
          fatoromie = 1 / 1000
          fatorvisual = 1
    if tipom == "Consulta":
      
      if unidade == "PC":
          unidadef = "PC"
          fatoromie = 1
          fatorvisual = 1

      if unidade == "UN":
          unidadef = "PC"
          fatoromie = 1
          fatorvisual = 1

      if unidade == "KG":
          unidadef = "GR"
          fatoromie = 1 # não usa
          fatorvisual = 1000
      
      if unidade == "MIL":
          unidadef = "PC"
          fatoromie = 1 # não usa
          fatorvisual = 1000
      else:
        unidadef = "PC"
        fatoromie = 1 # não usa
        fatorvisual = 1

          

    
    return [unidadef, fatoromie, fatorvisual]

#===================definição de caracteristicas =================#
def Def_Caracter(idprod):
 data = {
                "call":"ConsultarCaractProduto",
                "app_key": app_key,
                "app_secret": app_secret,
                "param":[{
                         "nCodProd": idprod,
                         "cCodIntProd": "",
                         "nCodCaract": 3638913624,
                         "cCodIntCaract": ""
                                          }
                ]}
 response = requests.post(url=url_caracter, json=data)
 fino = response.json()
 data2 = {
                "call":"ConsultarCaractProduto",
                "app_key": app_key,
                "app_secret": app_secret,
                "param":[{
                         "nCodProd": idprod,
                         "cCodIntProd": "",
                         "nCodCaract": 4086784228,
                         "cCodIntCaract": ""
                                          }
                ]}
 response = requests.post(url=url_caracter, json=data2)
 unitario = response.json()

 peso_fino = fino.get('cConteudo')
 peso_unitario = unitario.get('cConteudo')

    # caracter = Def_Caracter(id_produto)
    #     fino = caracter[0]
    #     peso = caracter[1]
    


 return [peso_fino, peso_unitario]

def Def_Caracter_alt(idprod, fino, peso):
 data = {
                "call":"AlterarCaractProduto",
                "app_key": app_key,
                "app_secret": app_secret,
                "param":[{
                         "nCodProd": idprod,
                         "cCodIntProd": "",
                         "nCodCaract": 3638913624,
                         "cCodIntCaract": "",
                         "cConteudo": fino,
                         "cExibirItemNF": "N",
                         "cExibirItemPedido": "N",
                         "cExibirOrdemProd": "N"
                         }
                        ]}
 response = requests.post(url=url_caracter, json=data)
 status_fino = response.json()
 data2 = {
                "call":"AlterarCaractProduto",
                "app_key": app_key,
                "app_secret": app_secret,
                "param":[{
                         "nCodProd": idprod,
                         "cCodIntProd": "",
                         "nCodCaract": 4086784228,
                         "cCodIntCaract": "",
                         "cConteudo": peso,
                         "cExibirItemNF": "N",
                         "cExibirItemPedido": "N",
                         "cExibirOrdemProd": "N"
                         }
                        ]}
 response = requests.post(url=url_caracter, json=data2)
 status_unitario = response.json()
 ffino = status_fino.get('cDesStatus')
 fpeso = status_unitario.get('cDesStatus')
 
 return f"Status {ffino} - {fpeso}"
#=====================alterar estrutura====================#
def Def_alterar_estrutura(item):
    id = Def_id_produto(item)

    data = {
            "call":"AlterarEstrutura",
            "app_key": app_key,
            "app_secret": app_secret,
            "param":[{
                    "idProduto": id,
                        "itemMalhaAlterar": [
                        {
                        "idMalha": 2430284968,
                        "idProdMalha": 2424594641,
                        "quantProdMalha": 0.05524,
                        "obsProdMalha": "Estrutura alterada por Calculo de OP 2"
                        }
                    ]
                    }
            ]}
    response = requests.post(url=url_estrutura, json=data)
    estrutura = response.json()
        
    return estrutura


#===================Consulta de estrutura==================#
def Def_consulta_estrutura(item):
    #item = request.form.get("item")
    
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
        
        return estrutura
#===================numero de op==================#

def Def_numero_op():
    numero = Sequencia_op.query.get('ops_numero')
    
    if numero is None:
        numero = Sequencia_op(tabela_campo='ops_numero', valor=10000, valor_anterior=9999)
        db.session.add(numero)
        db.session.commit()
    else:
        numero_op = numero.valor + 1
        numero.valor = numero.valor + 1
        numero.valor_anterior = numero.valor - 1
        db.session.commit()

    return numero.valor
#===================numero de lote==================#

def Def_numero_lote(op):
    if Sequencia_lote.query.get(op) == None:
        mod_numero = Sequencia_lote(op_visual= op, valor = 1, valor_anterior = 0)
        db.session.add(mod_numero)
        db.session.commit()
        valor = 1
    else: 
        numero = Sequencia_lote.query.get(op)
        valor = numero.valor + 1
        numero.valor = numero.valor + 1
        numero.valor_anterior = numero.valor - 1
        db.session.commit()

    return valor
#===================validar Código=======================#

def Def_item_ok(item):
   item_M = item.upper()     
   data = {
                "call":"ConsultarProduto",
                "app_key": app_key,
                "app_secret": app_secret,
                "param":[{
                    "codigo": item_M
                        }
                ]}
   response = requests.post(url=url_produtos, json=data)
   cadastro = response.json()
   retorno = cadastro.get('codigo')
   if retorno == item_M:
       ok="ok"
   else:
       ok="não cadastrado"
       
   return [ok, item_M]
#===================Definição de movimento de estoque==================#

def Def_movimento_estoque(item, tipo, lote_visual, referencia, quantidade, obs):
    if not current_user.is_authenticated:
        return redirect( url_for('login'))

    
    data_atual = date.today().strftime("%d/%m/%Y")
    hora_atual = datetime.now().strftime("%H:%M")
    usuario = current_user.name
    novo_movimento = Movimentos_estoque(item = item, tipo = tipo,
                                        lote_visual = lote_visual,
                                        referencia = referencia, 
                                        quantidade = quantidade, obs=obs,
                                        data_movimento = data_atual,
                                        hora_movimento = hora_atual,
                                        usuario = usuario)
    db.session.add(novo_movimento)  
    db.session.commit()
         
    return redirect(request.referrer)

#===================fim das definições do diego ==================#
def Def_locais(id_local):
        
        
    if id_local == 2436985075:
        local = "Estoque"
    elif id_local == 2511785274:
        local = "Acabamento"
    elif id_local == 4084861665:
        local = "Setor Cobre"
    elif id_local == 4085565942:
        local = "Qualidade"
    elif id_local == 4085566100:
        local = "Seleção"
    elif id_local == 4085566245:
        local = "Embalagem"
    elif id_local == 2407629011:
        local = "MKM"

    return local
#===================testes temporarios do diego ==================#
@app.route('/temp')
def temp_prod():
 return f" descrição = {Def_cadastro_prod('CBA-4000',A1)[5]} saldo = {Def_cadastro_prod('CBA-4000',A1)[2]}"

@app.route('/temp2')
def temp_ajust():
 return f" id_produto = {Def_ajuste_estoque('TESTE1235',33,'ENT',AC)[0]} status = {Def_ajuste_estoque('TESTE1235',33,'ENT',AS)[2]} erro = {Def_ajuste_estoque('TESTE1235',33,'ENT',AS)[5]}"

@app.route('/temp3')
def estrut_ajust():
 return f" id_produto = {Def_alterar_estrutura('CBA-4000')} - "

@app.route('/temp4')
def estrut_consult():
 return f" id_produto = {Def_consulta_estrutura('CBA-4000')} - "


#===================definições simples do diego ==================#
def Def_id_produto(item):
 return Def_cadastro_prod(item, A1)[0]

def Def_tipo(item):
 return Def_cadastro_prod(item, A1)[1]

def Def_saldoFisico(item, local):
 return Def_cadastro_prod(item, local)[2]

def Def_unidade(item):
 dados = Def_cadastro_prod(item, A1)
 unidade_omie = dados[3]
 unidade = Def_Convert_Unidade("Consulta", unidade_omie)[0]
 return [unidade, unidade_omie]

def Def_valor_unitario(item):
 return Def_cadastro_prod(item, A1)[4]

def Def_descricao(item):
 return Def_cadastro_prod(item, A1)[5]

 



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        db.session.commit()
    app.run(host='0.0.0.0', port=8080, debug=True)

 