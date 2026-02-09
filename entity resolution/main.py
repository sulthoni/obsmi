"""
GraphRAG Entity Resolution for Statistical Metadata with Hierarchical Relations
Finds relationships between concepts:
- owl:sameAs (equivalent concepts)
- skos:broader/narrower (hierarchical relationships)
"""

"""
LOGIC CODE FOR ENTITY RESOLUTION AND RELATIONSHIP DISCOVERY
Algorithm 1: GraphRAG Entity Resolution with Hierarchical Relation Discovery

Input:
  SPARQL endpoint E
  similarity threshold τ
  LLM confidence threshold κ (e.g., 0.70)
  batch size B

Output:
  RDF graph G_out containing inferred links (sameAs, broader/narrower, related)
  relationship list R

1:  C ← SPARQL_FETCH_CONCEPTS(E)
    // each c ∈ C has fields: uri, label, definition, source

2:  for each concept c_i ∈ C do
3:      t_i ← desc(c_i) = CONCAT(label_i, definition_i, "Source:", source_i)
4:      e_i ← EMBED(t_i)                     // cached embedding lookup
5:  end for

6:  S ← COSINE_SIMILARITY_MATRIX({e_i} for i=1..n)

7:  R ← ∅
8:  for i ← 1 to n do
9:      Cand_i ← ∅
10:     for j ← i+1 to n do
11:         if S[i,j] ≥ τ then
12:             Cand_i ← Cand_i ∪ {c_j}
13:         end if
14:     end for

15:     if Cand_i = ∅ then continue end if

16:     Partition Cand_i into batches {Batch_i^1, Batch_i^2, ..., Batch_i^k} of size B

17:     for each batch Batch_i^b do
18:         Rel_b ← LLMRel(c_i, Batch_i^b)
            // returns only relations deemed significant by the model prompt

19:         for each (c_j, r_ij, γ_ij, ρ_ij) ∈ Rel_b do
20:             if γ_ij ≥ κ then
21:                 R ← R ∪ {(c_i, c_j, r_ij, γ_ij, ρ_ij)}
22:             end if
23:         end for
24:     end for
25: end for

26: G_out ← ∅
27: for each (c_i, c_j, r_ij, γ_ij, ρ_ij) ∈ R do
28:     u_i ← URI(c_i.uri); u_j ← URI(c_j.uri)
29:     if r_ij = SAME_AS then
30:         ADD_TRIPLE(G_out, u_i, owl:sameAs, u_j)
31:         ADD_TRIPLE(G_out, u_j, owl:sameAs, u_i)
32:     else if r_ij = BROADER then
33:         // interpretation used in the implementation:
34:         // "concept i is broader than concept j"
35:         ADD_TRIPLE(G_out, u_j, skos:broader, u_i)
36:         ADD_TRIPLE(G_out, u_i, skos:narrower, u_j)
37:     else if r_ij = NARROWER then
38:         // "concept i is narrower than concept j"
39:         ADD_TRIPLE(G_out, u_i, skos:broader, u_j)
40:         ADD_TRIPLE(G_out, u_j, skos:narrower, u_i)
41:     else if r_ij = RELATED then
42:         ADD_TRIPLE(G_out, u_i, skos:related, u_j)
43:         ADD_TRIPLE(G_out, u_j, skos:related, u_i)
44:     end if

45:     // provenance/trace comment (implementation attaches comment to u_i)
46:     comment ← FORMAT("Confidence=%.3f; %s", γ_ij, ρ_ij)
47:     ADD_TRIPLE(G_out, u_i, rdfs:comment, comment)
48: end for

49: return (G_out, R)
"""

import os
from typing import List, Dict, Tuple, Set, Literal
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, Namespace, Literal as RDFLiteral, URIRef
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
from enum import Enum
import sys
from datetime import datetime


class RelationType(Enum):
    """Types of relationships that can be inferred."""
    SAME_AS = "sameAs"
    BROADER = "broader"
    NARROWER = "narrower"
    RELATED = "related"
    NONE = "none"


