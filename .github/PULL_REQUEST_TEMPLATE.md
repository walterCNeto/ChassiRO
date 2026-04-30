# Descrição

(o que esse PR muda, em uma ou duas frases)

# Tipo

- [ ] Adiciona/atualiza norma no catálogo
- [ ] Corrige vínculo ou aplicabilidade
- [ ] Adiciona/atualiza processo ou risco
- [ ] Bug fix técnico (schema, export, landing, docs)
- [ ] Documentação
- [ ] Outro:

# Issue relacionada

Closes #

# Como validar

```bash
# comandos para confirmar que a mudança funciona
cd backend
make reset
make stats
```

Resultados esperados:

- (números do `v_chassi_stats` que devem mudar)
- (queries que devem retornar o novo conteúdo)

# Checklist

- [ ] Eu rodei `make reset` localmente e o seed carregou sem erro
- [ ] `make stats` retorna números coerentes com a mudança
- [ ] Toda norma adicionada tem URL oficial no campo `url_oficial`
- [ ] Toda mudança de vínculo está justificada na descrição do PR
- [ ] Atualizei o `CHANGELOG.md` quando a mudança é relevante para usuários
