"""Errors for the Nexova RAG pipeline.

Messages name configuration variables. They never include secret values.
"""


class RagError(Exception):
    """Base error for retrieval and generation."""


class EmbeddingNotConfigured(RagError):
    """The embeddings call cannot run because its configuration is empty."""

    def __init__(self) -> None:
        super().__init__(
            "Embeddings are not configured. Set EMBEDDING_MODEL_ID, "
            "EMBEDDING_BASE_URL and EMBEDDING_API_KEY, using a different model "
            "ID from GENERATION_MODEL_ID. For a local open-source index only, "
            "set RAG_EMBED_BACKEND=fastembed. That local model is not the "
            "4Geeks embeddings model."
        )


class GenerationNotConfigured(RagError):
    """The generation call cannot run because its configuration is empty."""

    def __init__(self) -> None:
        super().__init__(
            "The generation model is not configured. Set GENERATION_MODEL_ID, "
            "GENERATION_BASE_URL and GENERATION_API_KEY. The ID must differ "
            "from the embeddings model. No answer was invented."
        )


class ModelIdConflict(RagError):
    """Embedding and generation were pointed at the same model ID."""

    def __init__(self) -> None:
        super().__init__(
            "EMBEDDING_MODEL_ID and GENERATION_MODEL_ID must be different. "
            "Embeddings and generation are separate calls."
        )


class EmbeddingCallFailed(RagError):
    """The embeddings endpoint failed or returned an unusable vector."""


class GenerationCallFailed(RagError):
    """The generation endpoint failed or returned an empty answer."""


class CorpusError(RagError):
    """The company corpus is missing or cannot be chunked safely."""
