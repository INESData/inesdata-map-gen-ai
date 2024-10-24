
def get_prompt(data_source_schema, ontology):
    prompt = f"""
        Necesito generar unas tablas de mapeos que emparejen las columnas de una fuente de datos con los campos de una ontología específica, separando en tablas de prefijos, sujetos fuentes y predicados. Aquí tienes un ejemplo del mapeo esperado para una ontología y una fuente de datos de personas:        
        ### OUTPUT esperado:
        #### Tabla de prefijos:
        Prefix|URI
        ex|http://example.org
        rdf|http://www.w3.org/1999/02/22-rdf-syntax-ns#
        rdfs|http://www.w3.org/2000/01/rdf-schema#
        
        #### Tabla de sujetos:
        ID|Class|URI
        Person|ex:Person
        
        #### Tabla de fuentes:
        ID|Feature|Value
        Person|source|inesdata-map/data/input/datasources/people.csv
        Person|format|CSV
        
        #### Tabla de predicados:
        ID|Predicate|Object|DataType|Language
        Person|ex:hasName|hasName|string|en
        Person|ex:hasAge|hasAge|string|en
        
        
        ### INPUT:
        #### Ontología:
        {ontology}
    
        #### Esquema de la fuente de datos (en formato CSV):
        {data_source_schema}
        """
    return prompt
