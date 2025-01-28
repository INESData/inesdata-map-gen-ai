import nltk
import pandas as pd
import rdflib
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from rdflib import Graph
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import f1_score
from morph_kgc.mapping.mapping_parser import (
    _r2rml_to_rml,
    _rml_legacy_to_rml,
    _rdf_class_to_pom,
    _expand_constant_shortcut_properties,
    _subject_graph_maps_to_pom,
    _complete_pom_with_default_graph,
    _complete_termtypes,
    _complete_triples_map_class,
    _validate_termtypes,
)

from llm_metrics_const import *
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
from io import StringIO


RML_COLS = [
    rdflib.term.Variable("logical_source_value"),
    rdflib.term.Variable("reference_formulation"),
    rdflib.term.Variable("iterator"),
    rdflib.term.Variable("subject_map_value"),
    rdflib.term.Variable("predicate_map_type"),
    rdflib.term.Variable("predicate_map_value"),
    rdflib.term.Variable("object_map_type"),
    rdflib.term.Variable("object_map_value"),
]

RML_COLS_STR = [
    "logical_source_value",
    "reference_formulation",
    "iterator",
    "subject_map_value",
    "predicate_map_type",
    "predicate_map_value",
    "object_map_type",
    "object_map_value",
]
    
    
def get_text_similarity(text1, text2):
    # Descargar recursos necesarios de NLTK
    nltk.download("punkt")
    nltk.download("punkt_tab")
    nltk.download("wordnet")
    nltk.download("stopwords")

    # Tokenize and lemmatize the texts
    tokens1 = word_tokenize(text1)
    tokens2 = word_tokenize(text2)
    lemmatizer = WordNetLemmatizer()
    tokens1 = [lemmatizer.lemmatize(token) for token in tokens1]
    tokens2 = [lemmatizer.lemmatize(token) for token in tokens2]

    # Remove stopwords
    stop_words = stopwords.words("english")
    tokens1 = [token for token in tokens1 if token not in stop_words]
    tokens2 = [token for token in tokens2 if token not in stop_words]

    # Create the TF-IDF vectors
    vectorizer = TfidfVectorizer()
    vector1 = vectorizer.fit_transform([" ".join(tokens1)])
    vector2 = vectorizer.transform([" ".join(tokens2)])

    # Calculate the cosine similarity
    similarity = cosine_similarity(vector1, vector2)

    return similarity[0][0]


def convert_to_rml(rml_string):
    # Creating a graph
    g = Graph()
    # parsing the string into rml format
    return g.parse(data=rml_string, format="turtle")


def normalize_mapping_graph(mapping_graph):
    # convert R2RML to RML
    mapping_graph = _r2rml_to_rml(mapping_graph)
    # convert legacy RML to RML
    mapping_graph = _rml_legacy_to_rml(mapping_graph)
    # convert rr:class to new POMs
    mapping_graph = _rdf_class_to_pom(mapping_graph)
    # expand constant shortcut properties rr:subject, rr:predicate, rr:object and rr:graph
    mapping_graph = _expand_constant_shortcut_properties(mapping_graph)
    # move graph maps in subject maps to the predicate object maps of subject maps
    mapping_graph = _subject_graph_maps_to_pom(mapping_graph)
    # complete predicate object maps without graph maps with rr:defaultGraph
    mapping_graph = _complete_pom_with_default_graph(mapping_graph)
    # if a term as no associated rr:termType, complete it according to R2RML specification
    mapping_graph = _complete_termtypes(mapping_graph)
    # add rr:TriplesMap typing
    mapping_graph = _complete_triples_map_class(mapping_graph)
    # check termtypes are correct
    _validate_termtypes(mapping_graph)
    return mapping_graph


def convert_to_df(mapping_graph):
    # Normalize mapping graph
    mapping_graph = normalize_mapping_graph(mapping_graph)
    # Parse the mappings using the SPARQL query
    rml_query_results = mapping_graph.query(RML_PARSING_QUERY_MORPH)
    # Convert Dict to DataFrame
    rml_df = pd.DataFrame(rml_query_results.bindings)
    # In csv cases, there is no iterator
    if rdflib.term.Variable("iterator") not in rml_df.columns:
        rml_df[rdflib.term.Variable("iterator")] = None

    return rml_df


def get_rml_metrics(mapping, llm_mapping):
    # convert into rdf graph
    mapping_graph = convert_to_rml(mapping)
    # convert into pandas dataframe
    rml = convert_to_df(mapping_graph)
    # selecting the required columns from rml    
    rml_df = rml[RML_COLS].copy()
    # changing the column names to strings
    rml_df.columns = RML_COLS_STR

    rml_rows = rml_df.shape[0]  # number of rml_rows
    # dropping last row which is not necessary
    rml_df.drop(index=rml_df.index[rml_rows - 1], inplace=True)
    rml_rows -= 1
    # convert csv string into dataframe given by LLM
    llm_mapping = llm_mapping.strip()
    if len(llm_mapping) == 0:
        return 0
    llm = pd.read_csv(StringIO(llm_mapping), sep="|")
    # selecting the columns from llm df
    llm_df = llm[RML_COLS_STR].copy()
    llm_rows = llm_df.shape[0]
    # printing the dataframes
    print("RML_DF:")
    print(rml_df)
    print("LLM_DF:")
    print(llm_df)
    # compare two pds

    columns = list(rml_df)  # list all the columns
    f1_list = []
    diff = abs(rml_rows - llm_rows)
    print(f'Difference: {diff}')

    if diff:
       # Align the DataFrames by filling missing rows with NaN
       max_rows = max(rml_rows, llm_rows)
       if rml_rows < llm_rows:
           rml_df = rml_df.reindex(range(max_rows)).fillna(np.nan).astype(str)
       else:
           llm_df = llm_df.reindex(range(max_rows)).fillna(np.nan).astype(str) 
       print('Adjusted RML:')
       print(rml_df)
       print('Adjusted LLM:')
       print(llm_df)
    # comparing the sub-df and llm-df
    for i in columns:
        print(f"COLUMN NAME: {i}")
        # striping blank spaces if present
        llm_df[i] = llm_df[i].str.strip()
        rml_df[i] = rml_df[i].str.strip()
        # print the Classification report
        print(classification_report(llm_df[i], rml_df[i]))
        # compute F1-scores
        f1 = f1_score(llm_df[i], rml_df[i], average="weighted")
        # add it to the list
        f1_list.append(f1)
    # return the average f1 score
    return sum(f1_list) / len(f1_list)
