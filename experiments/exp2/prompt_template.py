
def get_prompt(data_source, ontology):
    prompt = f"""
        Necesito generar un fichero RML (RDF Mapping Language) que mapee una fuente de datos a RML usando una ontología específica. Aquí tienes un ejemplo del mapeo RML esperado:
        ### INPUT:
        #### Ontología:
        @prefix ex: <http://example.org/> .
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

        ex:Person a rdfs:Class .
        ex:hasName a rdf:Property ;
            rdfs:domain ex:Person ;
            rdfs:range rdfs:Literal .
        ex:hasAge a rdf:Property ;
            rdfs:domain ex:Person ;
            rdfs:range rdfs:Literal .
    
        #### Esquema de la fuente de datos (en formato CSV):
        id,name,age
        
        ### OUTPUT:
        @prefix rr: <http://www.w3.org/ns/r2rml#> .
        @prefix rml: <http://semweb.mmlab.be/ns/rml#> .
        @prefix ex: <http://example.org/> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        <#Mapping>
            rml:logicalSource [
                rml:source "people.csv" ;
                rml:referenceFormulation rml:CSV ;
                rml:iterator "/rows/row" ;
            ] ;
            rr:subjectMap [
                rr:template "http://example.org/person/{id}" ;
                rr:class ex:Person ;
            ] ;
            rr:predicateObjectMap [
                rr:predicate ex:hasName ;
                rr:objectMap [
                    rml:reference "name" ;
                ] ;
            ] ;
            rr:predicateObjectMap [
                rr:predicate ex:hasAge ;
                rr:objectMap [
                    rml:reference "age" ;
                    rr:datatype xsd:integer ;
                ] ;
            ] .

        ### Requisitos:
        1. Usa la ontología proporcionada para definir las clases y propiedades en el RML.
        2. Cada columna de la fuente de datos debe mapearse a una propiedad adecuada de la ontología.
        3. Genera un mapeo para cada tabla de la fuente de datos.
        4. Asegúrate de definir los TriplesMap, LogicalSource, SubjectMap, PredicateObjectMap, y cualquier otra estructura necesaria de acuerdo con la especificación RML.
        5. El RML generado debe ser válido y compatible con motores de mapeo RML, como RMLMapper.

        Proporciona el contenido completo del fichero RML en formato texto. No incluyas saltos de linea al comienzo del fichero ni triples comillas. No devuelvas más contenido aparte del RML.
        
        ### INPUT:
        #### Ontología:
        {ontology}
        #### Esquema de la fuente de datos (en formato CSV):
        {data_source}
        """
    return prompt
