# INESDATA-MAP: GEN_AI_MAPPING

**`gen_ai_mapping`** es un paquete de Python cuya finalidad es **utilizar la IA generativa para generar automáticamente un mapping desde la web de _INESDATA-MAP mapper_**. La web se encarga de realizar una llamada a dicho paquete con los siguientes inputs de entrada:

- Listado de **ids de las ontologías** involucradas en el mapeo.
- Listado de **ids de las fuentes de datos** involucradas en el mapeo.

Estos ids son los correspondientes identificadores dentro de la base de datos del backend de la web de [_INESDATA-MAP mapper_](https://github.com/INESData/inesdata-map/tree/main), por lo que es necesario también conectarse a dicha BD, usando las siguientes variables de entorno:

- `SPRING_DATASOURCE_URL`: Cadena de conexión a la base de datos del backend de la web (e.g. `<db_driver>:<db_type>://<db-host>:<port>/<db_name>`).
- `SPRING_DATASOURCE_USERNAME`: Usuario de la base de datos.
- `SPRING_DATASOURCE_PASSWORD`: Contraseña de la base de datos.

De esta forma, el módulo `gen_ai_mapping` se encarga de:

1. Conectarse a la **BD del backend de la web de _INESDATA-MAP mapper_**:
    1.2. Acceder a la tabla de ontologías para **obtener las ontologías** con el id indicado en el input.
    1.3. Acceder a la tabla de fuentes de datos para **obtener las fuentes** con el id indicado en el input.
        1.3.1. Utilizar la columna del _path_ para obtener la ruta en disco donde está almacenada la fuente.
        1.3.2. Extraer el _esquema_ de cada fuente de datos, independientemente de su formato (XML, CSV, ...).
2. **Rellenar el prompt template** con ontologías y esquemas de fuentes de datos.
3. Llamada a la **inferencia del modelo LLM desplegado en KServe**: Para hacer posible la conexión con el LLM desplegado en Kubeflow, son necesarias las siguientes variables de entorno:

- `KUBEFLOW_LLM_ENDPOINT`: URL del endpoint LLM de Kubeflow (e.g., `https://kubeflow.ai.inesdata-project.eu/openai/v1/completions`).
- `KUBEFLOW_LLM_HOST`: URL del host de KServe (e.g., `mixtral87b.XXX.kserve.ai.inesdata-project.eu`).
- `KUBEFLOW_USERNAME`: Usuario de Kubeflow.
- `KUBEFLOW_PASSWORD`: Contraseña de Kubeflow.
- `HF_TOKEN`: Token de usuario de [Hugging Face](https://huggingface.co/settings/tokens) para el modelo tokenizador (e.g. `hf_XXX`).

**NOTA**. Si se desea probar otro modelo desplegado en otra nube (tenemos un ejemplo con **Azure OpenAI**):
- El modelo que se recomienda desplegar en Azure OpenAI, y con el que han sido realizadas las pruebas, es **`gpt-4o-mini`**, el cual aparece indicado en los parámetros `model` y `model-id` del archivo `gen_ai_mapping/azure_llm_params.json`.
- Para que se conecte al modelo de Azure y no al de Kubeflow (modelo por defecto), es necesario borrar la variable de entorno de Kubeflow `KUBEFLOW_LLM_ENDPOINT`.
- Y crear las nuevas variables de entorno:
    - `AZURE_LLM_ENDPOINT`: URL del endpoint LLM de Azure OpenAI (e.g. `https://<azure-openai-url>.openai.azure.com/openai/deployments/`).
    - `AZURE_API_KEY`: Credenciales de Azure.

4. Almacenamiento del **output resultante en disco**. Para ello es necesario la variable de entorno:
- `APP_DATAPROCESSINGPATH`: Ruta de guardado del output del paquete.

## Uso ▶️

Este paquete se ejecutaría de la siguiente forma:

```bash
python3 -m gen_ai_mapping -ds [121] -o [40]
```

Los argumentos son los siguientes:

- `data_sources` [`-ds`]: parámetro _obligatorio_ con el listado de identificadores de las fuentes de datos almacenadas en la base de datos del backend de la web de _INESDATA-MAP mapper_.
- `ontologies` [`-o`]: parámetro _obligatorio_ con el listado de identificadores de las ontologías almacenadas en la base de datos del backend de la web de _INESDATA-MAP mapper_.