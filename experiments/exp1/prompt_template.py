
def get_prompt(data_source, ontology):
    prompt = f"""
        Necesito generar un fichero RML (RDF Mapping Language) que mapee una fuente de datos a RML usando una ontología específica.
        
        #### Ontología:
        {ontology}

        ### Fuente de datos (en formato CSV):
        {data_source}

        ### Requisitos:
        1. Usa la ontología proporcionada para definir las clases y propiedades en el RML.
        2. Cada columna de la fuente de datos debe mapearse a una propiedad adecuada de la ontología.
        3. Genera un mapeo para cada tabla de la fuente de datos.
        4. Asegúrate de definir los TriplesMap, LogicalSource, SubjectMap, PredicateObjectMap, y cualquier otra estructura necesaria de acuerdo con la especificación RML.
        5. El RML generado debe ser válido y compatible con motores de mapeo RML, como RMLMapper.

        Proporciona el contenido completo del fichero RML en formato texto. No incluyas saltos de linea al comienzo del fichero ni triples comillas. No devuelvas más contenido aparte del RML.
        """
    return prompt
