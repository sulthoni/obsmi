# Ontology-Based Statistical Metadata Integration (OBSMI)

##### Table of Contents

[Description](#description)  
[Design](#design)  
[Setup Environment](#setup)
[Evaluation](#evaluation)

## Description

Ontology-Based Statistical Metadata Integration (OBSMI) is a framework that leverages semantic web technologies to harmonize statistical metadata across multiple supporting systems in accordance with international standards. Built upon the Statistical Data Production Ontology (SDPO), OBSMI adopts a hybrid Ontology-Based Data Integration (OBDI) approach that combines a shared vocabulary with local semantic flexibility, making it particularly suitable for addressing the complex needs of National Statistical Offices (NSOs).

## Design

![alt text](/images/OBSMI%20design.png)

The components of the OBSMI framework consist of the following:

- Existing ontologies, documents, data models, and process models serve as inputs and foundations for constructing the Shared Vocabulary.
- Shared Vocabulary (Statistical Data Production Ontology), the core component of the OBSMI framework. It refers to a global ontology encompassing a domain's fundamental concepts. The Statistical Data Production Ontology (SDPO) serves as a foundation for developing local statistical ontologies. As a result, local statistical ontologies can be semantically and structurally aligned by relying on a common foundational ontology.
- Satistical metadata sources refer to the repository of statistical metadata from supporting software or systems of the statistical data production process. These sources may be structured (e.g., relational databases, tabular files), semi-structured (e.g., XML, JSON), or exposed as endpoints (e.g., REST APIs, SPARQL endpoints).
- The result of Data Source Analysis contains the analysis of the schema and structure of the data sources, as well as the identification of column and table mappings from the data sources to the shared vocabulary.
- Local statistical ontologies, which represent the context and semantic meaning of each statistical metadata source. Local statistical ontologies can include more specific and detailed concepts compared to the SDPO, allowing for richer and more granular ontology structures.
- Wrappers or connectors, components designed to facilitate data access from the respective data sources. Each wrapper or connector is unique and tailored to the specific type and technology of the underlying statistical metadata source.
- Triplestores for Statistical Knowledge Graph, which store statistical metadata in RDF format according to each local statistical ontology and statistical metadata source. A triplestore is necessary when entity resolution is required, as the results of the resolution process must be stored for further querying and integration. However, the triplestore can be omitted if no such resolution is needed, allowing direct data access from the source using a format consistent with the local ontology. The triplestores also serve as SPARQL endpoint, an interface that enables querying of statistical metadata already transformed into RDF and stored in a triplestore

The OBSMI framework consists of six main processes as follows:

1. Development of Shared Vocabulary for Statistical Metadata
2. Data Source Analysis and Construction of Local Statistical Ontology
3. Mapping Creation of Statistical Knowledge Graph
4. Statistical Knowledge Graph Population
5. Entity Resolution on Statistical Knowledge Graph Instances
6. Federated Querying over Distributed Statistical KG

## Setup Environment

The evaluation environment was set up using Apache Jena Fuseki. The [docker](https://github.com/sulthoni/obsmi/tree/main/docker) folder includes the datasets and step-by-step instructions for building the Docker container.

## Evaluation

This section presents the functional testing of OBSMI using federated queries to answer a set of competency questions across three SPARQL endpoints. The data sources involved include Statistical Metadata for Dissemination, Questionnaire Designer, and Survey Management. In this example, the queried survey is the National Labor Force Survey (Survei Angkatan Kerja Nasional).

In this testing phase, we utilized three SPARQL endpoints provided by **Apache Jena Fuseki**, as follows:

- `http://localhost:3030/#/dataset/colsys/query`: SPARQL endpoint for the Survey Management dataset
- `http://localhost:3030/#/dataset/designer/query`: SPARQL endpoint for the Questionnaire Designer dataset
- `http://localhost:3030/#/dataset/sirusa/query`: SPARQL endpoint for the Statistical Metadata for Dissemination dataset

The following section presents the competency questions, the SPARQL queries used to answer them, and the results of the SPARQL queries.

The SPARQL queries executed in the http://localhost:3030/#/dataset/colsys/query endpoint.

#### CQ1. What processes are required to conduct a survey?

```SQL
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX gsim-sum: <https://w3id.org/italia/onto/gsim-sum#>
PREFIX gsim: <http://rdf.unece.org/models/gsim#>
PREFIX colsys: <https://bps.go.id/metadata/collection-system/>
PREFIX : <https://w3id.org/sdp/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT DISTINCT ?StatisticalProgramName ?StatisticalProgramCycleName ?BusinessProcess ?ProcessStepName ?GSBPM_code WHERE {
  {
    # From dataset Statistical metadata for dissemination
    SERVICE <http://127.0.0.1:3030/sirusa/sparql> {
      ?StatisticalProgram a :StatisticalProgram ; gsim-sum:hasName-IA ?StatisticalProgramName .
      ?StatisticalProgram :hasSP-SPC ?StatisticalProgramCycle .
      ?StatisticalProgramCycle gsim-sum:hasName-IA ?StatisticalProgramCycleName .
      ?StatisticalProgramCycle :includesSPC-BP ?BusinessProcess .
      ?BusinessProcess :hasBP-PS ?ProcessStep .
      ?ProcessStep rdfs:label ?ProcessStepName .
      ?ProcessStep :classifiedAs-PS ?GSBPM_code .
      FILTER(?StatisticalProgram IN (<https://bps.go.id/metadata/sirusa/statistical-program/Survei%20Angkatan%20Kerja%20Nasional%20%28SAKERNAS%29>))
    }
  }
  UNION
  {
    #From dataset Survey management
      ?StatisticalProgram_CollectionSystem a :StatisticalProgram ; gsim-sum:hasName-IA ?StatisticalProgramName .
      ?StatisticalProgram :hasSP-SPC ?StatisticalProgramCycle .
      ?StatisticalProgramCycle gsim-sum:hasName-IA ?StatisticalProgramCycleName .
      ?StatisticalProgramCycle :includesSPC-BP ?BusinessProcess .
      ?BusinessProcess :hasBP-PS ?ProcessStep .
      ?ProcessStep rdfs:label ?ProcessStepName .
      ?ProcessStep :classifiedAs-PS ?GSBPM_code .

      #Filter by owl:sameAs
      ?StatisticalProgram owl:sameAs ?StatisticalProgram_CollectionSystem .
  }

}
LIMIT 100

```

Result
|StatisticalProgramName |StatisticalProgramCycleName |BusinessProcess |ProcessStepName |GSBPM_code |
|-----------------------------------------|------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|------------------------------------|
|Survei Angkatan Kerja Nasional (SAKERNAS)|Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|https://bps.go.id/metadata/sirusa/business-process/Survei%20Angkatan%20Kerja%20Nasional%20%28SAKERNAS%29/2024 |Process Step - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|http://id.unece.org/models/gsbpm/2.2|
|Survei Angkatan Kerja Nasional (SAKERNAS)|Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|https://bps.go.id/metadata/sirusa/business-process/Survei%20Angkatan%20Kerja%20Nasional%20%28SAKERNAS%29/2024 |Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|
|SAKERNAS 2024 FEB - PENDATAAN |Februari 2024 |https://bps.go.id/metadata/collection-system/business-process/903c27f9-3f93-41e0-9333-f261f43582db/07d004dc-9c61-448d-a1b7-b275b60fac5d|Process Step - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |http://id.unece.org/models/gsbpm/3.1|

#### CQ2. What metadata is required to create a survey?

```SQL
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX gsim-sum: <https://w3id.org/italia/onto/gsim-sum#>
PREFIX gsim: <http://rdf.unece.org/models/gsim#>
PREFIX colsys: <https://bps.go.id/metadata/collection-system/>
PREFIX : <https://w3id.org/sdp/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT DISTINCT ?StatisticalProgramName ?ProcessStepName ?GSBPM_code ?ProcessInputName ?MetadataInputValue WHERE {
  {
    # From Dataset Sistem Rujukan Statistik
    SERVICE <http://127.0.0.1:3030/sirusa/sparql> {
      ?StatisticalProgram a :StatisticalProgram ; gsim-sum:hasName-IA ?StatisticalProgramName .
      ?StatisticalProgram :hasSP-SPC / :includesSPC-BP / :hasBP-PS ?ProcessStep .
      ?ProcessStep rdfs:label ?ProcessStepName .
      ?ProcessStep :classifiedAs-PS ?GSBPM_code .
      ?ProcessStep :hasPS-PI ?ProcessInput .
      ?ProcessInput rdfs:label ?ProcessInputName .
      ?ProcessInput :refersToCI-IA ?MetadataInput.
      ?MetadataInput rdfs:label ?MetadataInputValue .
      #Limit only 1 survey
      FILTER(?StatisticalProgram IN (<https://bps.go.id/metadata/sirusa/statistical-program/Survei%20Angkatan%20Kerja%20Nasional%20%28SAKERNAS%29>))
    }
  }
  UNION
  {
      #From dataset Survey management
      ?StatisticalProgram_CollectionSystem a :StatisticalProgram ; gsim-sum:hasName-IA ?StatisticalProgramName .
      ?StatisticalProgram :hasSP-SPC / :includesSPC-BP / :hasBP-PS ?ProcessStep .
      ?ProcessStep rdfs:label ?ProcessStepName .
      ?ProcessStep :classifiedAs-PS ?GSBPM_code .
      ?ProcessStep :hasPS-PI ?ProcessInput .
      ?ProcessInput rdfs:label ?ProcessInputName .
      ?ProcessInput :refersToCI-IA ?MetadataInput.
      ?MetadataInput rdfs:label ?MetadataInputValue .

      #Filter by owl:sameAs
      ?StatisticalProgram owl:sameAs ?StatisticalProgram_CollectionSystem .
  }

}
LIMIT 100
```

Result
|StatisticalProgramName |ProcessStepName |GSBPM_code |ProcessInputName |MetadataInputValue |
|-----------------------------------------|---------------------------------------------------------------------------------------------------|------------------------------------|-------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|http://id.unece.org/models/gsbpm/2.2|Core Input - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|Concept - "Lapangan pekerjaan" |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|http://id.unece.org/models/gsbpm/2.2|Core Input - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|Concept - "Mencari pekerjaan" |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|http://id.unece.org/models/gsbpm/2.2|Core Input - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|Concept - "Sementara Tidak Bekerja" |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|http://id.unece.org/models/gsbpm/2.2|Core Input - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|Concept - "Umur" |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|http://id.unece.org/models/gsbpm/2.2|Core Input - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|Concept - "Pendidikan" |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Input - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Conceptual - "ILO" |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Input - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Conceptual - "Nilai tambah pertanian per tenaga kerja\r\n" |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Input - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Conceptual - "Pekerja informal" |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Input - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Conceptual - "Pekerja Anak" |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Input - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Conceptual - "Pengangguran terbuka" |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Input - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Conceptual - "Penduduk usia muda yang tidak sekolah, bekerja, atau mengikuti pelatihan" |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Input - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Conceptual - "Persentase setengah pengangguran" |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Input - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Conceptual - "Upah\/gaji bersih adalah imbalan yang diterima selama sebulan oleh buruh\/karyawan baik berupa uang atau barang yang dibayarkan perusahaan\/kantor\/majikan. Imbalan dalam bentuk barang dinilai dengan harga setempat. Upah\/gaji bersih yang dimaksud tersebut adalah setelah dikurangi dengan potongan-potongan iuran wajib, pajak penghasilan, dan sebagainya."|
|SAKERNAS 2024 FEB - PENDATAAN |Process Step - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |http://id.unece.org/models/gsbpm/3.1|Core Input - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |Role - PCL |
|SAKERNAS 2024 FEB - PENDATAAN |Process Step - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |http://id.unece.org/models/gsbpm/3.1|Core Input - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |Role - Admin Kabupaten |
|SAKERNAS 2024 FEB - PENDATAAN |Process Step - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |http://id.unece.org/models/gsbpm/3.1|Core Input - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |Role - PML |
|SAKERNAS 2024 FEB - PENDATAAN |Process Step - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |http://id.unece.org/models/gsbpm/3.1|Core Input - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |Individual - Pencacah |
|SAKERNAS 2024 FEB - PENDATAAN |Process Step - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |http://id.unece.org/models/gsbpm/3.1|Core Input - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |Individual - 3300ics@gmail.com |
|SAKERNAS 2024 FEB - PENDATAAN |Process Step - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |http://id.unece.org/models/gsbpm/3.1|Core Input - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |Individual - Kortim |
|SAKERNAS 2024 FEB - PENDATAAN |Process Step - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |http://id.unece.org/models/gsbpm/3.1|Core Input - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |Individual - Admin Kabupaten |
|SAKERNAS 2024 FEB - PENDATAAN |Process Step - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |http://id.unece.org/models/gsbpm/3.1|Core Input - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |Individual - mira |
|SAKERNAS 2024 FEB - PENDATAAN |Process Step - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |http://id.unece.org/models/gsbpm/3.1|Core Input - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |Individual - 3300fasih@gmail.com |
|SAKERNAS 2024 FEB - PENDATAAN |Process Step - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |http://id.unece.org/models/gsbpm/3.1|Core Input - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |Individual - infazrizki |

#### CQ3. What metadata is produced by each process in the statistical data production?

```SQL
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX gsim-sum: <https://w3id.org/italia/onto/gsim-sum#>
PREFIX gsim: <http://rdf.unece.org/models/gsim#>
PREFIX colsys: <https://bps.go.id/metadata/collection-system/>
PREFIX : <https://w3id.org/sdp/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT DISTINCT ?StatisticalProgramName ?ProcessStepName ?GSBPM_code ?ProcessOutputName ?MetadataOutputValue WHERE {
  {
    # From Dataset Sistem Rujukan Statistik
    SERVICE <http://127.0.0.1:3030/sirusa/sparql> {
      ?StatisticalProgram a :StatisticalProgram ; gsim-sum:hasName-IA ?StatisticalProgramName .
      ?StatisticalProgram :hasSP-SPC / :includesSPC-BP / :hasBP-PS ?ProcessStep .
      ?ProcessStep rdfs:label ?ProcessStepName .
      ?ProcessStep :classifiedAs-PS ?GSBPM_code .
      ?ProcessStep :createsPS-PO ?ProcessOutput .
      ?ProcessOutput rdfs:label ?ProcessOutputName .
      ?ProcessOutput :refersToCO-IA ?MetadataOutput.
      ?MetadataOutput rdfs:label ?MetadataOutputValue .
      #Limit only 1 survey
      FILTER(?StatisticalProgram IN (<https://bps.go.id/metadata/sirusa/statistical-program/Survei%20Angkatan%20Kerja%20Nasional%20%28SAKERNAS%29>))
    }
  }
  UNION
  {
      #From dataset Survey management
      ?StatisticalProgram_CollectionSystem a :StatisticalProgram ; gsim-sum:hasName-IA ?StatisticalProgramName .
      ?StatisticalProgram :hasSP-SPC / :includesSPC-BP / :hasBP-PS ?ProcessStep .
      ?ProcessStep rdfs:label ?ProcessStepName .
      ?ProcessStep :classifiedAs-PS ?GSBPM_code .
      ?ProcessStep :createsPS-PO ?ProcessOutput .
      ?ProcessOutput rdfs:label ?ProcessOutputName .
      ?ProcessOutput :refersToCO-IA ?MetadataOutput.
      ?MetadataOutput rdfs:label ?MetadataOutputValue .

      #Filter by owl:sameAs
      ?StatisticalProgram owl:sameAs ?StatisticalProgram_CollectionSystem .
  }

}
LIMIT 100
```

Result
|StatisticalProgramName |ProcessStepName |GSBPM_code |ProcessOutputName |MetadataOutputValue |
|-----------------------------------------|---------------------------------------------------------------------------------------------------|------------------------------------|-------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|http://id.unece.org/models/gsbpm/2.2|Core Output - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|Conceptual Variable - Pendidikan |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|http://id.unece.org/models/gsbpm/2.2|Core Output - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|Conceptual Variable - Jenis pekerjaan |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|http://id.unece.org/models/gsbpm/2.2|Core Output - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|Conceptual Variable - Umur |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|http://id.unece.org/models/gsbpm/2.2|Core Output - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|Conceptual Variable - Mencari pekerjaan |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|http://id.unece.org/models/gsbpm/2.2|Core Output - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|Conceptual Variable - Lapangan pekerjaan |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|http://id.unece.org/models/gsbpm/2.2|Core Output - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|Conceptual Variable - Sementara Tidak Bekerja |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Output - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Product - Angka Partisipasi Kasar (APK) |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Output - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Product - Tingkat Kesempatan Kerja |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Output - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Product - Angka Partisipasi Murni (APM) |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Output - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Product - Tingkat Partisipasi Angkatan Kerja (TPAK) |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Output - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Product - Tingkat Pengangguran Terbuka (TPT) |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Output - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Product - Angka Partisipasi Sekolah (APS) |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Output - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Product - Persentase Usia Muda (15-24 Tahun) Yang Sedang Tidak Sekolah, Bekerja Atau Mengikuti Pelatihan |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Output - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Product - Proporsi Tenaga Kerja pada Sektor Industri Manufaktur |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Output - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Product - Angkatan Kerja |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Output - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Product - Tingkat Kesempatan Kerja (TKK) |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Output - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Product - Nilai tambah pertanian per tenaga kerja menurut kelas usaha tani tanaman/ peternakan/ perikanan/ kehutanan |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Output - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Product - Indeks Pembangunan Gender (IPG) |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Output - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Product - Setengah penganggur |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Output - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Product - Persentase Anak Usia 10-17 Tahun yang Bekerja |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Output - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Product - Persentase Setengah Pengangguran |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Output - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Product - Proporsi Lapangan Kerja Informal |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Core Output - Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |Product - Upah rata-rata per jam pekerja |
|SAKERNAS 2024 FEB - PENDATAAN |Process Step - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |http://id.unece.org/models/gsbpm/3.1|Core Output - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |SAKERNAS FEB 2024 - PENDATAAN_uc_final |
|SAKERNAS 2024 FEB - PENDATAAN |Process Step - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |http://id.unece.org/models/gsbpm/3.1|Core Output - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |Agent in Role - PCL |
|SAKERNAS 2024 FEB - PENDATAAN |Process Step - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |http://id.unece.org/models/gsbpm/3.1|Core Output - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |Agent in Role - Admin Kabupaten |
|SAKERNAS 2024 FEB - PENDATAAN |Process Step - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |http://id.unece.org/models/gsbpm/3.1|Core Output - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |Agent in Role - PML |

#### CQ4. Do the production processes occur sequentially in accordance with the order specified by GSBPM?

```SQL
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX gsim-sum: <https://w3id.org/italia/onto/gsim-sum#>
PREFIX gsim: <http://rdf.unece.org/models/gsim#>
PREFIX colsys: <https://bps.go.id/metadata/collection-system/>
PREFIX : <https://w3id.org/sdp/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT DISTINCT ?StatisticalProgramName ?ProcessStepName ?GSBPM_code ?ProcessStepStart WHERE {
  {
    # From Dataset Sistem Rujukan Statistik
    SERVICE <http://127.0.0.1:3030/sirusa/sparql> {
      ?StatisticalProgram a :StatisticalProgram ; gsim-sum:hasName-IA ?StatisticalProgramName .
      ?StatisticalProgram :hasSP-SPC / :includesSPC-BP / :hasBP-PS ?ProcessStep .
      ?ProcessStep rdfs:label ?ProcessStepName .
      ?ProcessStep :classifiedAs-PS ?GSBPM_code .
      ?ProcessStep :hasStartTime-PS ?ProcessStepStart .
      #Limit only 1 survey
      FILTER(?StatisticalProgram IN (<https://bps.go.id/metadata/sirusa/statistical-program/Survei%20Angkatan%20Kerja%20Nasional%20%28SAKERNAS%29>))
    }
  }
  UNION
  {
      #From dataset Survey management
      ?StatisticalProgram_CollectionSystem a :StatisticalProgram ; gsim-sum:hasName-IA ?StatisticalProgramName .
      ?StatisticalProgram :hasSP-SPC / :includesSPC-BP / :hasBP-PS ?ProcessStep .
      ?ProcessStep rdfs:label ?ProcessStepName .
      ?ProcessStep :classifiedAs-PS ?GSBPM_code .
      ?ProcessStep :hasStartTime-PS ?ProcessStepStart .

      #Filter by owl:sameAs
      ?StatisticalProgram owl:sameAs ?StatisticalProgram_CollectionSystem .
  }

}
LIMIT 100
```

Result:
|StatisticalProgramName |ProcessStepName |GSBPM_code |ProcessStepStart |
|-----------------------------------------|---------------------------------------------------------------------------------------------------|------------------------------------|-------------------------------------------------------------------------------------------------|
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|http://id.unece.org/models/gsbpm/2.2|2023-10-31 09:38:30 |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|2023-10-31 09:38:30 |
|SAKERNAS 2024 FEB - PENDATAAN |Process Step - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |http://id.unece.org/models/gsbpm/3.1|2024-01-27T06:04:15.4486850 |

#### CQ5. What metadata falls under the categories of planning, implementation, dissemination, and evaluation?

```SQL
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX gsim-sum: <https://w3id.org/italia/onto/gsim-sum#>
PREFIX gsim: <http://rdf.unece.org/models/gsim#>
PREFIX colsys: <https://bps.go.id/metadata/collection-system/>
PREFIX : <https://w3id.org/sdp/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT DISTINCT ?StatisticalProgramName ?ProcessStepName ?GSBPM_code ?GBPSM_Phase WHERE {
  {
    # From Dataset Sistem Rujukan Statistik
    SERVICE <http://127.0.0.1:3030/sirusa/sparql> {
      ?StatisticalProgram a :StatisticalProgram ; gsim-sum:hasName-IA ?StatisticalProgramName .
      ?StatisticalProgram :hasSP-SPC / :includesSPC-BP / :hasBP-PS ?ProcessStep .
      ?ProcessStep rdfs:label ?ProcessStepName .
      ?ProcessStep :classifiedAs-PS ?GSBPM_code .
      ?GSBPM_code skos:broader / skos:prefLabel ?GBPSM_Phase .
      #Limit only 1 survey
      FILTER(?StatisticalProgram IN (<https://bps.go.id/metadata/sirusa/statistical-program/Survei%20Angkatan%20Kerja%20Nasional%20%28SAKERNAS%29>))
    }
  }
  UNION
  {
      #From dataset Survey management
      ?StatisticalProgram_CollectionSystem a :StatisticalProgram ; gsim-sum:hasName-IA ?StatisticalProgramName .
      ?StatisticalProgram :hasSP-SPC / :includesSPC-BP / :hasBP-PS ?ProcessStep .
      ?ProcessStep rdfs:label ?ProcessStepName .
      ?ProcessStep :classifiedAs-PS ?GSBPM_code .
      ?GSBPM_code skos:broader / skos:prefLabel ?GBPSM_Phase .

      #Filter by owl:sameAs
      ?StatisticalProgram owl:sameAs ?StatisticalProgram_CollectionSystem .
  }

}
LIMIT 100
```

Result
|StatisticalProgramName |ProcessStepName |GSBPM_code |GBPSM_Phase |
|-----------------------------------------|---------------------------------------------------------------------------------------------------|------------------------------------|-------------------------------------------------------------------------------------------------|
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|http://id.unece.org/models/gsbpm/2.2|Design |
|Survei Angkatan Kerja Nasional (SAKERNAS)|Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Design |
|SAKERNAS 2024 FEB - PENDATAAN |Process Step - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |http://id.unece.org/models/gsbpm/3.1|Build |

#### CQ6. Can the processes in statistical data production be audited?

_Activity logs are only available for the Build Collection Instruments process. Therefore, in this evaluation, logs are presented solely for that process._

```SQL
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX gsim-sum: <https://w3id.org/italia/onto/gsim-sum#>
PREFIX gsim: <http://rdf.unece.org/models/gsim#>
PREFIX colsys: <https://bps.go.id/metadata/collection-system/>
PREFIX : <https://w3id.org/sdp/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT DISTINCT ?StatisticalProgramName ?StatisticalProgramCycleName ?BusinessProcess ?ProcessStepName ?MetadataOutput ?LogData WHERE {
  {
    # From dataset Statistical metadata for dissemination
    SERVICE <http://127.0.0.1:3030/sirusa/sparql> {
      ?StatisticalProgram a :StatisticalProgram ; gsim-sum:hasName-IA ?StatisticalProgramName .
      ?StatisticalProgram :hasSP-SPC ?StatisticalProgramCycle .
      ?StatisticalProgramCycle gsim-sum:hasName-IA ?StatisticalProgramCycleName .
      ?StatisticalProgramCycle :includesSPC-BP ?BusinessProcess .
      ?BusinessProcess :hasBP-PS ?ProcessStep .
      ?ProcessStep rdfs:label ?ProcessStepName .
      ?ProcessStep :createsPS-PO ?ProcessExecutionLog .
      ?ProcessExecutionLog :refersToCO-IA ?MetadataOutput.
      ?MetadataOutput a :ProcessExecutionLog .
      ?MetadataOutput gsim-sum:hasExecutionLog ?LogData .
      FILTER(?StatisticalProgram IN (<https://bps.go.id/metadata/sirusa/statistical-program/Survei%20Angkatan%20Kerja%20Nasional%20%28SAKERNAS%29>)) .
      BIND("Sistem Rujukan Statistik" as ?ApplicationPackage) .
    }
  }
  UNION
  {
    #From dataset Survey management
      ?StatisticalProgram_CollectionSystem a :StatisticalProgram ; gsim-sum:hasName-IA ?StatisticalProgramName .
      ?StatisticalProgram :hasSP-SPC ?StatisticalProgramCycle .
      ?StatisticalProgramCycle gsim-sum:hasName-IA ?StatisticalProgramCycleName .
      ?StatisticalProgramCycle :includesSPC-BP ?BusinessProcess .
      ?BusinessProcess :hasBP-PS ?ProcessStep .
      ?ProcessStep rdfs:label ?ProcessStepName .
      ?ProcessStep :createsPS-PO ?ProcessExecutionLog .
      ?ProcessExecutionLog :refersToCO-IA ?MetadataOutput.
      ?MetadataOutput a :ProcessExecutionLog .
      ?MetadataOutput gsim-sum:hasExecutionLog ?LogData .

      #Filter by owl:sameAs
      ?StatisticalProgram owl:sameAs ?StatisticalProgram_CollectionSystem .
  }

}
LIMIT 100
```

Result
|StatisticalProgramName |StatisticalProgramCycleName|BusinessProcess |ProcessStepName |MetadataOutput |LogData |
|-----------------------------|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|SAKERNAS 2024 FEB - PENDATAAN|Februari 2024 |https://bps.go.id/metadata/collection-system/business-process/903c27f9-3f93-41e0-9333-f261f43582db/07d004dc-9c61-448d-a1b7-b275b60fac5d|Process Step - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024|https://bps.go.id/metadata/collection-system/process-execution-log/903c27f9-3f93-41e0-9333-f261f43582db/07d004dc-9c61-448d-a1b7-b275b60fac5d|{"s_id":"903c27f9-3f93-41e0-9333-f261f43582db","sp_id":"07d004dc-9c61-448d-a1b7-b275b60fac5d","s_panel_type":false,"s_area_type":false,"s_update_listing_type":false,"s_can_add_sample":false,"s_is_multi_pencacah":false,"s_geo_live_tracking":false,"s_geo_radius":0,"s_geo_accuracy":50,"s_created_at":"2024-01-27T06:04:15.4486850","s_updated_at":"2024-02-06T10:29:38.0291640","note":"- Kuesioner CAPI sudah dibuat dan diujicoba - Role petugas sudah dibuat - Rule validasi perlu dipertajam"}|

#### CQ7. Is the design or planned process always consistent with the actual process execution?

_To answer this question, it is necessary to compare the concepts and definitions from the planning phase with their implementation in the questionnaire. In this example, the comparison involves the planning phase results obtained from CQ2 and CQ3, which are then compared with the implementation results obtained through the following SPARQL query._

```SQL
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX gsim-sum: <https://w3id.org/italia/onto/gsim-sum#>
PREFIX gsim: <http://rdf.unece.org/models/gsim#>
PREFIX colsys: <https://bps.go.id/metadata/collection-system/>
PREFIX : <https://w3id.org/sdp/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?StatisticalProgramName ?QuestionnaireName ?QuestionnaireBlockLabel ?QuestionLabel
WHERE {
  	#From dataset Survey management
	SERVICE <http://127.0.0.1:3030/colsys/sparql> {
      ?StatisticalProgram_CollectionSystem a :StatisticalProgram ; gsim-sum:hasName-IA ?StatisticalProgramName .
      ?StatisticalProgram_CollectionSystem :hasSP-SPC / :includesSPC-BP / :hasBP-PS ?ProcessStep .
      ?ProcessStep rdfs:label ?ProcessStepName .
      ?ProcessStep :classifiedAs-PS ?GSBPM_code .
      ?ProcessStep :createsPS-PO ?ProcessOutput .
      ?ProcessOutput rdfs:label ?ProcessOutputName .
      ?ProcessOutput :refersToCO-IA ?MetadataOutput.
      ?MetadataOutput a gsim:Questionnaire .
      ?MetadataOutput rdfs:label ?MetadataOutputValue .

      FILTER(?StatisticalProgram_CollectionSystem = <https://bps.go.id/metadata/collection-system/statistical-program/903c27f9-3f93-41e0-9333-f261f43582db>) .
  	}

    ?MetadataOutput rdfs:label ?QuestionnaireName .
    ?MetadataOutput :includesQ-IQB ?QuestionnaireBlock .
    ?QuestionnaireBlock rdfs:label ?QuestionnaireBlockLabel .
    ?QuestionnaireBlock :includesIQB-IQ ?Question .
    ?Question rdfs:label ?QuestionLabel .
}
LIMIT 100
```

Result (Part of Results)
|StatisticalProgramName |QuestionnaireName |QuestionnaireBlockLabel |QuestionLabel |
|-----------------------------------------|---------------------------------------------------------------------------------------------------|------------------------------------|-------------------------------------------------------------------------------------------------|
|SAKERNAS 2024 FEB - PENDATAAN |Questionnaire SAKERNAS FEB 2024 - PENDATAAN_uc_final |Instance Question Block - IV. DAFTAR ANGGOTA RUMAH TANGGA|Instance question - <span class="font-normal">k10. Umur <b>$NAME$</b> (tahun)</span> |
|SAKERNAS 2024 FEB - PENDATAAN |Questionnaire SAKERNAS FEB 2024 - PENDATAAN_uc_final |Instance Question Block - V.1. PERKAWINAN, PENDIDIKAN, PELATIHAN (5TH+)|Instance question - 6.g. Jumlah pelatihan/kursus/training yang diikuti : |
|SAKERNAS 2024 FEB - PENDATAAN |Questionnaire SAKERNAS FEB 2024 - PENDATAAN_uc_final |Instance Question Block - V.1. PERKAWINAN, PENDIDIKAN, PELATIHAN (5TH+)|Instance question - <b>6.b.</b> Jurusan pendidikan/ bidang studi pada pendidikan tertinggi yang ditamatkan:|
|SAKERNAS 2024 FEB - PENDATAAN |Questionnaire SAKERNAS FEB 2024 - PENDATAAN_uc_final |Instance Question Block - V.1. PERKAWINAN, PENDIDIKAN, PELATIHAN (5TH+)|Instance question - <b>6.b.</b> Kode jurusan pendidikan: |
|SAKERNAS 2024 FEB - PENDATAAN |Questionnaire SAKERNAS FEB 2024 - PENDATAAN_uc_final |Instance Question Block - V.1. PERKAWINAN, PENDIDIKAN, PELATIHAN (5TH+)|Instance question - <b>6.c.</b> Bulan <b>$NAME$</b> lulus sekolah/kuliah pada pendidikan tertinggi yang ditamatkan?|
|SAKERNAS 2024 FEB - PENDATAAN |Questionnaire SAKERNAS FEB 2024 - PENDATAAN_uc_final |Instance Question Block - V.1. PERKAWINAN, PENDIDIKAN, PELATIHAN (5TH+)|Instance question - <span class="font-normal">6.b. Penyelenggara pendidikan pada pendidikan tertinggi yang ditamatkan:</span>|
|SAKERNAS 2024 FEB - PENDATAAN |Questionnaire SAKERNAS FEB 2024 - PENDATAAN_uc_final |Instance Question Block - V.1. PERKAWINAN, PENDIDIKAN, PELATIHAN (5TH+)|Instance question - <span class="font-normal">6.c. Tahun <b>$NAME$</b> lulus sekolah/kuliah pada pendidikan tertinggi yang ditamatkan?</span>|
|SAKERNAS 2024 FEB - PENDATAAN |Questionnaire SAKERNAS FEB 2024 - PENDATAAN_uc_final |Instance Question Block - V.1. PERKAWINAN, PENDIDIKAN, PELATIHAN (5TH+)|Instance question - <span class="font-normal">6.d. Apakah <b>$NAME$</b> pernah mengikuti pelatihan/kursus/training?</span>|
|SAKERNAS 2024 FEB - PENDATAAN |Questionnaire SAKERNAS FEB 2024 - PENDATAAN_uc_final |Instance Question Block - V.1. PERKAWINAN, PENDIDIKAN, PELATIHAN (5TH+)|Instance question - <span class="font-normal">6.e. Apakah dari pelatihan/kursus/training tersebut <b>$NAME$</b> memperoleh sertifikat?</span>|
|SAKERNAS 2024 FEB - PENDATAAN |Questionnaire SAKERNAS FEB 2024 - PENDATAAN_uc_final |Instance Question Block - V.1. PERKAWINAN, PENDIDIKAN, PELATIHAN (5TH+)|Instance question - <span class="font-normal">6.f. Apakah pelatihan/kursus/training tersebut dilaksanakan dalam setahun terakhir?</span>|
|SAKERNAS 2024 FEB - PENDATAAN |Questionnaire SAKERNAS FEB 2024 - PENDATAAN_uc_final |Instance Question Block - V.2. MAGANG, DISABILITAS, DAN KONSEP BEKERJA (5TH+)|Instance question - <div class="text-center border-2 p-4 rounded-lg" style="backgrond-color: #FF0000"><b>6.i. Dalam tiga tahun terakhir, apakah $NAME$ pernah mengikuti Program Magang/Praktik Kerja Lapangan (PKL)?</b></div>|
|SAKERNAS 2024 FEB - PENDATAAN |Questionnaire SAKERNAS FEB 2024 - PENDATAAN_uc_final |Instance Question Block - V.2. MAGANG, DISABILITAS, DAN KONSEP BEKERJA (5TH+)|Instance question - <div class="text-center border-2 p-4 rounded-lg" style="backgrond-color: #FF0000"><b>6.j. Dalam tiga tahun terakhir, apakah $NAME$ pernah mengikuti Program Pertukaran Pelajar/Mahasiswa?</b></div>|
|SAKERNAS 2024 FEB - PENDATAAN |Questionnaire SAKERNAS FEB 2024 - PENDATAAN_uc_final |Instance Question Block - V.2. MAGANG, DISABILITAS, DAN KONSEP BEKERJA (5TH+)|Instance question - <div class="text-center border-2 p-4 rounded-lg" style="backgrond-color: #FF0000"><b>6.k. Dalam tiga tahun terakhir, apakah $NAME$ pernah mengikuti Program Pengabdian Masyarakat?</b></div>|
|SAKERNAS 2024 FEB - PENDATAAN |Questionnaire SAKERNAS FEB 2024 - PENDATAAN_uc_final |Instance Question Block - V.2. MAGANG, DISABILITAS, DAN KONSEP BEKERJA (5TH+)|Instance question - <div class="text-center border-2 p-4 rounded-lg" style="backgrond-color: #FF0000"><b>JIKA NO. 6.a= 4,5,6,7,8,9,10,11 DAN 12, LANJUTKAN KE No. 6.i <br>JIKA NO. 6.a= 1,2, DAN 3, LANJUTKAN KE No. 7</b></div>|
|SAKERNAS 2024 FEB - PENDATAAN |Questionnaire SAKERNAS FEB 2024 - PENDATAAN_uc_final |Instance Question Block - V.2. MAGANG, DISABILITAS, DAN KONSEP BEKERJA (5TH+)|Instance question - <span class="font-normal">10. Apakah <b>$NAME$</b> sebenarnya memiliki pekerjaan/kegiatan usaha, tetapi seminggu terakhir sedang tidak bekerja/tidak menjalankan usaha tersebut?</span>|
|SAKERNAS 2024 FEB - PENDATAAN |Questionnaire SAKERNAS FEB 2024 - PENDATAAN_uc_final |Instance Question Block - V.2. MAGANG, DISABILITAS, DAN KONSEP BEKERJA (5TH+)|Instance question - <span class="font-normal">11.a. Apakah alasan utama <b>$NAME$</b> sementara tidak bekerja selama seminggu terakhir?</span>|
|SAKERNAS 2024 FEB - PENDATAAN |Questionnaire SAKERNAS FEB 2024 - PENDATAAN_uc_final |Instance Question Block - V.2. MAGANG, DISABILITAS, DAN KONSEP BEKERJA (5TH+)|Instance question - <span class="font-normal">11.a. Jika 11a terisi kode 8, tuliskan alasan lainnya: </span>|
|SAKERNAS 2024 FEB - PENDATAAN |Questionnaire SAKERNAS FEB 2024 - PENDATAAN_uc_final |Instance Question Block - V.2. MAGANG, DISABILITAS, DAN KONSEP BEKERJA (5TH+)|Instance question - <span class="font-normal">11.b. Apakah <b>$NAME$</b> tetap memperoleh penghasilan/gaji/upah selama periode sementara tidak bekerja? </span>|
|SAKERNAS 2024 FEB - PENDATAAN |Questionnaire SAKERNAS FEB 2024 - PENDATAAN_uc_final |Instance Question Block - V.2. MAGANG, DISABILITAS, DAN KONSEP BEKERJA (5TH+)|Instance question - <span class="font-normal">11.c. Sudah berapa lama <b>$NAME$</b> sementara tidak bekerja? </span>|
|SAKERNAS 2024 FEB - PENDATAAN |Questionnaire SAKERNAS FEB 2024 - PENDATAAN_uc_final |Instance Question Block - V.2. MAGANG, DISABILITAS, DAN KONSEP BEKERJA (5TH+)|Instance question - <span class="font-normal">11.d. Apakah ada jaminan <b>$NAME$</b> kembali bekerja pada unit usaha/tempat kerja sekarang? </span>|
|SAKERNAS 2024 FEB - PENDATAAN |Questionnaire SAKERNAS FEB 2024 - PENDATAAN_uc_final |Instance Question Block - V.2. MAGANG, DISABILITAS, DAN KONSEP BEKERJA (5TH+)|Instance question - <span class="font-normal">6.i. Memperoleh sertifikat:</span> |

#### CQ8. What applications can be used to assist processes in statistical data production?

_The name of the application associated with each process is inferred based on the application linked to the corresponding dataset. Since this information is not explicitly available within the dataset, it was manually added to the SPARQL query based on the known source of the data._

```SQL
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX gsim-sum: <https://w3id.org/italia/onto/gsim-sum#>
PREFIX gsim: <http://rdf.unece.org/models/gsim#>
PREFIX colsys: <https://bps.go.id/metadata/collection-system/>
PREFIX : <https://w3id.org/sdp/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT DISTINCT ?StatisticalProgramName ?StatisticalProgramCycleName ?BusinessProcess ?ProcessStepName ?GSBPM_code ?ApplicationPackage WHERE {
  {
    # From dataset Statistical metadata for dissemination
    SERVICE <http://127.0.0.1:3030/sirusa/sparql> {
      ?StatisticalProgram a :StatisticalProgram ; gsim-sum:hasName-IA ?StatisticalProgramName .
      ?StatisticalProgram :hasSP-SPC ?StatisticalProgramCycle .
      ?StatisticalProgramCycle gsim-sum:hasName-IA ?StatisticalProgramCycleName .
      ?StatisticalProgramCycle :includesSPC-BP ?BusinessProcess .
      ?BusinessProcess :hasBP-PS ?ProcessStep .
      ?ProcessStep rdfs:label ?ProcessStepName .
      ?ProcessStep :classifiedAs-PS ?GSBPM_code .
      FILTER(?StatisticalProgram IN (<https://bps.go.id/metadata/sirusa/statistical-program/Survei%20Angkatan%20Kerja%20Nasional%20%28SAKERNAS%29>)) .
      BIND("Sistem Rujukan Statistik" as ?ApplicationPackage) .
    }
  }
  UNION
  {
    #From dataset Survey management
      ?StatisticalProgram_CollectionSystem a :StatisticalProgram ; gsim-sum:hasName-IA ?StatisticalProgramName .
      ?StatisticalProgram :hasSP-SPC ?StatisticalProgramCycle .
      ?StatisticalProgramCycle gsim-sum:hasName-IA ?StatisticalProgramCycleName .
      ?StatisticalProgramCycle :includesSPC-BP ?BusinessProcess .
      ?BusinessProcess :hasBP-PS ?ProcessStep .
      ?ProcessStep rdfs:label ?ProcessStepName .
      ?ProcessStep :classifiedAs-PS ?GSBPM_code .
      BIND("Collection System" as ?ApplicationPackage) .

      #Filter by owl:sameAs
      ?StatisticalProgram owl:sameAs ?StatisticalProgram_CollectionSystem .
  }

}
LIMIT 100
```

Result
|StatisticalProgramName |StatisticalProgramCycleName |BusinessProcess |ProcessStepName |GSBPM_code |ApplicationPackage |
|-----------------------------------------|------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|------------------------------------|------------------------|
|Survei Angkatan Kerja Nasional (SAKERNAS)|Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|https://bps.go.id/metadata/sirusa/business-process/Survei%20Angkatan%20Kerja%20Nasional%20%28SAKERNAS%29/2024 |Process Step - Design Variable Description - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|http://id.unece.org/models/gsbpm/2.2|Sistem Rujukan Statistik|
|Survei Angkatan Kerja Nasional (SAKERNAS)|Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024|https://bps.go.id/metadata/sirusa/business-process/Survei%20Angkatan%20Kerja%20Nasional%20%28SAKERNAS%29/2024 |Process Step - Design Design Output - Survei Angkatan Kerja Nasional (SAKERNAS) periode 2024 |http://id.unece.org/models/gsbpm/2.1|Sistem Rujukan Statistik|
|SAKERNAS 2024 FEB - PENDATAAN |Februari 2024 |https://bps.go.id/metadata/collection-system/business-process/903c27f9-3f93-41e0-9333-f261f43582db/07d004dc-9c61-448d-a1b7-b275b60fac5d|Process Step - Build Collection Instrument - SAKERNAS 2024 FEB - PENDATAAN periode Februari 2024 |http://id.unece.org/models/gsbpm/3.1|Collection System |
