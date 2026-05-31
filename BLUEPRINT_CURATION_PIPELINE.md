## 🔱 BLUEPRINT: Omega Engine — Data & Curation Pipeline

### 1. High-Level Overview
The Omega Engine's Data & Curation Pipeline is a robust, multi-stage system designed to ingest, process, enrich, and store diverse content from various sources into a unified knowledge base for entities. It comprises an **Intake Sentinel** responsible for monitoring and ingesting raw data, and a **Curation Pipeline** that transforms this raw data into structured, embedded, and contextualized `CuratedContent` objects, making them available for the `ModelGateway`, `MemoryStore`, `Qdrant`, and `Redis` streams. This pipeline ensures that entities have access to up-to-date, relevant, and intelligently processed information.

### 2. Intake Sentinel (Porting `intake_sentinel.py`)
- **Purpose in Omega Engine**: The Intake Sentinel will act as the primary entry point for raw, untriaged data. It will continuously monitor designated input directories (`data/inbox/`) for new files or events, applying initial categorization and moving data into the pipeline for further processing.
- **Core Functionality**:
    - **Directory Monitoring**: Implement a robust file system watcher (e.g., `watchdog` or `anyio.Path.watch`) to detect new files in `data/inbox/`.
    - **File Categorization**: Basic classification of incoming files (e.g., based on extension or initial content scan).
    - **Initial Triage**: Move files from `data/inbox/` to `data/processed/` for successful intake or `data/rejected/` for invalid formats/types.
- **Dependencies & AnyIO Migration**:
    - File system operations should be wrapped with `anyio.to_thread.run_sync` to prevent blocking the event loop, especially for I/O-intensive tasks like moving large files.
    - Consider `anyio.Path` for asynchronous file system interactions.
- **Directory Structure**:
    - `data/inbox/`: Monitored directory for new, raw content.
    - `data/processed/`: Staging area for content successfully ingested by the Intake Sentinel, awaiting Curation.
    - `data/rejected/`: For content that fails initial intake (e.g., unsupported file types, corrupt files).
- **Key Functions to Port/Adapt**:
    - `monitor_inbox()`: Asynchronous function to continuously watch `data/inbox/`.
    - `process_incoming_file(file_path)`: Handles initial file categorization and movement.
    - `move_to_processed(file_path)`: Moves a file to `data/processed/`.
    - `move_to_rejected(file_path)`: Moves a file to `data/rejected/`.

### 3. Curation Pipeline (Porting `curation_pipeline.py`)
- **Purpose in Omega Engine**: The Curation Pipeline transforms raw content from `data/processed/` into enriched, entity-ready `CuratedContent`. It leverages `ModelGateway` for advanced processing (summarization, entity extraction), `MemoryStore` for contextual recall, `Qdrant` for vector storage, and `Redis` for event propagation.
- **Core Functionality**:
    - **Content Processors**:
        - `_web_processor`: Fetches and parses web pages.
        - `_rss_processor`: Ingests and parses RSS/Atom feeds.
        - `_document_processor`: Handles various document types (PDFs, text files, etc.).
    - **Content Enrichment**: Utilize `ModelGateway` for LLM-based tasks (e.g., summarization, keyword extraction, sentiment analysis, entity linking).
    - **Embedding Generation**: Generate vector embeddings for curated content using the `ModelGateway`'s embedding capabilities.
    - **Scheduling**: Manage the fetching and processing of content from various sources.
    - **Storage**: Store processed `CuratedContent` in `MemoryStore` (short-term) and `Qdrant` (long-term vector storage).
    - **Event Propagation**: Publish curation events to `Redis` streams for real-time updates and inter-service communication.
- **Dependencies & AnyIO Migration**:
    - `aiohttp` for asynchronous web requests.
    - `feedparser` for RSS/Atom parsing (potentially wrap in `anyio.to_thread.run_sync`).
    - `BeautifulSoup` for HTML parsing (wrap in `anyio.to_thread.run_sync`).
    - Replace `asyncio.gather` with `anyio.create_task_group` for concurrent execution of processors.
    - Ensure all blocking I/O (e.g., file reads in `_document_processor`) are wrapped in `anyio.to_thread.run_sync`.
- **Managers Integration**:
    - `ModelGateway`: Used for LLM interactions (e.g., `model_gateway.generate_text()`, `model_gateway.generate_embeddings()`).
    - `MemoryStore`: For caching and short-term conversational context storage of `CuratedContent`.
    - `Qdrant`: For persistent vector storage of `CuratedContent` embeddings, enabling semantic search and retrieval.
    - `Redis`: For publishing curation events (e.g., "new content curated", "entity linked") to `Redis` streams, allowing other services to react in real-time.
- **Data Flow**:
    1. Raw content arrives in `data/inbox/`.
    2. Intake Sentinel moves it to `data/processed/`.
    3. Curation Pipeline selects content from `data/processed/`.
    4. Appropriate processor (`_web_processor`, `_rss_processor`, `_document_processor`) handles the raw content.
    5. Content is enriched using `ModelGateway` (summarization, entity extraction).
    6. Embeddings are generated via `ModelGateway`.
    7. `CuratedContent` objects are created.
    8. `CuratedContent` is stored in `MemoryStore` and `Qdrant`.
    9. A `Redis` event is published, signaling new curated content.
