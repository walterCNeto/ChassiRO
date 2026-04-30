# Chassi Universal de RCSA — Web (landing + docs)

Pacote estático com landing institucional e documentação OpenAPI 3.1 da API.
Sem build step. Sem framework. Deploy em qualquer hosting de arquivos
estáticos (Cloudflare Pages, Netlify, Vercel, GitHub Pages, S3+CloudFront).

## Conteúdo

```
web/
├── index.html              Landing comercial
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

### Cloudflare Pages / Netlify / Vercel

Aponta o build pra essa pasta `web/` como diretório de saída. Sem build
command.

### GitHub Pages

Move o conteúdo pra `docs/` ou pra branch `gh-pages` e ativa Pages no repo.

### S3 + CloudFront

Sync direto:

```bash
aws s3 sync web/ s3://chassi.com.br/ --delete
aws cloudfront create-invalidation --distribution-id XXX --paths '/*'
```

## Domínios sugeridos

- `chassi.com.br` ou `chassi.wcn.com.br` — landing (`index.html`)
- `docs.chassi.com.br` ou rota `/docs` — Redoc (`docs.html`)
- `api.chassi.com.br` — API REST (não incluída neste pacote — exige backend)

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

A landing menciona endpoints (`api.chassi.com.br/v1/...`) que ainda não
existem em produção. Quando a API for hospedada, os exemplos de código
funcionarão diretamente. Até lá, eles servem como contrato visível.
