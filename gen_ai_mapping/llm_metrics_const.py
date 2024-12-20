# Refined Query
RML_PARSING_QUERY= """
PREFIX rr: <http://www.w3.org/ns/r2rml#>
PREFIX rml: <http://semweb.mmlab.be/ns/rml#>

SELECT ?subject ?predicate ?object ?source
WHERE {
    # Extract logical source
    ?mapping rml:logicalSource ?logicalSource .
    ?logicalSource rml:source ?source .

    # Extract subjects
    ?subjectMap rr:template ?subjectTemplate;
                rr:class ?subject .

    # Extract predicates and objects
    ?predicateObjectMap rr:predicate ?predicate ;
                        rr:objectMap ?objectMap .
    ?objectMap rml:reference ?object .
}

"""
RML_PARSING_QUERY_1= """
PREFIX ex: <http://example.org/>

SELECT ?logical_source ?subject ?predicate ?object

WHERE {
  ?subject ?predicate ?object .
  ?subject ex:logical_source ?logical_source .
}
"""

RML_PARSING_QUERY_MORPH = """
    prefix rml: <http://w3id.org/rml/>
    prefix sd: <https://w3id.org/okn/o/sd#>

    SELECT DISTINCT 
        ?triples_map_id ?triples_map_type ?logical_source_type ?logical_source_value ?iterator ?reference_formulation
        ?subject_map_type ?subject_map_value ?subject_map ?subject_termtype
        ?predicate_map_type ?predicate_map_value
        ?object_map_type ?object_map_value ?object_map ?object_termtype
        ?lang_datatype ?lang_datatype_map_type ?lang_datatype_map_value
        ?graph_map_type ?graph_map_value

    WHERE {
        ?triples_map_id rml:logicalSource ?_source ;
                        a ?triples_map_type .
        OPTIONAL {
            # logical_source is optional because it can be specified with file_path in config (see #119)
            ?_source ?logical_source_type ?logical_source_value .
            OPTIONAL {
                ?logical_source_value sd:name ?logical_source_in_memory_value.
                BIND(CONCAT("{",?logical_source_in_memory_value,"}") AS ?logical_source_value)
            }
            FILTER ( ?logical_source_type IN ( rml:source, rml:tableName, rml:query ) ) .
        }
        OPTIONAL { ?_source rml:iterator ?iterator . }
        OPTIONAL { ?_source rml:referenceFormulation ?reference_formulation . }

    # Subject -------------------------------------------------------------------------
        ?triples_map_id rml:subjectMap ?subject_map .
        ?subject_map ?subject_map_type ?subject_map_value .
        FILTER ( ?subject_map_type IN (
                            rml:constant, rml:template, rml:reference, rml:quotedTriplesMap, rml:functionExecution ) ) .
        OPTIONAL { ?subject_map rml:termType ?subject_termtype . }

    # Predicate -----------------------------------------------------------------------
        OPTIONAL {
            ?triples_map_id rml:predicateObjectMap ?_predicate_object_map .
            ?_predicate_object_map rml:predicateMap ?_predicate_map .
            ?_predicate_map ?predicate_map_type ?predicate_map_value .
            FILTER ( ?predicate_map_type IN ( rml:constant, rml:template, rml:reference, rml:functionExecution ) ) .

    # Object --------------------------------------------------------------------------
            OPTIONAL {
                ?_predicate_object_map rml:objectMap ?object_map .
                ?object_map ?object_map_type ?object_map_value .
                FILTER ( ?object_map_type IN (
                            rml:constant, rml:template, rml:reference, rml:quotedTriplesMap, rml:functionExecution ) ) .
                OPTIONAL { ?object_map rml:termType ?object_termtype . }
                OPTIONAL {
                    ?object_map ?lang_datatype ?lang_datatype_map .
                    ?lang_datatype_map ?lang_datatype_map_type ?lang_datatype_map_value .
                    # remove xsd:string data types as it is equivalent to not specifying any data type
                    FILTER ( ?lang_datatype_map_value != <http://www.w3.org/2001/XMLSchema#string> ) .
                    FILTER ( ?lang_datatype_map_type IN ( rml:constant, rml:template, rml:reference, rml:functionExecution ) ) .
                }
            }
            OPTIONAL {
                ?_predicate_object_map rml:objectMap ?object_map .
                ?object_map rml:parentTriplesMap ?object_map_value .
                OPTIONAL { ?object_map rml:termType ?object_termtype . }
                BIND ( rml:parentTriplesMap AS ?object_map_type ) .
            }
            OPTIONAL {
                ?_predicate_object_map rml:graphMap ?graph_map .
                ?graph_map ?graph_map_type ?graph_map_value .
                FILTER ( ?graph_map_type IN ( rml:constant, rml:template, rml:reference, rml:functionExecution ) ) .
            }
        }
    }
"""

RML_PARSING_QUERY_MORPH_SIMPLIFIED = """
    prefix rml: <http://w3id.org/rml/>

    SELECT DISTINCT ?triples_map_id

    WHERE {
        ?triples_map_id rml:logicalSource .
    }
"""
