# Chassi de Controles Internos — Web (landing + docs)

Pacote estático com landing institucional e documentação OpenAPI 3.1 da API.
Sem build step. Sem framework. Deploy em qualquer hosting de arquivos
estáticos (Cloudflare Pages, Netlify, Vercel, GitHub Pages, S3+CloudFront).

## Conteúdo

```
web/
├── index.html              Landing
├── docs.html               Reference da API (Redoc)
├── openapi.yaml            Especificação OpenAPI 3.1
├── redoc.standalone.js     Redoc empacotado (sem CDN)
└── redoc.standalone.js.LICENSE.txt
```

## Como rodar local

Qualquer servidor estático serve. Por exemplo:

```bash
cd web
python3 -m http.server 8765
```

Abre em `http://localhost:8765`.

## Como deploy

### GitHub Pages (recomendado para projetos open source)

1. Settings → Pages no GitHub
2. Source: Deploy from branch
3. Branch: `main` · Folder: `/web`
4. Salvar — fica disponível em `https://walterCNeto.github.io/ChassiRO/`

### Cloudflare Pages / Netlify / Vercel

Aponta o build pra essa pasta `web/` como diretório de saída. Sem build
command.

### S3 + CloudFront (para hospedagem própria)

```bash
aws s3 sync web/ s3://seu-dominio/ --delete
aws cloudfront create-invalidation --distribution-id XXX --paths '/*'
```

## Estética

- **Tipografia**: Fraunces (serif display) + Manrope (sans body) + IBM Plex Mono
- **Paleta**: papel-tinta (`#f5f0e6` / `#1a1814`) com accent vinho-carimbo (`#9c2c25`)
- **Direção**: documento regulatório premium reimaginado — densidade editorial,
  marginalia, numeração romana de seções, carimbo SVG decorativo

## OpenAPI

`openapi.yaml` é a fonte da verdade do contrato da API:

- 20 paths agrupados em 7 tags (Catálogos, Normas, Processos, Riscos, Vínculos, Instância, Chassi)
- 18 schemas com exemplos
- 2 servers declarados (produção, homologação)
- Auth via `X-API-Key`

A spec é design-first — pode ser usada como contrato para implementação
backend (FastAPI, Express, qualquer geração automática de stubs).

## Atualizar Redoc

Para atualizar a versão do Redoc empacotado:

```bash
curl -L "https://registry.npmjs.org/redoc/-/redoc-X.Y.Z.tgz" -o redoc.tgz
tar xzf redoc.tgz
cp package/bundles/redoc.standalone.js web/redoc.standalone.js
cp package/bundles/redoc.standalone.js.LICENSE.txt web/
rm -rf redoc.tgz package
```

## Notas

A landing menciona endpoints (`api.example.com/v1/...`) que ainda não
existem hospedados publicamente. Quando a API for hospedada, os exemplos de
código funcionarão diretamente. Até lá, eles servem como contrato visível.

A landing também aponta diretamente pra o repositório no GitHub e pra o
guia de contribuição — quem quiser começar a contribuir, o caminho está na
landing.
