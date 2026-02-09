# GraphRAG Entity Resolution for Statistical Metadata

This tool performs automated entity resolution and relationship discovery for statistical metadata concepts using a hybrid approach combining semantic similarity (embeddings) and Large Language Model (LLM) reasoning.

## Features

- **Discovers multiple relationship types:**
  - `owl:sameAs` - Equivalent concepts
  - `skos:broader` - Hierarchical relationships (broader concepts)
  - `skos:narrower` - Hierarchical relationships (narrower concepts)
  - `skos:related` - Related concepts

- **Hybrid approach:**
  - Semantic similarity filtering using embeddings
  - LLM-based relationship verification with confidence scoring
  - Batch processing for efficiency

- **Output:**
  - RDF/Turtle file with inferred relationships
  - Console and file logging
  - Hierarchy visualization

## Prerequisites

- Python 3.8+
- Access to a SPARQL endpoint containing statistical metadata
- Google API key (for Gemini models)

## Installation

1. Install required dependencies:

```bash
pip install -r requirements.txt
```

The required packages include:
- `SPARQLWrapper` - SPARQL endpoint communication
- `rdflib` - RDF graph manipulation
- `google-generativeai` - Google Gemini API
- `langchain-google-genai` - LangChain integration for Google models
- `scikit-learn` - Cosine similarity calculations
- `numpy` - Numerical operations

## Configuration

### 1. Set Your Google API Key

Open `main.py` and locate the `main()` function. Replace the placeholder with your actual Google API key:

```python
def main():
    """Main execution function."""
    GOOGLE_API_KEY = "PUT YOUR GOOGLE API KEY HERE"  # <-- Change this
    SPARQL_ENDPOINT = "http://localhost:3030/#/dataset/sirusa/query"
    ...
```

**To get a Google API key:**
- Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
- Sign in with your Google account
- Create a new API key
- Copy and paste it into the code

### 2. Configure SPARQL Endpoint (Optional)

If your SPARQL endpoint is different from the default, update it in the `main()` function:

```python
SPARQL_ENDPOINT = "http://your-endpoint-url/sparql"
```

**Common SPARQL endpoints:**
- Apache Jena Fuseki: `http://localhost:3030/dataset/query`
- Ontop: `http://localhost:8080/sparql`
- Remote endpoint: `https://your-server.com/sparql`

### 3. Customize Source Concepts (Optional)

To change which concepts are analyzed, modify the `get_all_concepts()` method in the `StatisticalMetadataEntityResolver` class:

**Option A: Load all concepts** (remove the VALUES clause):

```python
def get_all_concepts(self) -> List[Dict]:
    """Retrieve all concepts from the SPARQL endpoint."""
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?concept ?label ?definition ?source WHERE {
        ?concept rdfs:label ?label .
        ?concept rdfs:comment ?definition .
        FILTER(isIRI(?concept)) . 
    } 
    """
    ...
```

**Option B: Select specific concepts** (modify the VALUES list):

```python
def get_all_concepts(self) -> List[Dict]:
    """Retrieve all concepts from the SPARQL endpoint."""
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?concept ?label ?definition ?source WHERE {
        VALUES ?concept {
            <https://your-namespace.org/concept/1>
            <https://your-namespace.org/concept/2>
            <https://your-namespace.org/concept/3>
            # Add your concept URIs here
        }
        ?concept rdfs:label ?label .
        ?concept rdfs:comment ?definition .
        FILTER(isIRI(?concept)) . 
    } 
    """
    ...
```

**Option C: Filter by pattern** (use FILTER with regex):

```python
def get_all_concepts(self) -> List[Dict]:
    """Retrieve all concepts from the SPARQL endpoint."""
    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?concept ?label ?definition ?source WHERE {
        ?concept rdfs:label ?label .
        ?concept rdfs:comment ?definition .
        FILTER(isIRI(?concept)) .
        FILTER(REGEX(STR(?concept), "your-pattern-here"))
    } 
    """
    ...
```

