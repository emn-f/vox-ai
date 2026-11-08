import pytest
from unittest.mock import MagicMock, patch
from src.core.semantica import eh_saudacao, semantica
from src.core.db.retrieval import (
    eh_pergunta_desenvolvedor,
    recuperar_contexto_inteligente,
    TOPICOS_EXCLUSIVOS_DEV,
)
from src.config import TAMANHO_VETOR_SEMANTICO


class TestSaudacoesBypass:
    """Testes para detecção de saudações e bypass de busca vetorial."""

    @pytest.mark.parametrize(
        "texto",
        [
            "hey",
            "Hey",
            "HEY!",
            "oi",
            "oie",
            "olá",
            "olá!",
            "ola",
            "hello",
            "hi",
            "bom dia",
            "bom dia!",
            "boa tarde",
            "boa noite",
            "opa",
            "tudo bem?",
            "como vai?",
            "oi tudo bem",
            "ola vox",
            "hey como vai",
            "",
            "   ",
        ],
    )
    def test_eh_saudacao_positivo(self, texto: str):
        assert eh_saudacao(texto) is True

    @pytest.mark.parametrize(
        "texto",
        [
            "Como retificar o nome no cartório?",
            "Qual o endereço da Casa Marielle Franco em Salvador?",
            "O que diz a resolução do MEC sobre nome social na chamada?",
            "Sofri discriminação, o que posso fazer?",
            "Como contribuir com o projeto no GitHub?",
            "Qual a história do dia 17 de maio de 1990?",
        ],
    )
    def test_eh_saudacao_negativo(self, texto: str):
        assert eh_saudacao(texto) is False

    def test_semantica_bypasses_rag_em_saudacao(self):
        """Verifica que 'hey' retorna (None, None, None) imediatamente sem chamar Gemini nem DB."""
        with patch("src.core.semantica.configurar_api_gemini") as mock_gemini:
            resultado = semantica("hey")
            assert resultado == (None, None, None)
            mock_gemini.assert_not_called()

        with patch("src.core.semantica.configurar_api_gemini") as mock_gemini:
            resultado = semantica("Olá! Tudo bem?")
            assert resultado == (None, None, None)
            mock_gemini.assert_not_called()


class TestFiltroDevRetrieval:
    """Testes para blindagem contra vazamento de dados técnicos de dev."""

    @pytest.mark.parametrize(
        "pergunta, esperado",
        [
            ("Como retificar o registro civil?", False),
            ("Onde buscar acolhimento em Salvador?", False),
            ("Qual o horário do ambulatório?", False),
            ("Como posso contribuir no GitHub?", True),
            ("Como rodar o projeto localmente com uv run?", True),
            ("Onde configuro o secrets.toml?", True),
            ("Quais são os padrões de commit do repositório?", True),
        ],
    )
    def test_eh_pergunta_desenvolvedor(self, pergunta: str, esperado: bool):
        assert eh_pergunta_desenvolvedor(pergunta) is esperado

    def test_recuperar_contexto_filtra_dev_chunks_para_usuario_comum(self):
        """Para perguntas que não são de dev, chunks com tópicos técnicos devem ser expurgados."""
        mock_chunks = [
            {
                "kb_id": "vox-kb-0318",
                "topico": "Como Contribuir",
                "descricao": "Configure as credenciais em .streamlit/secrets.toml e rode uv run streamlit run vox_ai.py",
                "similarity": 0.85,
            },
            {
                "kb_id": "vox-kb-0322",
                "topico": "Padrões de Commit",
                "descricao": "Use Conventional Commits como feat: e fix:",
                "similarity": 0.82,
            },
            {
                "kb_id": "vox-kb-0100",
                "topico": "Retificação de Nome",
                "descricao": "O Provimento 73/2018 do CNJ autoriza a alteração de prenome e gênero diretamente em cartório.",
                "similarity": 0.80,
            },
        ]

        with patch("src.core.db.retrieval.buscar_referencias_db", return_value=mock_chunks):
            vetor = [0.1] * TAMANHO_VETOR_SEMANTICO
            contexto, fonte, ids = recuperar_contexto_inteligente(
                vetor,
                query_texto="Como faço para mudar meu nome nos documentos?",
            )

            assert contexto is not None
            assert "Provimento 73/2018" in contexto
            assert "secrets.toml" not in contexto
            assert "Conventional Commits" not in contexto
            assert all(item["kb_id"] != "vox-kb-0318" for item in ids)

    def test_recuperar_contexto_permite_dev_chunks_quando_usuario_pergunta_dev(self):
        """Para perguntas de desenvolvimento explícitas, chunks técnicos são preservados."""
        mock_chunks = [
            {
                "kb_id": "vox-kb-0318",
                "topico": "Como Contribuir",
                "descricao": "Configure as credenciais em .streamlit/secrets.toml e rode uv run streamlit run vox_ai.py",
                "similarity": 0.85,
            },
        ]

        with patch("src.core.db.retrieval.buscar_referencias_db", return_value=mock_chunks):
            vetor = [0.1] * TAMANHO_VETOR_SEMANTICO
            contexto, fonte, ids = recuperar_contexto_inteligente(
                vetor,
                query_texto="Como posso rodar o código e contribuir no GitHub?",
            )

            assert contexto is not None
            assert "secrets.toml" in contexto
            assert ids[0]["kb_id"] == "vox-kb-0318"
