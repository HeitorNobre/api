# API de Consulta de Boletos

Este projeto foi desenvolvido como parte do meu primeiro projeto comercial. Ele consiste em uma API que permite a consulta de boletos pendentes para unidades condominiais, retornando links de pagamento.

## Endpoints

### `/obter_dados`

**Método**: `GET`  
**Descrição**: Este endpoint pesquisa no banco de dados informações correspondentes ao CPF e nome do condomínio fornecidos, retornando o link para pagamento de boletos pendentes, caso existam.

**Parâmetros**:
- `cpf` (obrigatório): CPF do morador.
- `nome_condominio` (obrigatório): Nome do condomínio.

**Exemplo de requisição**:

```bash
GET /obter_dados?cpf=12345678900&nome_condominio=Condominio+Exemplo
```
**Exemplo de resposta**:
```json
{
  "links_cobranca": [
    "https://exemplo.com/segunda-via-boleto/12345"
  ]
}
```
**Em caso de não haver pendências**:
```JSON
{
  "links_cobranca": "sem cobranças pendentes"
}
```

## Tecnologias Utilizadas

- **Flask**: Framework web utilizado para construir a API.
- **FuzzyWuzzy**: Utilizado para realizar correspondências aproximadas entre o nome do condomínio informado e os registros no banco de dados.
- **Cachetools**: Para melhorar a performance, utilizando cache nas chamadas à API externa.
- **Requests**: Para realizar as requisições HTTP à API externa.
- **dotenv**: Para gerenciar variáveis de ambiente de maneira segura.

## Contribuições
- Este projeto está aberto para visualização pública, mas não permite alterações diretas. No entanto, fique à vontade para clonar o repositório e sugerir melhorias via pull requests.
