import asyncio
from concurrent.futures import ThreadPoolExecutor
from sentence_transformers import SentenceTransformer


model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')


executor = ThreadPoolExecutor(max_workers=2) 

def _compute_embedding(text: str) -> list[float]:
    return model.encode(text, normalize_embeddings=True).tolist()

async def get_embedding(text: str) -> list[float]:
    loop = asyncio.get_running_loop()
    vector = await loop.run_in_executor(executor, _compute_embedding, text)
    
    return vector