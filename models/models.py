from config import db
from flask_login import UserMixin
from datetime import datetime
from pytz import timezone




# class Ops(db.Model):
#     __tablename__='ops'

#     id = db.Column(db.Integer, primary_key=True)   
#     numero_op = db.Column(db.String(50))
#     situação = db.Column(db.String(50))
#     item = db.Column(db.String(50))
#     descrição = db.Column(db.String(255))
#     quantidade = db.Column(db.Integer)
#     data_abertura = db.Column(db.String)
#     hora_abertura = db.Column(db.String)

#     lotes = db.relationship('Lote', backref='ops', lazy=True)


#     def __init__(self, numero_op, situação, item, descrição, quantidade, data_abertura, hora_abertura):
#         self.numero_op = numero_op
#         self.situação = situação
#         self.item = item
#         self.descrição = descrição
#         self.quantidade = quantidade
#         self.data_abertura = data_abertura
#         self.hora_abertura = hora_abertura

#     def __repr__(self):
#         return 'Ops: {} - {} - {} - {} - {} - {} - {} - {}' .format(self.id, self.numero_op, self.situação, self.item, self.descrição, 
#                                                                     self.quantidade, self.data_abertura, self.hora_abertura)
class Ops_visual(db.Model):
    __tablename__='ops_visual'

    id = db.Column(db.Integer, primary_key=True)   
    numero_op_visual = db.Column(db.String(50))
    situação = db.Column(db.String(50))
    item = db.Column(db.String(50))
    descrição = db.Column(db.String(255))
    quantidade = db.Column(db.Integer)
    peso_enviado = db.Column(db.Integer)
    peso_retornado = db.Column(db.Integer)
    fino_enviado = db.Column(db.Integer)
    fino_retornado = db.Column(db.Integer)
    data_abertura = db.Column(db.String(50))
    hora_abertura = db.Column(db.String(50))

    #lotes = db.relationship('Lote', backref='ops', lazy=True)


    def __init__(self, numero_op_visual, situação, item, descrição, quantidade, peso_enviado, peso_retornado, fino_enviado, fino_retornado, data_abertura, hora_abertura):
        self.numero_op_visual = numero_op_visual
        self.situação = situação
        self.item = item
        self.descrição = descrição
        self.quantidade = quantidade
        self.peso_enviado = peso_enviado
        self.peso_retornado = peso_retornado
        self.fino_enviado = fino_enviado
        self.fino_retornado = fino_retornado
        self.data_abertura = data_abertura
        self.hora_abertura = hora_abertura

    def __repr__(self):
        return 'Ops: {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {}' .format(self.id, self.numero_op_visual, self.situação, self.item, self.descrição, 
                                                                    self.quantidade, self.peso_enviado, self.peso_retornado, self.fino_enviado, self.fino_retornado, self.data_abertura, self.hora_abertura)


