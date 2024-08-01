gen-ai-rml-api
==============================

Generative AI for RML construction files

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

## Prerequisites

1. Clone the repository.

    ```bash
    git clone https://dev-git.labs.gmv.com/gmv-bda/upm/inesdata-map/generative-ai/gen-ai-rml-api
    ```

2. Install `apt-get install libpq-dev` and create virtual environment and activate it.

    ```bash
    make venv
    source venv/bin/activate
    ```

3. [Optional] Generate the package. This command will generate a wheel with the package and install it.

   ```bash
   make install
   ```

4. Create a configuration file named `.env` in the root folder of this project.

    ```bash
    APP_NAME=MyApp
    ADMIN_EMAIL=example@gmv.com
    DATABASE_URL=postgresql://admin:admin@localhost:5432/myDb
    ```
 
5. Run the Fastapi application.
   
   ```bash
   uvicorn gen-ai-rml-api.app:app
   ```

### Installing

A step by step series of examples that tell you how to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system


```bash
make test
```

## Deployment

```
Add additional notes about how to deploy this on a live system
```

## Contributing

```
Enter here the contributing parts in this project.
```

## Versioning

```
Put here the Versions of the project
```

## License

```
This project is licensed by ...
```

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
