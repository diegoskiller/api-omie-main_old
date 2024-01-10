<h1>APLICAÇÃO PARA CONTROLE DE ORDENS DE PRODUÇÃO PARA FÁBRICA</h1>
<p>Essa aplicação permite a criação de ordens de produção para fabricação de produtos em uma industria. </p>
<p>Ela esta integrada com uma api externa do ERP Omie, de onde os itens são importados assim com suas estruturas e saldo em estoque </p>

<h2>FUNCIONALIDADES</h2>
<p>  • Criação de OPs (ordens de produção), onde é possivel adcionar os itens consumidos como materia prima sendo esses itens importados das estruturas cadastradas no ERP Omie, ou adcionado manualmente direto na aplicação </p>
<p>  • É possivel abrir, fechar e editar ordens de produção, atrelando lotes a elas, consumindo as materias primas utilizadas e registrando as movimentações em banco de dado relacional </p>
<p>  • Tanto as OPs, lotes, movimentações e saldo de itens produzidos são salvos em um banco SQL utilizando a ORM SQLAlchemy </p>
<p>  • Existe alguns armazéns cadastrados (ex: Estoque, controle de qualidade, expedição, etc..). Apos produzir uma OP total ou parcialmente o saldo do produto fabricado é salvo e um desses armazéns escolhido pelo usuário, depois disso é possivel transfirir entre todos os armazéns </p>
<p>  • É possivel consultar a lista de itens cadastrados no ERP Omie, assim como as estruturas, saldo dos itens, e outras informaçoes atravez do consumo da API disponibilizada pelo Omie </p>
<p>  • Sistema de login, com proteção de rotas e registro de qual usuário realizou determinadas ações no sistema </p>
<p>  • É acessar o deploy de uma demo no seguinte linkhttps://sistema-ytvz.onrender.com. Por ser um deploy free tier pode apresentar lentidão </p>


<h2>PASSOS PARA EXECUTAR A APLICAÇÃO.</h2>
<p>  • É recomendado criar um ambiente virtual para executar essa aplicação (venv) </p>
<p>  • Rodar o comando pip install requirements.txt para instalar as dependencias (pode ser preciso rodar como pip3 install requirements.txt) </p>
<p>  • Na pasta raiz execute o comando python3 app.py (ou  python app.py) </p>
<p>  • No navegador acessar o endereço localhost:3333 (por default abrirar na porta 3333) </p>
  
  
 
  
