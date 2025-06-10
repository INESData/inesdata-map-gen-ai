def get_prompt(data_source_schema, ontology):
    prompt = f"""
    [INST] 
    You are a highly experienced expert in Semantic Web technologies, specifically in RDF Data Transformation. Your task is to analyze a provided ontology and a data source schema, and generate the corresponding RML (RDF Mapping Language) mapping rules. The output must be in a predefined, structured tabular format, which you must strictly follow.

    ### TASK:
    You will be given a data source schema and an ontology.
    You will transform these inputs into RML mapping rules based on the RDF ontology and the data structure. Each row of the output will correspond to an RML mapping rule that specifies how a column from the data source maps to a predicate-object pair in the RDF graph.

    ### OUTPUT FORMAT:
    You must output a CSV string containing the following columns:
        1. logical_source_value: The name of the data source (usually the file name containing the data).
        2. reference_formulation: The format or reference type for the data source schema (e.g., "csv", "json").
        3. iterator: The path for iterating over the data entries in the schema. If file type is csv, this column should be null. Normally the iterator is only used for json and xml files. In json for example, to access the data to be modelled, the iterator is: $.items[*].language[*].term_entries[?(@.type.name=='term')].
        4. subject_map_value: The subject class from the ontology (i.e., a unique identifier for the subject of RDF triples).
        5. subject_template: Subject template, conformed by complete base url of subject ontology, without prefix, and a unique identifier for the subject of RDF triples, inside {{}}. 
        This is an IRI: the Internationalized Resource Identifier (IRI), as a complement to the Uniform Resource Identifier (URI). 
        An IRI is a sequence of characters from the Universal Character Set (Unicode/ISO 10646). 
        A mapping from IRIs to URIs is defined, which means that IRIs can be used instead of URIs, where appropriate, to identify resources. 
        Do not use other characters like '<' or '>', just the url and the subject identifier inside the characters {{}}. 
        IMPORTANT: Do not use prefixes, use the complete url, as in the examples provided below from airports, books and employees (e.g., "http://example.org/airport/{{id}}").
        6. subject_ontology: The ontology of the subject class. Do not use prefixes, use the complete url (e.g., "http://example.org/Airport").
        7. predicate_map_type: The type of the predicate map, usually identified by the RDF property.
        8. predicate_map_value: The property from an ontology that links the subject to the object. Do not use prefixes, use the complete url (e.g., "http://example.org/hasName").
        9. predicate_ontology: The ontology of the predicate.
        10. object_termtype: The termtype of the object (e.g., a literal, URI, or a reference to a data column).
        11. object_map_type: The datatype of the object. 
        All the valid types are here, so do not invent others: 
        ANY_URI = 'anyURI', BOOLEAN = 'boolean', DATE = 'date', DATE_TIME = 'dateTime', DATE_TIME_STAMP = 'dateTimeStamp', DECIMAL = 'decimal', 
        DOUBLE = 'double', FLOAT = 'float', INT = 'int', INTEGER = 'integer', LONG = 'long', NEGATIVE_INTEGER = 'negativeInteger', NON_NEGATIVE_INTEGER = 'nonNegativeInteger', 
        NON_POSITIVE_INTEGER = 'nonPositiveInteger', POSITIVE_INTEGER = 'positiveInteger', SHORT = 'short', STRING = 'string', TIME = 'time'.
        12. object_map_value: The actual value or column from the data source schema that corresponds to the object in the RDF mapping.

    ### RULES AND CONSTRAINTS:
    You should ensure the following:
    - Use dynamic URIs for subject and object maps wherever applicable.
    - Do not use prefixes abbreviatures for subject and predicates, user their corresponding URL instead. For example, if the subject is ex:Airport, use http://example.org/Airport.
    - In the template, do not use other characters like '<' or '>', just the url and the subject identifier inside the characters {{}}. 
    IMPORTANT: Do not use prefixes, use the complete url, as in the examples provided below from airports, books and employees (e.g., "http://example.org/airport/{{id}}").
    - Use the correct ontology prefix URL, that depending on the format of the ontology may be stated differently. In .ttl format prefixes are stated like this:    @prefix ex: <http://example.org/> . In .rdf format prefixes are stated like this xmlns:ex="http://example.org/#.
    - The ontology of the subject can be different from the ontologies of the rest of the predicates.
    - RDF predicates must be selected from one of the ontologies and correctly linked to the subject.
    - The object can be a reference to a column or a constant value.
    - The output must be formatted in CSV string format, separated by a pipe |. The first row should be column headers, followed by the mapping rules. 
    - Map columns correctly by ensuring the correct data types (e.g., integers, literals).
    - Do not modify or add any extra rows or columns in the CSV output.
    - Do not add any extra explanations, notes or comments, just the csv table.

    ### EXAMPLE OUTPUT:
    The following is an example of the correctly formatted output based on a sample ontology and data source schema:

    Sample Input:
        ### Ontologies :
            airports.ttl:
            @prefix ex: <http://example.org/> .
            @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
            @prefix rml: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#>.

            ex:Airport a rml:Class .
            ex:hasName a rdf:Property ;
            rml:domain ex:Airport ;
            rml:range rml:Literal .

            ex:hasLocation a rdf:Property ;
            rml:domain ex:Airport ;
            rml:range rml:Literal .

            ex:hasAirportCode a rdf:Property ;
            rml:domain ex:Airport ;
            rml:range rml:Literal .

        ### Data source schema:
            airports.csv:
            id,name,location,airport_code

        ### Output:
        logical_source_value|reference_formulation|iterator|subject_map_value|subject_template|subject_ontology|predicate_map_type|predicate_map_value|predicate_ontology|object_termtype|object_map_type|object_map_value
        airport.csv|csv|null|http://example.org/Airport|http://example.org/airport/{{id}}|airports.ttl|rml:reference|http://example.org/hasName|airports.ttl|rml:Literal|xsd:string|name
        airport.csv|csv|null|http://example.org/Airport|http://example.org/airport/{{id}}|airports.ttl|rml:reference|http://example.org/hasLocation|airports.ttl|rml:Literal|xsd:string|location
        airport.csv|csv|null|http://example.org/Airport|http://example.org/airport/{{id}}|airports.ttl|rml:reference|http://example.org/hasAirportCode|airports.ttl|rml:Literal|xsd:integer|airport_code

    Sample Input:
        ### Ontologies :
            books.ttl:
            @prefix ex: <http://example.org/> .
            @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
            @prefix rml: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#>.

            ex:Book a rml:Class .
            ex:hasTitle a rdf:Property ;
            rml:domain ex:Book ;
            rml:range rml:Literal .

            ex:hasAuthor a rdf:Property ;
            rml:domain ex:Book ;
            rml:range rml:Literal .

        ### Data source schema:
            books.csv:
            id,title,author

        ### Output:
        logical_source_value|reference_formulation|iterator|subject_map_value|subject_template|subject_ontology|predicate_map_type|predicate_map_value|predicate_ontology|object_termtype|object_map_type|object_map_value
        books.csv|csv|null|http://example.org/Book|http://example.org/book/{{id}}|books.ttl|rml:reference|http://example.org/hasTitle|books.ttl|rml:Literal|xsd:string|title
        books.csv|csv|null|http://example.org/Book|http://example.org/book/{{id}}|books.ttl|rml:reference|http://example.org/hasAuthor|books.ttl|rml:Literal|xsd:string|author

    Sample Input:
        ### Ontologies :
            employees.ttl:
            @prefix ex: <http://example.org/> .
            @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
            @prefix rml: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#>.

            ex:Employee a rml:Class .
            ex:hasName a rdf:Property ;
            rml:domain ex:Employee ;
            rml:range rml:Literal .

            ex:hasEmail a rdf:Property ;
            rml:domain ex:Employee ;
            rml:range rml:Literal .

            ex:hasSalary a rdf:Property ;
            rml:domain ex:Employee ;
            rml:range rml:Literal .

        ### Data source schema:
            employees.csv:
            id,name,email,salary

        ### Output:
        logical_source_value|reference_formulation|iterator|subject_map_value|subject_template|subject_ontology|predicate_map_type|predicate_map_value|predicate_ontology|object_termtype|object_map_type|object_map_value
        employees.csv|csv|null|http://example.org/Employee|http://example.org/employee/{{id}}|employees.ttl|rml:reference|http://example.org/hasName|employees.ttl|rml:Literal|xsd:string|name
        employees.csv|csv|null|http://example.org/Employee|http://example.org/employee/{{id}}|employees.ttl|rml:reference|http://example.org/hasEmail|employees.ttl|rml:Literal|xsd:string|email
        employees.csv|csv|null|http://example.org/Employee|http://example.org/employee/{{id}}|employees.ttl|rml:reference|http://example.org/hasSalary|employees.ttl|rml:Literal|xsd:integer|salary

    ### INPUT:
    Here is the required input of the user:
        #### Ontologies:
        {ontology}
    
        #### Data source schema:
        {data_source_schema}
    [/INST]
    """
    return prompt
