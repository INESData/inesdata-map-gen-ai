# INESDATA-MAP: GEN_AI_MAPPING

**`gen_ai_mapping`** es un paquete de Python cuya finalidad es **utilizar la IA generativa para generar automáticamente un mapping desde la web de _INESDATA-MAP mapper_**. La web se encarga de realizar una llamada a dicho paquete con los siguientes inputs de entrada:

- Listado de **ids de las ontologías** involucradas en el mapeo.
- Listado de **ids de las fuentes de datos** involucradas en el mapeo.

Estos ids son los correspondientes identificadores dentro de la base de datos del backend de la web de _INESDATA-MAP mapper_, por lo que es necesario también conectarse a dicha BD, usando las siguientes variables de entorno:

- `SPRING_DATASOURCE_URL`
- `SPRING_DATASOURCE_USERNAME`
- `SPRING_DATASOURCE_PASSWORD`

De esta forma, el módulo `gen_ai_mapping` se encarga de:

1. Conectarse a la **BD del backend de la web de _INESDATA-MAP mapper_**:
    1.2. Acceder a la tabla de ontologías para **obtener las ontologías** con el id indicado en el input.
    1.3. Acceder a la tabla de fuentes de datos para **obtener las fuentes** con el id indicado en el input.
        1.3.1. Utilizar la columna del _path_ para obtener la ruta en disco donde está almacenada la fuente.
        1.3.2. Extraer el _esquema_ de cada fuente de datos, independientemente de su formato (XML, CSV, ...).
2. **Rellenar el prompt template** con ontologías y esquemas de fuentes de datos.
3. Llamada a la **inferencia del modelo LLM desplegado en KServe**: Para realizar este paso, se deben crear dos variables de entorno adicionales (`KUBEFLOW_LLM_ENDPOINT` y `KUBEFLOW_LLM_HOST`) para indicar las URL’s del endpoint y el host de KServe, respectivamente. Para hacer posible la conexión con el LLM desplegado en Kubeflow, son necesarias también las siguientes variables de entorno:

- `KUBEFLOW_USERNAME`
- `KUBEFLOW_PASSWORD`

4. Almacenamiento del **output resultante en disco**. Para ello es necesario la variable de entorno `APP_DATAPROCESSINGPATH`, que indica la ruta de guardado del output del paquete.

## Uso ▶️

Este paquete se ejecutaría de la siguiente forma:

```bash
python3 -m gen_ai_mapping -ds [121] -o [40]
```

Los argumentos son los siguientes:

- `data_sources` [`-ds`]: parámetro _obligatorio_ con el listado de identificadores de las fuentes de datos almacenadas en la base de datos del backend de la web de _INESDATA-MAP mapper_.
- `ontologies` [`-o`]: parámetro _obligatorio_ con el listado de identificadores de las ontologías almacenadas en la base de datos del backend de la web de _INESDATA-MAP mapper_.