class Lote_visual(db.Model):
    __tablename__='lote_visual'

    id = db.Column(db.Integer, primary_key=True)
    referencia = db.Column(db.Integer, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    item = db.Column(db.String(50), nullable=False)
    lote_visual = db.Column(db.String(50), nullable=False)
    numero_lote = db.Column(db.String(50), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    peso = db.Column(db.Integer, nullable=False)
    fino = db.Column(db.Integer, nullable=False)
    local = db.Column(db.String(250), nullable=False)
    obs = db.Column(db.String(250))
    data_criacao = db.Column(db.String(50), nullable=False)
    

    def __init__(self, referencia, tipo, item, lote_visual, numero_lote, quantidade, peso, fino, local, obs, data_criacao):
        self.referencia = referencia
        self.tipo = tipo
        self.item = item
        self.lote_visual = lote_visual
        self.numero_lote = numero_lote
        self.quantidade = quantidade
        self.peso = peso
        self.fino = fino
        self.local = local
        self.obs = obs
        self.data_criacao = data_criacao
        

    def __repr__(self):
        return f"Lote(id={self.id}, referencia={self.referencia}, tipo={self.tipo},  item={self.item}, lote_visual='{self.lote_visual}', numero_lote='{self.numero_lote}', quantidade={self.quantidade})"

class Estrutura_op(db.Model):
    __tablename__='estrutura_op'

    id = db.Column(db.Integer, primary_key=True)
    op_referencia = db.Column(db.Integer, db.ForeignKey('ops_visual.id'), nullable=False)
    tipo_mov = db.Column(db.String(50)) 
    item_estrutura = db.Column(db.String(50))
    descricao_item = db.Column(db.String(255))
    quantidade_item = db.Column(db.Float)
    peso = db.Column(db.Float)
    fino = db.Column(db.Float)
    

    
    def __init__(self, op_referencia, tipo_mov, item_estrutura, descricao_item, 
                quantidade_item, peso, fino):  

        self.op_referencia = op_referencia
        self.tipo_mov = tipo_mov
        self.item_estrutura = item_estrutura
        self.descricao_item = descricao_item
        self.quantidade_item = quantidade_item
        self.peso = peso
        self.fino = fino
       

    def __repr__(self):
        return 'estrutura_op: {} - {} - {} - {} - {} - {} - {}' .format(self.op_referencia, self.tipo_mov, self.item_estrutura, self.descricao_item, self.quantidade_item, self.peso, self.fino)

class Sequencia_op(db.Model):
    __tablename__='sequencia_op'
    
    tabela_campo = db.Column(db.String(50), primary_key=True)
    valor = db.Column(db.Integer, nullable=False)
    valor_anterior = db.Column(db.Integer, nullable=False)

    def __init__(self, tabela_campo, valor, valor_anterior):

        self.tabela_campo = tabela_campo
        self.valor = valor
        self.valor_anterior = valor_anterior
    
    def __repr__(self):
        return 'sequencia: {} - {} - {}' .format(self.tabela_campo, self.valor, self.valor_anterior) 


class Sequencia_lote(db.Model):
    __tablename__='sequencia_lote'
    
    op_visual = db.Column(db.String(50), primary_key=True)
    valor = db.Column(db.Integer, nullable=False)
    valor_anterior = db.Column(db.Integer, nullable=False)

    def __init__(self, op_visual, valor, valor_anterior):

        self.op_visual = op_visual
        self.valor = valor
        self.valor_anterior = valor_anterior
    
    def __repr__(self):
        return 'sequencia: {} - {} - {}' .format(self.op_visual, self.valor, self.valor_anterior) 


class Movimentos_estoque(db.Model):
    __tablename__='Movimentos_estoque'

    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(50))
    tipo = db.Column(db.String(50))
    lote_visual = db.Column(db.String(50))
    referencia = db.Column(db.Integer)
    quantidade = db.Column(db.Integer)
    obs = db.Column(db.String(250))
    data_movimento = db.Column(db.String(50))
    hora_movimento = db.Column(db.String(50))
    usuario = db.Column(db.String(90))

    def __init__(self, item, tipo, lote_visual, referencia, quantidade, obs,  data_movimento, hora_movimento, usuario):  

        self.item = item
        self.tipo = tipo
        self.lote_visual = lote_visual
        self.referencia = referencia
        self.quantidade = quantidade
        self.obs = obs
        self.data_movimento = data_movimento
        self.hora_movimento = hora_movimento
        self.usuario = usuario


    def __repr__(self):
        return 'Movimentos_estoque: {} - {} - {} - {} - {} - {} - {} - {} - {}' .format(self.id, self.item, self.tipo, self.lote_visual,self.referencia, 
                self.quantidade,  self.obs, self.data_movimento, self.hora_movimento, self.usuario)



class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    def __init__(self, email, password, name):
        self.email = email
        self.password = password
        self.name = name



    def __repr__(self):
        return "<User %r>" % self.email



class Saldo_por_posicao(db.Model):
    __tablename__ = "saldo_por_posicao"

    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(50))
    descricao = db.Column(db.String(255))
    quantidade = db.Column(db.Integer)
    op = db.Column(db.String(50))
    lote = db.Column(db.String(50))
    operador = db.Column(db.String(50))
    posicao = db.Column(db.String(50))
    data_hora = db.Column(db.DateTime)

    def __init__(self, item, descricao, quantidade, op, lote, operador, posicao, data_hora=None):
        self.item = item
        self.descricao = descricao
        self.quantidade = quantidade
        self.op = op
        self.lote = lote
        self.operador = operador
        self.posicao = posicao
        if data_hora is None:
            data_hora = datetime.now(timezone('America/Sao_Paulo'))
        self.data_hora = data_hora

    def to_dict(self):
        data_hora_fmt = self.data_hora.strftime('%d/%m/%Y %H:%M:%S')
        return {'id': self.id,
                'item': self.item,
                'descricao': self.descricao,
                'quantidade': self.quantidade,
                'op': self.op,
                'lote': self.lote,
                'operador': self.operador,
                'posicao': self.posicao,
                'data_hora': data_hora_fmt}


