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
        3. iterator: The path for iterating over the data entries in the schema (e.g., "/rows/row").
        4. subject_map_value: The subject class from the ontology (i.e., a unique identifier for the subject of RDF triples).
        5. subject_ontology: The ontology of the subject class.
        6. predicate_map_type: The type of the predicate map, usually identified by the RDF property.
        7. predicate_map_value: The property from an ontology that links the subject to the object.
        8. predicate_ontology: The ontology of the predicate.
        9. object_map_type: The type of the object (e.g., a literal, URI, or a reference to a data column).
        10. object_map_value: The actual value or column from the data source schema that corresponds to the object in the RDF mapping.

    ### RULES AND CONSTRAINTS:
    You should ensure the following:
    - Use dynamic URIs for subject and object maps wherever applicable.
    - The ontology of the subject can be different from the ontologies of the rest of the predicates.
    - RDF predicates must be selected from one of the ontologies and correctly linked to the subject.
    - The object can be a reference to a column or a constant value.
    - The output must be formatted in CSV string format, separated by a pipe |. The first row should be column headers, followed by the mapping rules.
    - Map columns correctly by ensuring the correct data types (e.g., integers, literals).
    - Do not modify or add any extra rows or columns in the CSV output.

    ### EXAMPLE OUTPUT:
    The following is an example of the correctly formatted output based on a sample ontology and data source schema:

    Sample Input:
        This RDF ontology defines an ex:Airport class and related properties like ex:hasName, ex:hasLocation, and ex:hasAirportCode.
        ### Ontologies :
            airports.ttl:
            @prefix ex: <http://example.org/> .
            @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

            ex:Airport a rdfs:Class .
            ex:hasName a rdf:Property ;
            rdfs:domain ex:Airport ;
            rdfs:range rdfs:Literal .

            ex:hasLocation a rdf:Property ;
            rdfs:domain ex:Airport ;
            rdfs:range rdfs:Literal .

            ex:hasAirportCode a rdf:Property ;
            rdfs:domain ex:Airport ;
            rdfs:range rdfs:Literal .

        The file contains information about airports, including their IDs, names, locations, and airport codes.
        ### Data source schema:
            airports.csv:
            id,name,location,airport_code

        ### Output:
        This is the output you would expect after processing the data source and ontology according to the RML mapping rules. The output should be in CSV format.
            logical_source_value|reference_formulation|iterator|subject_map_value|subject_ontology|predicate_map_type|predicate_map_value|predicate_ontology|object_map_type|object_map_value
            airport.csv|csv|/rows/row|Airport|airports.ttl|rml:reference|ex:hasName|airports.ttl|rdfs:Literal|name
            airport.csv|csv|/rows/row|Airport|airports.ttl|rml:reference|ex:hasLocation|airports.ttl|rdfs:Literal|location
            airport.csv|csv|/rows/row|Airport|airports.ttl|rml:reference|ex:hasAirportCode|airports.ttl|rdfs:Literal|airport_code


    ### INPUT:
    Here is the required input of the user:
        #### Ontologies:
        {ontology}
   
        #### Data source schema:
        {data_source_schema}

        [/INST]
    """
    return prompt
