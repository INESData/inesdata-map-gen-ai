
def get_prompt(data_source_schema, ontology):
    prompt = f"""
        [INST] You are an expert in creating a csv string. The query will consist of Ontologies and Data source schema. 
        You need to extract the relevant parts to generate a csv string containing the following column: 
        ontology, logical_source_value, reference_formulation, iterator, subject_map_value, predicate_map_type, predicate_map_value, object_map_type and object_map_value. 
        Identify and map the relevant fields from the ontology and data source schema to the required columns. 
        For each entry in the ontology and data source schema, extract the values for the mapped fields. 
        Construct a row with the extracted values and combine the row into a single string, with each value separated by a pipe (|) and each row separated by a newline (\n). 
        Ensure the first row contains the column headers. Concatenate the header row and the data rows to form the final CSV string.
 
        Here is the format of the expected output for an ontology and a people data source:
        ontology|logical_source_value|reference_formulation|iterator|subject_map_value|predicate_map_type|predicate_map_value|object_map_type|object_map_value
        people.ttl|people.csv|csv|/rows/row|Person|rml:reference|hasName|xsd:string|name
        people.ttl|people.csv|csv|/rows/row|Person|rml:reference|hasAge|xsd:integer|age
 
        Here is the query from the user. Please analyse and do as described above.
        {ontology}
   
        Data source schema:
        {data_source_schema}
 
        Just generate the csv string.
        [/INST]
    """
    return prompt