class TeeLogger:
    """Class to write output to both console and file."""
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, 'w', encoding='utf-8')
    
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    
    def flush(self):
        self.terminal.flush()
        self.log.flush()
    
    def close(self):
        self.log.close()


class StatisticalMetadataEntityResolver:
    """
    Resolves entity relationships in statistical metadata using GraphRAG.
    Identifies: owl:sameAs, skos:broader, skos:narrower relationships.
    """
    
    def __init__(self, sparql_endpoint: str, google_api_key: str, log_file: str = None):
        os.environ["GOOGLE_API_KEY"] = google_api_key
        genai.configure(api_key=google_api_key)
        
        self.sparql = SPARQLWrapper(sparql_endpoint)
        self.sparql.setReturnFormat(JSON)
        
        self.llm = GoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0.2)
        self.embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
        
        # Namespaces for statistical metadata
        self.SDMX = Namespace("http://purl.org/linked-data/sdmx/2009/concept#")
        self.QB = Namespace("http://purl.org/linked-data/cube#")
        self.STAT = Namespace("http://example.org/stats/")
        
        # Cache for embeddings
        self.embedding_cache = {}
        
        # Setup logging
        if log_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = f"entity_resolution_log_{timestamp}.txt"
        
        self.logger = TeeLogger(log_file)
        sys.stdout = self.logger
        print(f"Logging to file: {log_file}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

    def __del__(self):
        """Cleanup: restore stdout and close log file."""
        if hasattr(self, 'logger'):
            sys.stdout = self.logger.terminal
            self.logger.close()

    
    def get_all_concepts(self) -> List[Dict]:
        """Retrieve all concepts from the SPARQL endpoint."""
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?concept ?label ?definition ?source WHERE {
  		  VALUES ?concept {
            <https://bps.go.id/metadata/sirusa/product/42384>
            <https://bps.go.id/metadata/sirusa/product/40333>
            <https://bps.go.id/metadata/sirusa/product/5424>
            <https://bps.go.id/metadata/sirusa/product/67729>
            <https://bps.go.id/metadata/sirusa/product/66837>
            <https://bps.go.id/metadata/sirusa/product/15440>
            <https://bps.go.id/metadata/sirusa/product/48411>
            <https://bps.go.id/metadata/sirusa/product/46970>
            <https://bps.go.id/metadata/sirusa/product/58734>
            <https://bps.go.id/metadata/sirusa/product/37916>
            <https://bps.go.id/metadata/sirusa/product/52634>
            <https://bps.go.id/metadata/sirusa/product/15745>
            <https://bps.go.id/metadata/sirusa/product/446>
            <https://bps.go.id/metadata/sirusa/product/37085>
            <https://bps.go.id/metadata/sirusa/product/55941>
            <https://bps.go.id/metadata/sirusa/product/44882>
            <https://bps.go.id/metadata/sirusa/product/12916>
            <https://bps.go.id/metadata/sirusa/product/62056>
            <https://bps.go.id/metadata/sirusa/product/14728>
            <https://bps.go.id/metadata/sirusa/product/11904>
            <https://bps.go.id/metadata/sirusa/product/40837>
            <https://bps.go.id/metadata/sirusa/product/45542>
            <https://bps.go.id/metadata/sirusa/product/36670>
            <https://bps.go.id/metadata/sirusa/product/24086>
            <https://bps.go.id/metadata/sirusa/product/57978>
            <https://bps.go.id/metadata/sirusa/product/55827>
            <https://bps.go.id/metadata/sirusa/product/63439>
            <https://bps.go.id/metadata/sirusa/product/12971>
            <https://bps.go.id/metadata/sirusa/product/29473>
            <https://bps.go.id/metadata/sirusa/product/10246>
            <https://bps.go.id/metadata/sirusa/product/29125>
            <https://bps.go.id/metadata/sirusa/product/35415>
            <https://bps.go.id/metadata/sirusa/product/40520>
            <https://bps.go.id/metadata/sirusa/product/31216>
            <https://bps.go.id/metadata/sirusa/product/30918>
            <https://bps.go.id/metadata/sirusa/product/11468>
            <https://bps.go.id/metadata/sirusa/product/49639>
            <https://bps.go.id/metadata/sirusa/product/29161>
            <https://bps.go.id/metadata/sirusa/product/42783>
            <https://bps.go.id/metadata/sirusa/product/64001>
            <https://bps.go.id/metadata/sirusa/product/46273>
            <https://bps.go.id/metadata/sirusa/product/52321>
            <https://bps.go.id/metadata/sirusa/product/36102>
            <https://bps.go.id/metadata/sirusa/product/4338>
            <https://bps.go.id/metadata/sirusa/product/34151>
            <https://bps.go.id/metadata/sirusa/product/59779>
            <https://bps.go.id/metadata/sirusa/product/35027>
            <https://bps.go.id/metadata/sirusa/product/35786>
            <https://bps.go.id/metadata/sirusa/product/60697>
            <https://bps.go.id/metadata/sirusa/product/53374>
            <https://bps.go.id/metadata/sirusa/product/16883>
            <https://bps.go.id/metadata/sirusa/product/57166>
            <https://bps.go.id/metadata/sirusa/product/47143>
            <https://bps.go.id/metadata/sirusa/product/13375>
            <https://bps.go.id/metadata/sirusa/product/32960>
            <https://bps.go.id/metadata/sirusa/product/30536>
            <https://bps.go.id/metadata/sirusa/product/29438>
            <https://bps.go.id/metadata/sirusa/product/54479>
            <https://bps.go.id/metadata/sirusa/product/58720>
            <https://bps.go.id/metadata/sirusa/product/20322>
            <https://bps.go.id/metadata/sirusa/product/12898>
            <https://bps.go.id/metadata/sirusa/product/39792>
            <https://bps.go.id/metadata/sirusa/product/13367>
            <https://bps.go.id/metadata/sirusa/product/36073>
            <https://bps.go.id/metadata/sirusa/product/53820>
            <https://bps.go.id/metadata/sirusa/product/38601>
            <https://bps.go.id/metadata/sirusa/product/38050>
            <https://bps.go.id/metadata/sirusa/product/38984>
            <https://bps.go.id/metadata/sirusa/product/33774>
            <https://bps.go.id/metadata/sirusa/product/11239>
            <https://bps.go.id/metadata/sirusa/product/15505>
            <https://bps.go.id/metadata/sirusa/product/63168>
            <https://bps.go.id/metadata/sirusa/product/45957>
            <https://bps.go.id/metadata/sirusa/product/54466>
            <https://bps.go.id/metadata/sirusa/product/36870>
            <https://bps.go.id/metadata/sirusa/product/33269>
            <https://bps.go.id/metadata/sirusa/product/36606>
            <https://bps.go.id/metadata/sirusa/product/66099>
            <https://bps.go.id/metadata/sirusa/product/54589>
            <https://bps.go.id/metadata/sirusa/product/40193>
            <https://bps.go.id/metadata/sirusa/product/33646>
            <https://bps.go.id/metadata/sirusa/product/5507>
            <https://bps.go.id/metadata/sirusa/product/11831>
            <https://bps.go.id/metadata/sirusa/product/32653>
            <https://bps.go.id/metadata/sirusa/product/62699>
            <https://bps.go.id/metadata/sirusa/product/15340>
            <https://bps.go.id/metadata/sirusa/product/41373>
            <https://bps.go.id/metadata/sirusa/product/36012>
            <https://bps.go.id/metadata/sirusa/product/66351>
            <https://bps.go.id/metadata/sirusa/product/37285>
            <https://bps.go.id/metadata/sirusa/product/42343>
            <https://bps.go.id/metadata/sirusa/product/63697>
            <https://bps.go.id/metadata/sirusa/product/38273>
            <https://bps.go.id/metadata/sirusa/product/8442>
            <https://bps.go.id/metadata/sirusa/product/30340>
            <https://bps.go.id/metadata/sirusa/product/44310>
            <https://bps.go.id/metadata/sirusa/product/60401>
            <https://bps.go.id/metadata/sirusa/product/60417>
            <https://bps.go.id/metadata/sirusa/product/10628>
            <https://bps.go.id/metadata/sirusa/product/32816>
          }
        ?concept rdfs:label ?label .
        ?concept rdfs:comment ?definition .
        FILTER(isIRI(?concept)) . 
                } 
        """
        
        self.sparql.setQuery(query)
        self.sparql.setMethod('POST')  # Use POST method for Ontop
        self.sparql.setTimeout(300)
        results = self.sparql.query().convert()
        
        concepts = []
        for result in results["results"]["bindings"]:
            concepts.append({
                "uri": result["concept"]["value"],
                "label": result.get("label", {}).get("value", ""),
                "definition": result.get("definition", {}).get("value", ""),
                "source": result.get("source", {}).get("value", "")
            })
        
        return concepts
    
    def create_entity_description(self, entity: Dict) -> str:
        """Create a textual description for embedding."""
        return f"{entity['label']}. {entity['definition']}. Source: {entity['source']}"
    
    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding with caching."""
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        embedding = self.embeddings.embed_query(text)
        self.embedding_cache[text] = np.array(embedding)
        return self.embedding_cache[text]
    
    
    def llm_determine_relationships_batch(self, source_concept: Dict, target_concepts: List[Dict]) -> List[Tuple[Dict, RelationType, float, str]]:
        """
        Use LLM to determine relationships between one source concept and multiple target concepts in a single call.
        Returns: List of (target_concept, relationship_type, confidence, reasoning) for concepts with relationships.
        """
        desc_source = self.create_entity_description(source_concept)
        
        # Build target concepts description
        target_descriptions = []
        for idx, concept in enumerate(target_concepts):
            desc = self.create_entity_description(concept)
            target_descriptions.append(f"CONCEPT {idx + 1}:\n{desc}")
        
        targets_text = "\n\n".join(target_descriptions)
        
        prompt = f"""You are an expert in statistical metadata and semantic relationships. 
            Analyze the relationship between ONE source concept and MULTIPLE target concepts.

            SOURCE CONCEPT:
            {desc_source}

            TARGET CONCEPTS:
            {targets_text}

            For EACH target indicator, determine whether there is a meaningful conceptual relationship with the source indicator.
            There are four possible relationships:

            1. SAME_AS
                - The source and target indicators are conceptually equivalent
                - They represent the same phenomenon using the same measure
                - Example:
                    Source: “Unemployment Rate (%)”
                    Target: “Percentage of Unemployed Population”

            2. BROADER
                - The target indicator has a broader conceptual scope than the source
                - The source is a specific subset of the target
                - Example:
                    Source: “Manufacturing Employment”
                    Target: “Total Employment”

            3. NARROWER
                - The target indicator has a narrower (more specific) scope than the source
                - The target represents a subset of the source
                - Example:
                    Source: “Population”
                    Target: “Child Population (0–14 years)”
            
            4. NONE
                - The indicators are not conceptually related

            IMPORTANT RULE:
            - Carefully examine the measure used
                - If the source and target indicators use different measures (e.g., count vs percentage, monetary vs ratio), the relationship must be NONE
            - Only include relationships that are: SAME_AS, BROADER, or NARROWER
            - Exclude all NONE relationships from the output
            - Only include relationships with confidence ≥ 0.7
            - Conceptual similarity is more important than naming similarity

            Respond in JSON format with an array of relationships:
            {{
            "relationships": [
                {{
                "concept_index": 1,
                "relationship": "SAME_AS" | "BROADER" | "NARROWER",
                "confidence": 0.7-1.0,
                "reasoning": "Brief conceptual explanation, including measure alignment"
                }}
            ]
            }}

            If no significant relationships exist, return: {{"relationships": []}}
"""
        
        try:
            response = self.llm.invoke(prompt)
            # Extract JSON from response
            response_text = response.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            result = json.loads(response_text.strip())
            
            # Parse results
            relationships = []
            for rel in result.get("relationships", []):
                idx = rel["concept_index"] - 1  # Convert to 0-based index
                if 0 <= idx < len(target_concepts):
                    rel_type = RelationType[rel["relationship"]]
                    confidence = float(rel["confidence"])
                    reasoning = rel["reasoning"]
                    
                    if confidence >= 0.7:
                        relationships.append((
                            target_concepts[idx],
                            rel_type,
                            confidence,
                            reasoning
                        ))
            
            return relationships
            
        except Exception as e:
            print(f"LLM batch relationship determination error: {e}")
            return []

    def find_relationships(self, concepts: List[Dict], 
                          semantic_threshold: float = 0.70,
                          batch_size: int = 10) -> List[Tuple[Dict, Dict, RelationType, float, str]]:
        """
        Find all types of relationships between concepts using hybrid approach with batching.
        Processes concepts in batches to reduce LLM calls.
        Returns: List of (concept1, concept2, relationship_type, confidence, reasoning)
        """
        relationships = []
        
        # Calculate semantic similarity for pre-filtering
        print(f"Calculating semantic similarity for {len(concepts)} concepts...")
        descriptions = [self.create_entity_description(c) for c in concepts]
        embeddings = [self.get_embedding(desc) for desc in descriptions]
        similarity_matrix = cosine_similarity(embeddings)
        
        total_concepts = len(concepts)
        processed = 0
        
        # Process each concept as source
        for i in range(total_concepts):
            source_concept = concepts[i]
            
            # Find candidates with sufficient semantic similarity
            candidates = []
            candidate_indices = []
            
            for j in range(i + 1, total_concepts):
                semantic_sim = similarity_matrix[i][j]
                if semantic_sim >= semantic_threshold:
                    candidates.append(concepts[j])
                    candidate_indices.append((j, semantic_sim))
            
            if not candidates:
                processed += 1
                continue
            
            print(f"\n{'='*80}")
            print(f"Processing concept {i+1}/{total_concepts}: {source_concept['label']}")
            print(f"Found {len(candidates)} candidates with similarity >= {semantic_threshold}")
            
            # Process candidates in batches
            for batch_start in range(0, len(candidates), batch_size):
                batch_end = min(batch_start + batch_size, len(candidates))
                batch_candidates = candidates[batch_start:batch_end]
                batch_indices = candidate_indices[batch_start:batch_end]
                
                print(f"\n  Batch {batch_start//batch_size + 1}: Analyzing {len(batch_candidates)} concepts...")
                
                # Show semantic similarities for this batch
                for idx, (j, sim) in enumerate(batch_indices):
                    print(f"    {idx+1}. {batch_candidates[idx]['label']} (similarity: {sim:.3f})")
                
                # Get relationships for this batch
                batch_relationships = self.llm_determine_relationships_batch(
                    source_concept,
                    batch_candidates
                )
                
                # Process results
                if batch_relationships:
                    print(f"\n  Found {len(batch_relationships)} relationships:")
                    for target_concept, rel_type, confidence, reasoning in batch_relationships:
                        print(f"    ✓ {target_concept['label']}")
                        print(f"      Type: {rel_type.value}")
                        print(f"      Confidence: {confidence:.3f}")
                        print(f"      Reasoning: {reasoning}")
                        
                        relationships.append((
                            source_concept,
                            target_concept,
                            rel_type,
                            confidence,
                            reasoning
                        ))
                else:
                    print(f"    No significant relationships found in this batch")
            
            processed += 1
            print(f"\nProgress: {processed}/{total_concepts} concepts processed")
        
        return relationships
    
    def create_relationship_links(self, relationships: List[Tuple[Dict, Dict, RelationType, float, str]], 
                                 output_graph: Graph) -> Graph:
        """
        Create appropriate RDF links based on relationship type.
        Automatically creates inverse relationships for broader/narrower.
        """
        for concept1, concept2, rel_type, confidence, reasoning in relationships:
            uri1 = URIRef(concept1['uri'])
            uri2 = URIRef(concept2['uri'])
            
            if rel_type == RelationType.SAME_AS:
                # Create bidirectional owl:sameAs links
                output_graph.add((uri1, OWL.sameAs, uri2))
                output_graph.add((uri2, OWL.sameAs, uri1))
                comment = f"Equivalent concept. Confidence: {confidence:.3f}. {reasoning}"
                
            elif rel_type == RelationType.BROADER:
                # Concept1 is broader than Concept2
                # So Concept2 has broader Concept1
                output_graph.add((uri2, SKOS.broader, uri1))
                # And Concept1 has narrower Concept2
                output_graph.add((uri1, SKOS.narrower, uri2))
                comment = f"Hierarchical relationship (broader). Confidence: {confidence:.3f}. {reasoning}"
                
            elif rel_type == RelationType.NARROWER:
                # Concept1 is narrower than Concept2
                # So Concept1 has broader Concept2
                output_graph.add((uri1, SKOS.broader, uri2))
                # And Concept2 has narrower Concept1
                output_graph.add((uri2, SKOS.narrower, uri1))
                comment = f"Hierarchical relationship (narrower). Confidence: {confidence:.3f}. {reasoning}"
                
            elif rel_type == RelationType.RELATED:
                # Create bidirectional skos:related links
                output_graph.add((uri1, SKOS.related, uri2))
                output_graph.add((uri2, SKOS.related, uri1))
                comment = f"Related concept. Confidence: {confidence:.3f}. {reasoning}"
            
            # Add provenance comment
            output_graph.add((uri1, RDFS.comment, RDFLiteral(comment)))
        
        return output_graph
    
    def run_entity_resolution(self, output_file: str = "entity_relationships.ttl"):
        """Run the complete entity resolution and relationship discovery process."""
        print("=" * 80)
        print("Statistical Metadata Relationship Discovery using GraphRAG")
        print("Finding: owl:sameAs, skos:broader, skos:narrower, skos:related")
        print("=" * 80)
        
        # Create output graph
        output_graph = Graph()
        output_graph.bind("owl", OWL)
        output_graph.bind("skos", SKOS)
        output_graph.bind("rdfs", RDFS)
        output_graph.bind("stat", self.STAT)
        
        # Get all concepts
        print("\nRetrieving concepts from SPARQL endpoint...")
        concepts = self.get_all_concepts()
        print(f"Found {len(concepts)} concepts")
        
        # Find relationships
        print("\n" + "=" * 80)
        print("DISCOVERING RELATIONSHIPS")
        print("=" * 80)
        
        relationships = self.find_relationships(
            concepts, 
            semantic_threshold=0.70  # Lower threshold to catch broader/narrower
        )
        
        print(f"\n{'=' * 80}")
        print(f"Found {len(relationships)} relationships")
        print(f"{'=' * 80}")
        
        # Summarize findings
        rel_counts = {}
        for _, _, rel_type, _, _ in relationships:
            rel_counts[rel_type.value] = rel_counts.get(rel_type.value, 0) + 1
        
        print("\nRelationship Summary:")
        for rel_type, count in rel_counts.items():
            print(f"  {rel_type}: {count}")
        
        # Create RDF links
        self.create_relationship_links(relationships, output_graph)
        
        # Save results
        output_graph.serialize(destination=output_file, format='turtle')
        
        print(f"\n{'=' * 80}")
        print(f"Relationship discovery complete!")
        print(f"Results saved to: {output_file}")
        
        # Count triples by relationship type
        sameas_count = len(list(output_graph.triples((None, OWL.sameAs, None))))
        broader_count = len(list(output_graph.triples((None, SKOS.broader, None))))
        narrower_count = len(list(output_graph.triples((None, SKOS.narrower, None))))
        related_count = len(list(output_graph.triples((None, SKOS.related, None))))
        
        print(f"\nTriples created:")
        print(f"  owl:sameAs: {sameas_count}")
        print(f"  skos:broader: {broader_count}")
        print(f"  skos:narrower: {narrower_count}")
        print(f"  skos:related: {related_count}")
        print(f"{'=' * 80}")
        
        return output_graph, relationships
    
    def visualize_hierarchy(self, relationships: List[Tuple[Dict, Dict, RelationType, float, str]]):
        """Print a simple text visualization of the concept hierarchy."""
        print("\n" + "=" * 80)
        print("CONCEPT HIERARCHY VISUALIZATION")
        print("=" * 80)
        
        # Build hierarchy structure
        broader_map = {}  # concept -> list of broader concepts
        narrower_map = {}  # concept -> list of narrower concepts
        sameas_map = {}  # concept -> list of equivalent concepts
        
        for c1, c2, rel_type, conf, _ in relationships:
            if rel_type == RelationType.BROADER:
                # c1 is broader than c2, so c2 has broader c1
                if c2['uri'] not in broader_map:
                    broader_map[c2['uri']] = []
                broader_map[c2['uri']].append(c1['label'])
                
                if c1['uri'] not in narrower_map:
                    narrower_map[c1['uri']] = []
                narrower_map[c1['uri']].append(c2['label'])
                
            elif rel_type == RelationType.NARROWER:
                # c1 is narrower than c2, so c1 has broader c2
                if c1['uri'] not in broader_map:
                    broader_map[c1['uri']] = []
                broader_map[c1['uri']].append(c2['label'])
                
                if c2['uri'] not in narrower_map:
                    narrower_map[c2['uri']] = []
                narrower_map[c2['uri']].append(c1['label'])
                
            elif rel_type == RelationType.SAME_AS:
                if c1['uri'] not in sameas_map:
                    sameas_map[c1['uri']] = []
                sameas_map[c1['uri']].append(c2['label'])
        
        # Print hierarchies
        all_concepts = self.get_all_concepts()
        
        for concept in all_concepts:
            uri = concept['uri']
            label = concept['label']
            
            # Check if this is a top-level concept (no broader concepts)
            if uri not in broader_map:
                print(f"\n📊 {label}")
                
                # Show equivalent concepts
                if uri in sameas_map:
                    for equiv in sameas_map[uri]:
                        print(f"   ≡ {equiv} (equivalent)")
                
                # Show narrower concepts recursively
                if uri in narrower_map:
                    for narrower in narrower_map[uri]:
                        print(f"   ├─ {narrower}")


def main():
    """Main execution function."""
    GOOGLE_API_KEY = "PUT YOUR GOOGLE API KEY HERE"
    SPARQL_ENDPOINT = "http://localhost:3030/#/dataset/sirusa/query"
    
    # Initialize resolver with optional custom log file name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"graphrag_resolution_{timestamp}.log"
    
    resolver = StatisticalMetadataEntityResolver(
        SPARQL_ENDPOINT, 
        GOOGLE_API_KEY,
        log_file=log_filename
    )
    
    try:
        
        # Run entity resolution
        result_graph, relationships = resolver.run_entity_resolution()
        resolver.visualize_hierarchy(relationships)
        
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Log saved to: {log_filename}")
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure logging is properly closed
        if hasattr(resolver, 'logger'):
            sys.stdout = resolver.logger.terminal
            resolver.logger.close()
            print(f"Log file closed: {log_filename}")


if __name__ == "__main__":
    main()