### 4. Adjust Parameters (Optional)

You can fine-tune the resolution process by modifying parameters in the `find_relationships()` method:

```python
relationships = self.find_relationships(
    concepts, 
    semantic_threshold=0.70,  # Cosine similarity threshold (0.0-1.0)
    batch_size=10              # Number of concepts per LLM batch
)
```

- **semantic_threshold**: Higher values (0.8-0.9) = more strict, fewer candidates
- **batch_size**: Larger batches = fewer API calls but longer processing time

## Running the Tool

Execute the main script:

```bash
cd "entity resolution"
python main.py
```

## Output

The tool generates several outputs:

### 1. RDF/Turtle File
- **Filename**: `entity_relationships.ttl`
- **Contains**: All discovered relationships as RDF triples
- **Format**: Turtle syntax

### 2. Log File
- **Filename**: `graphrag_resolution_YYYYMMDD_HHMMSS.log`
- **Contains**: 
  - Progress updates
  - Semantic similarity scores
  - LLM reasoning for each relationship
  - Confidence scores
  - Summary statistics

### 3. Console Output
- Real-time progress monitoring
- Relationship discoveries
- Hierarchy visualization
- Summary statistics

## Example Output

```
================================================================================
Statistical Metadata Relationship Discovery using GraphRAG
Finding: owl:sameAs, skos:broader, skos:narrower, skos:related
================================================================================

Retrieving concepts from SPARQL endpoint...
Found 100 concepts

================================================================================
DISCOVERING RELATIONSHIPS
================================================================================

Processing concept 1/100: Population Growth Rate

Found 5 relationships:
  ✓ Birth Rate
    Type: related
    Confidence: 0.85
    Reasoning: Both indicators measure demographic dynamics...

================================================================================
Relationship discovery complete!
Results saved to: entity_relationships.ttl

Triples created:
  owl:sameAs: 12
  skos:broader: 8
  skos:narrower: 8
  skos:related: 15
================================================================================
```

## Understanding the Algorithm

The tool implements a two-phase approach:

1. **Semantic Filtering** (Phase 1):
   - Embeds all concept descriptions using Google's embedding model
   - Calculates cosine similarity between all pairs
   - Filters candidates above the threshold (default: 0.70)

2. **LLM Verification** (Phase 2):
   - Sends candidate pairs to Gemini LLM in batches
   - LLM determines relationship type and confidence
   - Only relationships with confidence ≥ 0.70 are retained

## Troubleshooting

### Common Issues

**1. SPARQL Connection Error**
```
Error: HTTPError 404 or Connection refused
```
- Verify your SPARQL endpoint is running
- Check the endpoint URL format
- Test the endpoint in a web browser first

**2. Google API Error**
```
Error: Invalid API key
```
- Verify your API key is correct
- Check if the API key has proper permissions
- Ensure you've enabled the Generative Language API

**3. Out of Memory**
```
MemoryError or killed
```
- Reduce batch_size parameter
- Process fewer concepts at once
- Use a machine with more RAM

**4. No Relationships Found**
```
Found 0 relationships
```
- Lower the semantic_threshold (try 0.60)
- Check if concepts have proper labels and definitions
- Verify concepts are in the same domain/subject area

## Advanced Usage

### Custom Relationship Types

To add new relationship types, modify the `RelationType` enum:

```python
class RelationType(Enum):
    SAME_AS = "sameAs"
    BROADER = "broader"
    NARROWER = "narrower"
    RELATED = "related"
    NONE = "none"
    # Add your custom types here
```

### Different LLM Models

To use a different Gemini model, update the initialization:

```python
self.llm = GoogleGenerativeAI(
    model="gemini-pro",  # or "gemini-1.5-pro", etc.
    temperature=0.2
)
```

## License

See the LICENSE file in the root directory.

## Citation

If you use this tool in your research, please cite appropriately.

## Support

For issues and questions, please refer to the main project repository.
