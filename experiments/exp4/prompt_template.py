
def get_prompt(data_source_schema, ontology_field):
    prompt = f"""
        Necesito generar un mapeo RML (RDF Mapping Language) que empareje una columna de una fuente de datos con un campo de una ontología específica. Aquí tienes un ejemplo del mapeo RML esperado:
        ### INPUT:
        #### Ontología:
        ex:Person a rdfs:Class .
    
        #### Esquema de la fuente de datos (en formato CSV):
        id,name,age
        
        ### OUTPUT:
        rr:subjectMap [
            rr:template "http://example.org/person/{id}" ;
            rr:class ex:Person ;
        ] ;

        ### Requisitos:
        1. Usa el campo de la ontología proporcionada para definir las clases y propiedades en el RML.
        2. Cada columna de la fuente de datos debe mapearse a una propiedad adecuada de la ontología.
        3. Asegúrate de definir los TriplesMap, LogicalSource, SubjectMap, PredicateObjectMap, y cualquier otra estructura necesaria de acuerdo con la especificación RML.
        4. El RML generado debe ser válido y compatible con motores de mapeo RML, como RMLMapper.

        Proporciona el contenido completo del fichero RML en formato texto. No incluyas saltos de linea al comienzo del fichero ni triples comillas. No devuelvas más contenido aparte del RML.
        
        INPUT:
        - Campo de la ontología:
        {ontology_field}
        - Esquema de la fuente de datos (en formato CSV):
        {data_source_schema}
        """
    return prompt
