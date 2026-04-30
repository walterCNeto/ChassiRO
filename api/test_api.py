"""Validação end-to-end da API."""
import os, json, sys
os.environ['CHASSI_SNAPSHOT_PATH'] = '/home/claude/api-build/chassi.json'

from api.main import app
from fastapi.testclient import TestClient

passed = 0
failed = 0
def check(label, cond, detail=""):
    global passed, failed
    if cond:
        print(f"  PASS  {label}")
        passed += 1
    else:
        print(f"  FAIL  {label} -- {detail}")
        failed += 1

with TestClient(app) as c:
    print("=" * 60)
    print("VALIDACAO API CHASSI")
    print("=" * 60)

    print("\n[health]")
    r = c.get('/health')
    check('200', r.status_code == 200)
    check('version 0.1.0', r.json()['version'] == '0.1.0')
    check('28 normas', r.json()['counts']['normas'] == 28)

    print("\n[stats]")
    r = c.get('/v1/chassi/stats')
    d = r.json()
    check('200', r.status_code == 200)
    check('reguladores=12', d['reguladores_ativos'] == 12)
    check('processos=245', d['processos_total'] == 245)
    check('vinculos_np=97', d['vinculos_norma_processo'] == 97)
    check('vinculos_pr=68', d['vinculos_processo_risco'] == 68)

    print("\n[catalogos]")
    r = c.get('/v1/reguladores')
    check(f'12 reguladores (got {len(r.json())})', len(r.json()) == 12)

    r = c.get('/v1/tipos-entidade')
    check(f'25 tipos (got {len(r.json())})', len(r.json()) == 25)

    r = c.get('/v1/tipos-entidade?grupo=bancario')
    bancarios = len(r.json())
    check(f'tipos bancarios filtrados ({bancarios})', bancarios > 0 and bancarios < 25)

    r = c.get('/v1/segmentos')
    check(f'9 segmentos (got {len(r.json())})', len(r.json()) == 9)

    r = c.get('/v1/atividades')
    check(f'39 atividades (got {len(r.json())})', len(r.json()) == 39)

    print("\n[normas - filtro Banco S2]")
    r = c.get('/v1/normas?aplica_a=ENT_BANCO_MULTIPLO&segmento=S2')
    d = r.json()
    ids = {n['id'] for n in d}
    check(f'18 normas (got {len(d)})', len(d) == 18)
    check('RES_CMN_4502 (S1) ausente', 'RES_CMN_4502_16' not in ids)
    check('RES_CMN_4557 presente', 'RES_CMN_4557_17' in ids)
    check('RES_CMN_4943 presente', 'RES_CMN_4943_21' in ids)
    check('CIR_BCB_3978 presente', 'CIR_BCB_3978_20' in ids)

    print("\n[normas - filtro DTVM]")
    r = c.get('/v1/normas?aplica_a=ENT_DTVM')
    d = r.json()
    ids = {n['id'] for n in d}
    check(f'15 normas (got {len(d)})', len(d) == 15)
    check('RES_CVM_35 presente', 'RES_CVM_35_21' in ids)
    check('RES_CVM_50 presente', 'RES_CVM_50_21' in ids)
    check('RES_CVM_175 presente', 'RES_CVM_175_22' in ids)
    check('COD_ANBIMA_DISTR presente', 'COD_ANBIMA_DISTR' in ids)
    check('RES_CMN_4193 ausente', 'RES_CMN_4193_13' not in ids)
    check('RES_CMN_4943 ausente', 'RES_CMN_4943_21' not in ids)
    check('CIR_BCB_3978 ausente (PLD bancario)', 'CIR_BCB_3978_20' not in ids)

    print("\n[norma detalhe]")
    r = c.get('/v1/normas/RES_CMN_4557_17')
    d = r.json()
    check('200', r.status_code == 200)
    check('artigos>0', len(d['artigos']) > 0)
    check('aplicabilidade_tipo>0', len(d['aplicabilidade_tipo_entidade']) > 0)
    check('vinculos_processo>0', len(d['vinculos_processo']) > 0)
    check('vinculos_risco>0', len(d['vinculos_risco']) > 0)

    print("\n[norma 404]")
    r = c.get('/v1/normas/INEXISTENTE')
    check('404', r.status_code == 404)

    print("\n[busca textual]")
    r = c.get('/v1/normas?busca=PLD')
    d = r.json()
    check(f'busca PLD retorna ({len(d)})', len(d) > 0)

    print("\n[processos]")
    r = c.get('/v1/processos')
    check(f'245 processos (got {len(r.json())})', len(r.json()) == 245)

    r = c.get('/v1/processos?nucleo=B')
    bancarios = len(r.json())
    check(f'nucleo=B ({bancarios} processos)', 0 < bancarios < 245)

    r = c.get('/v1/processos?nucleo=B&nivel_max=1')
    p0p1 = len(r.json())
    check(f'B nivel_max=1 ({p0p1} <= bancarios)', p0p1 <= bancarios)

    r = c.get('/v1/processos/P0.B.2')
    d = r.json()
    check('processo P0.B.2 tem children', len(d['children']) > 0)
    check('processo P0.B.2 tem vinculos_norma', len(d['vinculos_norma']) > 0)
    check('processo P0.B.2 tem vinculos_risco', len(d['vinculos_risco']) > 0)

    print("\n[riscos]")
    r = c.get('/v1/riscos')
    check(f'90 riscos (got {len(r.json())})', len(r.json()) == 90)

    r = c.get('/v1/riscos?categoria=credito')
    cred = len(r.json())
    check(f'categoria=credito ({cred} riscos)', cred > 0)

    r = c.get('/v1/riscos/R0.U.1')
    d = r.json()
    check('R0.U.1 OK', r.status_code == 200)

    print("\n[vinculos]")
    r = c.get('/v1/vinculos/norma-processo')
    check(f'97 vinculos NP (got {len(r.json())})', len(r.json()) == 97)

    r = c.get('/v1/vinculos/norma-processo?tipo=primaria')
    primarias = len(r.json())
    check(f'primarias filtradas ({primarias})', 0 < primarias < 97)

    r = c.get('/v1/vinculos/processo-risco?materialidade_min=5')
    mat5 = len(r.json())
    check(f'materialidade=5 ({mat5} pares)', mat5 == 34)

    print("\n[POST /v1/instancia - banco S2]")
    r = c.post('/v1/instancia', json={
        'tipo_entidade': 'ENT_BANCO_MULTIPLO',
        'segmento': 'S2',
        'atividades': ['ATV_DEPOSITO_VISTA', 'ATV_CAMBIO_COMERCIAL', 'ATV_CREDITO_PJ']
    })
    d = r.json()
    check('200', r.status_code == 200)
    check(f'normas={d["contagens"]["normas"]} (esperado >= 18)', d['contagens']['normas'] >= 18)
    check(f'processos={d["contagens"]["processos"]} (>0)', d['contagens']['processos'] > 0)
    check(f'riscos={d["contagens"]["riscos"]} (>0)', d['contagens']['riscos'] > 0)
    check('versao=0.1.0', d['versao_chassi'] == '0.1.0')

    print("\n[POST /v1/instancia - DTVM]")
    r = c.post('/v1/instancia', json={
        'tipo_entidade': 'ENT_DTVM',
        'atividades': ['ATV_DISTRIBUICAO_VM']
    })
    d = r.json()
    check('200', r.status_code == 200)
    check(f'normas={d["contagens"]["normas"]} (>0)', d['contagens']['normas'] > 0)

    print("\n[POST /v1/instancia - input invalido]")
    r = c.post('/v1/instancia', json={'tipo_entidade': 'XXX'})
    check('400', r.status_code == 400)

    print("\n[chassi]")
    r = c.get('/v1/chassi/version')
    check('200', r.status_code == 200)

    r = c.get('/v1/chassi/versions')
    check(f'1 versao (got {len(r.json())})', len(r.json()) == 1)

    print("\n[snapshot download]")
    r = c.get('/v1/chassi/snapshot.json')
    check(f'200 ({len(r.content)} bytes)', r.status_code == 200 and len(r.content) > 100000)

    print("\n[OpenAPI]")
    r = c.get('/openapi.json')
    spec = r.json()
    paths = spec['paths']
    check(f'{len(paths)} paths definidos', len(paths) >= 18)

    print("\n[docs UI]")
    r = c.get('/docs')
    check('Swagger UI OK', r.status_code == 200 and b'swagger' in r.content.lower())

    print()
    print("=" * 60)
    print(f"RESULTADO: {passed} passou, {failed} falhou")
    print("=" * 60)
    sys.exit(0 if failed == 0 else 1)
