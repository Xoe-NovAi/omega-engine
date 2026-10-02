#!/usr/bin/env python3
"""
Standalone Qwen3-Embedding-0.6B ONNX Server

Runs outside Ollama to bypass MAX_LOADED_MODELS=1 deadlock.
Supports native 1024-dim embeddings via Ollama qwen3-embedding:0.6b.
Instruction-aware: queries get "Instruct: {task}\nQuery:{text}", documents raw.

Critical: Disables ONNX Runtime spin-wait (allow_spinning=0) to avoid
CPU burn on hybrid CPUs (i7-13620H P-core/E-core). Uses spin_duration_us=1000
+ spin_backoff_max=8 per ONNX Runtime best practices for hybrid CPUs.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional, Literal

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import onnxruntime as ort
from tokenizers import Tokenizer
from huggingface_hub import hf_hub_download, snapshot_download

# ─── Prevent ONNX Runtime spin-wait BEFORE importing ort ─────────
# On hybrid CPUs (e.g. Intel i7-13620H 6P+4E), run the embedding server on the
# 4 Gracemont E-cores (logical CPUs 12-15). This keeps the 6 P-cores + HT siblings
# (logical CPUs 0-11) 100% unencumbered for Ollama LLM inference.
#
# E-core affinity allocation:
# - Logical CPUs: 12, 13, 14, 15
# - Thread count: 4 (1 thread per physical E-core; Gracemont has no HT)
# - Spin-wait disabled: prevents OS thread thrash and barrier convoys
E_CORE_AFFINITY = {12, 13, 14, 15}
NUM_E_CORE_THREADS = 4

def configure_cpu_affinity():
    """Pin process to Gracemont E-cores (12-15) if available on Linux."""
    if hasattr(os, "sched_setaffinity"):
        try:
            available_cpus = set(range(os.cpu_count() or 16))
            if E_CORE_AFFINITY.issubset(available_cpus):
                os.sched_setaffinity(0, E_CORE_AFFINITY)
                logging.info(f"CPU affinity locked to Gracemont E-cores: {os.sched_getaffinity(0)}")
            else:
                logging.warning(f"Target E-cores {E_CORE_AFFINITY} not subset of available {available_cpus}; keeping default affinity")
        except Exception as e:
            logging.warning(f"Could not set CPU affinity: {e}")

configure_cpu_affinity()

os.environ.setdefault("OMP_NUM_THREADS", str(NUM_E_CORE_THREADS))
os.environ.setdefault("KMP_AFFINITY", "granularity=fine,compact,1,0")
os.environ.setdefault("KMP_BLOCKTIME", "0")

# ─── Configuration ──────────────────────────────────────────────
MODEL_REPO = "onnx-community/Qwen3-Embedding-0.6B-ONNX"
MODEL_DIR = Path(os.getenv("EMBED_MODEL_DIR", "/home/xnai/Documents/Projects/omega-engine-alpha/models/embedding/qwen3-0.6b-onnx"))
ONNX_MODEL_NAME = "model_int8.onnx"  # INT8 quantized for CPU efficiency (~614 MB)
TRUNCATE_DIM = int(os.getenv("TRUNCATE_DIM", "1024"))  # canonical: native 1024, no MRL truncation
MAX_LENGTH = 8192
BATCH_SIZE = 32

# Qwen3-Embedding uses left padding and last-token pooling (EOS pooling)
# MEAN POOLING DESTROYS QUALITY for decoder-based embedders like Qwen3
PADDING_SIDE = "left"
POOLING = "last_token"  # REQUIRED for Qwen3-Embedding
NORMALIZE = True

# Default instruction for queries (recommended by Qwen for retrieval tasks)
DEFAULT_INSTRUCTION = "Given a web search query, retrieve relevant passages that answer the query"

# ─── Logging ────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("embedding_server")

# ─── Pydantic Models ────────────────────────────────────────────
class EmbedRequest(BaseModel):
    inputs: List[str] = Field(..., min_length=1, max_length=BATCH_SIZE)
    input_type: Literal["query", "document"] = "document"
    instruction: Optional[str] = None
    truncate_dim: Optional[int] = None

class EmbedResponse(BaseModel):
    embeddings: List[List[float]]
    dimensions: int
    model: str = "qwen3-embedding-0.6b-onnx"

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    dimensions: int
    truncate_dim: int

# ─── Model Loader ───────────────────────────────────────────────
class Qwen3EmbeddingONNX:
    def __init__(self, model_dir: Path, model_name: str = ONNX_MODEL_NAME, truncate_dim: int = TRUNCATE_DIM):
        self.model_dir = model_dir
        self.model_path = model_dir / "onnx" / model_name
        self.truncate_dim = truncate_dim
        self.session: Optional[ort.InferenceSession] = None
        self.tokenizer: Optional[Tokenizer] = None
        self._load()

    def _load(self):
        """Load ONNX model and tokenizer with optimal CPU settings."""
        log.info(f"Loading model from {self.model_path}")
        
        # Ensure model exists
        if not self.model_path.exists():
            raise FileNotFoundError(f"ONNX model not found at {self.model_path}. Run download first.")
        
        # ONNX Runtime session - CPU execution provider with optimization
        # Pin to E-cores: 4 Gracemont cores (12-15), 4 threads, spin-wait disabled
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        sess_options.intra_op_num_threads = NUM_E_CORE_THREADS  # Dedicated to 4 physical E-cores (12-15)
        sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        
        # Disable spin-wait (prevents barrier convoy on hybrid CPUs)
        sess_options.add_session_config_entry("session.intra_op.allow_spinning", "0")
        sess_options.add_session_config_entry("session.inter_op.allow_spinning", "0")
        # Alternative (also valid): time-bounded spin with exponential backoff
        # sess_options.add_session_config_entry("session.intra_op.spin_duration_us", "1000")
        # sess_options.add_session_config_entry("session.intra_op.spin_backoff_max", "8")
        
        providers = ["CPUExecutionProvider"]
        self.session = ort.InferenceSession(str(self.model_path), sess_options, providers=providers)
        log.info(f"ONNX session loaded with providers: {self.session.get_providers()}")
        log.info(f"Intra-op threads: {sess_options.intra_op_num_threads}, Execution mode: ORT_SEQUENTIAL, Spinning: DISABLED")
        
        # Load tokenizer from local files (tokenizer files are in main repo, not onnx subfolder)
        tokenizer_path = self.model_dir / "tokenizer.json"
        if tokenizer_path.exists():
            self.tokenizer = Tokenizer.from_file(str(tokenizer_path))
        else:
            # Fallback: load from HF hub
            self.tokenizer = Tokenizer.from_pretrained(MODEL_REPO)
        log.info("Tokenizer loaded")

    def _prepare_inputs(self, texts: List[str], input_type: str, instruction: Optional[str]) -> List[str]:
        """Prepare texts with instruction prefix for queries."""
        if input_type == "query":
            instr = instruction or DEFAULT_INSTRUCTION
            return [f"Instruct: {instr}\nQuery:{t}" for t in texts]
        return texts  # Documents: no instruction prefix

    def _tokenize(self, texts: List[str]) -> dict:
        """Tokenize with left padding, truncation. Returns inputs for ONNX including KV cache."""
        encoded = self.tokenizer.encode_batch(texts)
        
        # Pad to max length (left padding for Qwen)
        max_len = min(max(len(e.ids) for e in encoded), MAX_LENGTH)
        batch_size = len(texts)
        
        input_ids = []
        attention_mask = []
        
        for e in encoded:
            ids = e.ids[:max_len]
            mask = e.attention_mask[:max_len]
            
            # Left padding
            pad_len = max_len - len(ids)
            if pad_len > 0:
                pad_id = self.tokenizer.token_to_id("<|endoftext|>") or 0
                ids = [pad_id] * pad_len + ids
                mask = [0] * pad_len + mask
            
            input_ids.append(ids)
            attention_mask.append(mask)
        
        input_ids_arr = np.array(input_ids, dtype=np.int64)
        attention_mask_arr = np.array(attention_mask, dtype=np.int64)
        
        # Build position_ids (required for Qwen)
        position_ids = np.arange(max_len, dtype=np.int64).reshape(1, -1).repeat(batch_size, axis=0)
        
        # Build empty past_key_values for prefill (past_seq_len = 0)
        # Shape: [batch, num_heads=8, past_seq_len=0, head_dim=128]
        past_kvs = {}
        for i in range(28):
            past_kvs[f'past_key_values.{i}.key'] = np.zeros((batch_size, 8, 0, 128), dtype=np.float32)
            past_kvs[f'past_key_values.{i}.value'] = np.zeros((batch_size, 8, 0, 128), dtype=np.float32)
        
        return {
            "input_ids": input_ids_arr,
            "attention_mask": attention_mask_arr,
            "position_ids": position_ids,
            **past_kvs,
        }

    def _pool(self, last_hidden: np.ndarray, attention_mask: np.ndarray) -> np.ndarray:
        """Pool last hidden state: last_token or mean."""
        if POOLING == "last_token":
            # Left padding: last token is at the end (non-padded position)
            seq_lens = attention_mask.sum(axis=1)
            batch_indices = np.arange(last_hidden.shape[0])
            pooled = last_hidden[batch_indices, seq_lens - 1]
        else:  # mean pooling
            mask_expanded = attention_mask[:, :, np.newaxis]
            pooled = (last_hidden * mask_expanded).sum(axis=1) / mask_expanded.sum(axis=1).clip(min=1)
        return pooled

    def embed(self, texts: List[str], input_type: str = "document", 
              instruction: Optional[str] = None, truncate_dim: Optional[int] = None) -> np.ndarray:
        """Generate embeddings for texts."""
        if not texts:
            return np.array([])
        
        # Prepare texts with instruction
        prepared = self._prepare_inputs(texts, input_type, instruction)
        
        # Tokenize
        inputs = self._tokenize(prepared)
        
        # Run ONNX inference
        outputs = self.session.run(None, inputs)
        last_hidden = outputs[0]  # Shape: (batch, seq_len, hidden_size=1024)
        
        # Pool
        pooled = self._pool(last_hidden, inputs["attention_mask"])
        
        # Normalize
        if NORMALIZE:
            norms = np.linalg.norm(pooled, axis=1, keepdims=True)
            pooled = pooled / norms.clip(min=1e-12)
        
        # Matryoshka truncation
        dim = truncate_dim or self.truncate_dim
        if dim and dim < pooled.shape[1]:
            pooled = pooled[:, :dim]
        
        return pooled.astype(np.float32)


# ─── FastAPI App ────────────────────────────────────────────────
app = FastAPI(title="Qwen3-Embedding-0.6B ONNX Server", version="0.1.0")
model: Optional[Qwen3EmbeddingONNX] = None


@app.on_event("startup")
async def startup():
    global model
    try:
        model = Qwen3EmbeddingONNX(MODEL_DIR)
        log.info("Model loaded successfully")
    except Exception as e:
        log.error(f"Failed to load model: {e}")
        # Don't raise - let health endpoint report status


@app.get("/health", response_model=HealthResponse)
async def health():
    loaded = model is not None and model.session is not None
    return HealthResponse(
        status="healthy" if loaded else "loading",
        model_loaded=loaded,
        dimensions=TRUNCATE_DIM,
        truncate_dim=TRUNCATE_DIM,
    )


@app.post("/embed", response_model=EmbedResponse)
async def embed(req: EmbedRequest):
    if model is None or model.session is None:
        raise HTTPException(503, "Model not loaded")
    
    try:
        embeddings = model.embed(
            req.inputs,
            input_type=req.input_type,
            instruction=req.instruction,
            truncate_dim=req.truncate_dim,
        )
        return EmbedResponse(
            embeddings=embeddings.tolist(),
            dimensions=embeddings.shape[1],
        )
    except Exception as e:
        log.error(f"Embedding error: {e}")
        raise HTTPException(500, str(e))


# ─── CLI Download Helper ────────────────────────────────────────
def download_model():
    """Download model files from Hugging Face Hub (blocking; anyio-pure entry)."""
    log.info(f"Downloading {MODEL_REPO} to {MODEL_DIR}")

    # Download entire repo (includes tokenizer + onnx subfolder)
    snapshot_download(
        repo_id=MODEL_REPO,
        local_dir=MODEL_DIR,
        local_dir_use_symlinks=False,
        resume_download=True,
        max_workers=8,
    )
    log.info("Download complete")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "download":
        download_model()
    else:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8090, log_level="info")