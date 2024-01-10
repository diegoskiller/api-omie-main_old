from config import db
from flask_login import UserMixin
from datetime import datetime
from pytz import timezone




class Ops(db.Model):
    __tablename__='ops'

    id = db.Column(db.Integer, primary_key=True)   
    numero_op = db.Column(db.String(50))
    situação = db.Column(db.String(50))
    item = db.Column(db.String(50))
    descrição = db.Column(db.String(255))
    quantidade = db.Column(db.Integer)
    data_abertura = db.Column(db.String(255))
    hora_abertura = db.Column(db.String(255))

    lotes = db.relationship('Lote', backref='ops', lazy=True)


    def __init__(self, numero_op, situação, item, descrição, quantidade, data_abertura, hora_abertura):
        self.numero_op = numero_op
        self.situação = situação
        self.item = item
        self.descrição = descrição
        self.quantidade = quantidade
        self.data_abertura = data_abertura
        self.hora_abertura = hora_abertura

    def __repr__(self):
        return 'Ops: {} - {} - {} - {} - {} - {} - {} - {}' .format(self.id, self.numero_op, self.situação, self.item, self.descrição, 
                                                                    self.quantidade, self.data_abertura, self.hora_abertura)

class Lote(db.Model):
    __tablename__='lote'

    id = db.Column(db.Integer, primary_key=True)
    op_referencia = db.Column(db.Integer, db.ForeignKey('ops.id'), nullable=False)
    lote = db.Column(db.String(50), nullable=False)
    numero_lote = db.Column(db.String(50), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    peso = db.Column(db.Integer, nullable=False)
    data_fabricacao = db.Column(db.String(255), nullable=False)
    data_validade = db.Column(db.String(255), nullable=False)


    def __init__(self, op_referencia, lote, numero_lote, quantidade, peso, data_fabricacao, data_validade):
        self.op_referencia = op_referencia
        self.lote = lote
        self.numero_lote = numero_lote
        self.quantidade = quantidade
        self.peso = peso
        self.data_fabricacao = data_fabricacao
        self.data_validade = data_validade

    def __repr__(self):
        return f"Lote(id={self.id}, op_referencia={self.op_referencia}, numero_lote='{self.numero_lote}', quantidade={self.quantidade})"

class Estrutura_op(db.Model):
    __tablename__='estrutura_op'

    id = db.Column(db.Integer, primary_key=True)
    op_referencia = db.Column(db.Integer, db.ForeignKey('ops.id'), nullable=False)
    item_estrutura = db.Column(db.String(50))
    descricao_item = db.Column(db.String(255))
    quantidade_item = db.Column(db.Float)    

    
    def __init__(self, op_referencia, item_estrutura, descricao_item, 
                quantidade_item):  

        self.op_referencia = op_referencia
        self.item_estrutura = item_estrutura
        self.descricao_item = descricao_item
        self.quantidade_item = quantidade_item
       

    def __repr__(self):
        return 'Movimentos_estoque: {} - {} - {} - {}' .format(self.op_referencia, self.item_estrutura, self.descricao_item,self.quantidade_item)


class Movimentos_estoque(db.Model):
    __tablename__='movimentos_estoque'

    id = db.Column(db.Integer, primary_key=True)
    item_movimento = db.Column(db.String(50))
    numero_lote = db.Column(db.String(50))
    descricao = db.Column(db.String(255))
    op_referencia = db.Column(db.Integer)
    item_referencia = db.Column(db.String(50))
    saldo_anterior = db.Column(db.Integer)
    quantidade_movimento = db.Column(db.Integer)
    saldo_atual = db.Column(db.Integer)
    data_movimento = db.Column(db.String(255))
    hora_movimento = db.Column(db.String(255))

    def __init__(self, item_movimento, numero_lote, descricao, op_referencia, 
                item_referencia, saldo_anterior, quantidade_movimento, saldo_atual,  data_movimento, hora_movimento):  

        self.item_movimento = item_movimento
        self.numero_lote = numero_lote
        self.descricao = descricao
        self.op_referencia = op_referencia
        self.item_referencia = item_referencia
        self.saldo_anterior = saldo_anterior
        self.quantidade_movimento = quantidade_movimento
        self.saldo_atual = saldo_atual
        self.data_movimento = data_movimento
        self.hora_movimento = hora_movimento


    def __repr__(self):
        return 'Movimentos_estoque: {} - {} - {} - {} - {} - {} - {} - {} - {} - {}' .format(self.id, self.item_movimento, self.descricao, self.op_referencia, 
                self.item_referencia, self.saldo_anterior, self.quantidade_movimento,  self.saldo_atual, self.data_movimento, self.hora_movimento)



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

        db.create_all()
        db.session.commit()

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

db.create_all()
db.session.commit()
