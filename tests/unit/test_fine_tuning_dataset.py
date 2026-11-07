import json
import os
import pytest

pytestmark = pytest.mark.unit

DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "fine_tuning",
    "persona_vox_dataset.jsonl",
)


def test_fine_tuning_dataset_file_exists():
    assert os.path.exists(DATASET_PATH), f"Arquivo não encontrado: {DATASET_PATH}"


def test_fine_tuning_dataset_has_minimum_50_examples():
    lines = []
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    assert len(lines) >= 50, f"Dataset tem apenas {len(lines)} registros, mínimo exigido: 50"


def test_fine_tuning_dataset_structure_and_uniqueness():
    seen_ids = set()

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            record = json.loads(line)

            # Validação de campos obrigatórios
            for required_field in ["id", "category", "instruction", "input", "output", "messages"]:
                assert required_field in record, f"Linha {idx} sem campo {required_field}"

            # Verificação de unicidade do ID
            record_id = record["id"]
            assert record_id not in seen_ids, f"ID duplicado encontrado: {record_id}"
            seen_ids.add(record_id)

            # Conteúdo não-vazio
            assert len(record["input"].strip()) > 5
            assert len(record["output"].strip()) > 20

            # Validação da lista messages para formato chat
            messages = record["messages"]
            assert isinstance(messages, list)
            assert len(messages) >= 3
            roles = [m["role"] for m in messages]
            assert "system" in roles
            assert "user" in roles
            assert "assistant" in roles
