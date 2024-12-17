
def get_prompt(data_source_schema, ontology):
    prompt = f"""
        Necesito generar una tabla de mapeos que emparejen las columnas de una fuente de datos con los campos de una ontología específica. 
        Aquí tienes un ejemplo del mapeo esperado para una ontología y una fuente de datos de personas:
        ### OUTPUT esperado:
        ontology|logical_source|reference_formulation|iterator|subject|class|predicate|object|object_type
        inesdata-map/data/input/ontologies/people.ttl|inesdata-map/data/input/datasources/people.csv|csv|None|Person|ex:Person|ex:hasName|hasName|xsd:string
        inesdata-map/data/input/ontologies/people.ttl|inesdata-map/data/input/datasources/people.csv|csv|None|Person|ex:Person|ex:hasAge|hasAge|xsd:string
        
        ### INPUT:
        #### Ontología:
        {ontology}
    
        #### Esquema de la fuente de datos:
        {data_source_schema}
        """
    return prompt
