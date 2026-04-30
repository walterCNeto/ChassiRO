-- ============================================================
-- 099_versao.sql
-- Versionamento inicial do chassi
-- ============================================================

BEGIN;

INSERT INTO chassi_versions (id, version, released_at, notas, is_current) VALUES
('CV_0_1_0', '0.1.0', NOW(),
'Versao inicial do chassi universal de RCSA.

Cobertura:
- 12 reguladores
- 25 tipos de entidade
- 9 segmentos prudenciais (S1-S5 BCB + 4 SUSEP)
- 38 atividades canonicas
- ~30 normas estruturantes (Leis, CMN, BCB, CVM, SUSEP, ANBIMA)
- ~140 processos (P0+P1 universal/bancario completos; P2 seletivos; P0+P1 demais nucleos)
- ~70 riscos (R0+R1 universal completo; R0 demais nucleos)
- Vinculos qualificados norma-processo, norma-risco e processo-risco

Atencao: numeros, datas e status de normas devem ser revalidados contra
a base oficial dos reguladores antes de uso operacional.

Pendentes para v0.2:
- P3/P4 detalhados com controles-modelo
- Biblioteca de KRIs por risco
- Top-150 normas BACEN incluindo cartas-circulares
- Integracao com BacenProcedentes para indicadores de denuncia',
TRUE);

INSERT INTO chassi_changelog (version_id, change_type, entity_type, entity_id, description) VALUES
('CV_0_1_0', 'add', 'chassi', 'v0.1.0', 'Versao inicial completa do chassi universal');

COMMIT;
