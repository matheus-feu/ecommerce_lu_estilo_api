{
  "username": "joaosilva",
  "email": "joao.silva@email.com",
  "first_name": "João",
  "last_name": "Silva",
  "cpf": "12345678901",
  "password": "senhaSegura123"
}

Cadastro de Conta: O usuário cria uma conta no sistema (com e-mail, senha, etc).
Cadastro de Cliente: Após autenticar, o usuário preenche os dados de cliente (nome, CPF, etc), vinculando esses dados à sua conta.
Assim, uma conta pode existir sem ser cliente, mas todo cliente está vinculado a uma conta. Isso permite separar autenticação (conta) dos dados pessoais (cliente).


Cadastro de Conta:
O usuário preenche e envia os dados de cadastro (e-mail, senha, etc).


Validação de E-mail:
O sistema envia um e-mail de verificação. O usuário precisa clicar no link para ativar a conta.


Login:
Após validar o e-mail, o usuário faz login e recebe um token JWT.


Cadastro de Cliente:
Só com a conta autenticada (token JWT válido), o usuário pode acessar o endpoint de cadastro de cliente.