- **Key Functions to Port/Adapt**:
    - `curate_content(content_source)`: Main orchestration function.
    - `_web_processor(url)`: Fetches, parses, and enriches web content.
    - `_rss_processor(feed_url)`: Fetches, parses, and enriches RSS feed entries.
    - `_document_processor(file_path)`: Reads, parses, and enriches local documents.
    - `_generate_llm_insights(text)`: Uses `ModelGateway` for summarization/extraction.
    - `_generate_embeddings(text)`: Uses `ModelGateway` for embedding generation.
    - `_store_curated_content(curated_content)`: Stores in `MemoryStore` and `Qdrant`.
    - `_publish_curation_event(event_data)`: Publishes to `Redis`.
    - `_scheduler()`: Manages periodic content fetching from various sources.

### 4. Integration Points & Interfaces
- **Intake Sentinel to Curation Pipeline**:
    - The Intake Sentinel, after successfully moving a file to `data/processed/`, will trigger the Curation Pipeline. This can be achieved by:
        - Publishing a "new_file_processed" event to a `Redis` stream that the Curation Pipeline listens to.
        - Directly calling an asynchronous `curate_content` function within the Curation Pipeline, passing the path to the processed file.
- **Main Data Structures**:
    - `CuratedContent`: A dataclass or Pydantic model representing fully processed and enriched content. Should include:
        - `id`: Unique identifier (UUID).
        - `source_url` / `source_path`: Original source.
        - `title`: Title of the content.
        - `text_content`: Cleaned, extracted text.
        - `summary`: LLM-generated summary.
        - `keywords`: LLM-generated keywords.
        - `entities`: Extracted entities (people, places, things).
        - `embedding`: Vector embedding of the content.
        - `timestamp`: Curation timestamp.
        - `source_type`: (web, rss, document, etc.).
    - `ContentSource`: A dataclass or Pydantic model to define the origin of the content (e.g., URL for web, feed URL for RSS, file path for documents).
- **Error Propagation**:
    - Use structured logging (e.g., `src/omega/observability.py`) to record errors at each stage.
    - Exceptions should be caught and re-raised with additional context, allowing for clear debugging.
    - Failed items in the Intake Sentinel should go to `data/rejected/` with associated error logs.
    - The Curation Pipeline should handle individual item failures gracefully, continuing to process other items, and logging errors for failed curations.

### 5. Test Specifications
- **Intake Sentinel**:
    - **Unit Tests**:
        - `test_monitor_inbox_new_file`: Verifies detection of new files.
        - `test_process_incoming_file_valid`: Checks correct categorization and movement to `data/processed/`.
        - `test_process_incoming_file_invalid`: Checks correct movement to `data/rejected/` for invalid files.
        - `test_anyio_thread_safety`: Ensures blocking operations are wrapped correctly.
    - **Integration Tests**:
        - `test_end_to_end_intake`: Simulates a file landing in `inbox` and verifies its eventual presence in `processed` or `rejected`.
- **Curation Pipeline**:
    - **Unit Tests**:
        - `test_web_processor_success`: Mocks `aiohttp` and `BeautifulSoup` to test web content extraction and enrichment.
        - `test_rss_processor_success`: Mocks `feedparser` to test RSS content extraction.
        - `test_document_processor_text`: Tests text file processing.
        - `test_document_processor_pdf`: Tests (mocked) PDF processing.
        - `test_generate_llm_insights`: Mocks `ModelGateway` to verify LLM summarization/extraction.
        - `test_generate_embeddings`: Mocks `ModelGateway` to verify embedding generation.
        - `test_store_curated_content`: Mocks `MemoryStore` and `Qdrant` interactions.
        - `test_publish_curation_event`: Mocks `Redis` interaction.
        - `test_anyio_task_group`: Verifies concurrent execution with `anyio.create_task_group`.
    - **Integration Tests**:
        - `test_curation_pipeline_e2e_web`: Simulates processing a web URL, verifies storage in `Qdrant` and `Redis` event.
        - `test_curation_pipeline_e2e_document`: Simulates processing a document from `data/processed/`, verifies end-to-end flow.
        - `test_full_pipeline_resilience`: Introduces errors at various stages to test graceful degradation and error logging.

### 6. Effort Estimates
- **Intake Sentinel Porting**:
    - File system watcher and basic triage: 1-2 days
    - AnyIO migration & testing: 1 day
- **Curation Pipeline - Core Framework**:
    - Setting up `anyio.create_task_group`, basic data flow: 2 days
    - Integrating `ModelGateway` for LLM and embeddings: 3-4 days
    - Integrating `MemoryStore`, `Qdrant`, `Redis`: 3-4 days
- **Content Processors**:
    - `_web_processor` (basic fetch & parse): 2 days
    - `_rss_processor` (basic fetch & parse): 2 days
    - `_document_processor` (text, basic PDF): 3 days
- **Scheduling**:
    - Implementing a basic scheduling mechanism for content sources: 2 days
- **Testing**:
    - Unit tests for all components: 5-7 days
    - Integration tests: 3-5 days

Total Estimated Effort: Approximately 2-4 weeks for initial porting and re-implementation to a functional state.
