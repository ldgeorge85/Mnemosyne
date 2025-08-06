"""
Prompt templates for processing Outline documentation.

AI Agents: These prompts are specifically designed for knowledge base content.
Modify or extend based on your documentation structure.
"""

# For summarizing documentation pages
DOCUMENT_SUMMARY_PROMPT = """
Analyze this documentation page and extract key information:

Title: {title}
Content: {text}

Please extract:
1. **Main Purpose**: What is this document about?
2. **Key Concepts**: Important terms, systems, or ideas explained
3. **Action Items**: Any procedures, steps, or tasks described
4. **Related Topics**: Other documents or concepts referenced
5. **Technical Details**: APIs, configurations, code examples mentioned

Format as structured data for knowledge base storage.
"""

# For processing search results
SEARCH_RESULT_PROMPT = """
Given these search results for query "{query}":

{results}

Synthesize the information to answer the query by:
1. Identifying the most relevant documents
2. Extracting key facts that answer the query
3. Noting any conflicting information
4. Suggesting related topics to explore

Provide a comprehensive answer based on the documentation.
"""

# For extracting knowledge from collections
COLLECTION_ANALYSIS_PROMPT = """
Analyze this documentation collection:

Collection: {name}
Description: {description}
Documents: {document_list}

Extract:
1. **Collection Purpose**: What knowledge domain does this cover?
2. **Key Topics**: Main subjects covered in this collection
3. **Document Relationships**: How documents relate to each other
4. **Knowledge Gaps**: What seems to be missing?

This helps organize the knowledge base effectively.
"""

# For incremental updates
UPDATE_EXTRACTION_PROMPT = """
A document has been updated:

Previous Version Summary: {previous_summary}
New Content: {new_text}
Changed At: {updated_at}

Extract:
1. **What Changed**: Key differences from previous version
2. **New Information**: Facts or procedures added
3. **Removed Information**: What was deleted (if apparent)
4. **Impact**: How this affects related documentation

This maintains knowledge base currency.
"""

# For technical documentation
TECHNICAL_DOC_PROMPT = """
Extract technical details from this documentation:

Title: {title}
Content: {text}

Focus on:
1. **Code Examples**: Any code snippets or configurations
2. **API Endpoints**: REST APIs, GraphQL queries, webhooks
3. **Environment Variables**: Configuration settings
4. **Dependencies**: Required services, libraries, tools
5. **Commands**: CLI commands, scripts, procedures
6. **Error Patterns**: Common errors and solutions

Structure for technical knowledge retrieval.
"""

# For FAQ generation
FAQ_GENERATION_PROMPT = """
Based on this documentation:

{documents}

Generate frequently asked questions by:
1. Identifying common use cases
2. Extracting how-to procedures
3. Finding troubleshooting steps
4. Noting best practices

Format as Q&A pairs for quick reference.
"""


def get_prompt(prompt_type: str, **kwargs) -> str:
    """
    Get formatted prompt for specific use case.
    
    AI Agents: Available prompt types:
    - document_summary: Summarize a single document
    - search_result: Process search results
    - collection_analysis: Analyze a collection
    - update_extraction: Process document updates
    - technical_doc: Extract technical details
    - faq_generation: Generate FAQs from docs
    
    Example:
        prompt = get_prompt("document_summary", 
                           title=doc["title"], 
                           text=doc["text"])
    """
    prompts = {
        "document_summary": DOCUMENT_SUMMARY_PROMPT,
        "search_result": SEARCH_RESULT_PROMPT,
        "collection_analysis": COLLECTION_ANALYSIS_PROMPT,
        "update_extraction": UPDATE_EXTRACTION_PROMPT,
        "technical_doc": TECHNICAL_DOC_PROMPT,
        "faq_generation": FAQ_GENERATION_PROMPT
    }
    
    template = prompts.get(prompt_type)
    if not template:
        raise ValueError(f"Unknown prompt type: {prompt_type}")
    
    return template.format(**kwargs)