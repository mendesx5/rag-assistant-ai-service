import numpy as np

from app.rag.embeddings import get_embedder


def cosine_similarity(a: list[float], b: list[float]) -> float:
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


question = "Quantos dias de férias eu tenho?"
candidates = [
    "O colaborador tem direito a trinta dias de descanso anual remunerado.",
    "As despesas de viagem devem ser reembolsadas em até dez dias úteis.",
    "O estacionamento da empresa fica no subsolo.",
]

embedder = get_embedder()
question_vector = embedder.embed_query(question)
print(f"Vector size: {len(question_vector)}\n")

for text, vector in zip(candidates, embedder.embed_documents(candidates)):
    print(f"{cosine_similarity(question_vector, vector):.3f}  {text}")