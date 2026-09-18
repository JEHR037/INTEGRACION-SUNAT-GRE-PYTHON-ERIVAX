# SUNAT Integration System

Integration with the SUNAT API for generating and submitting the XML documents behind
Peruvian electronic shipping guides (guias de remision electronicas). The system signs users
in, builds XML that conforms to the SUNAT schemas, submits it, and handles the response,
including receiving and unpacking the CDR acknowledgement.

## Features

- XML generation conforming to the SUNAT schemas.
- Submission to SUNAT and response handling, CDR included.
- User authentication and session management.
- Web interface for building and submitting documents.
- Automatic refresh of authentication tokens so the SUNAT session stays alive.
- Activity log and submission history for tracing operations.

## Stack

| Concern        | Technology                              |
| -------------- | --------------------------------------- |
| Web framework  | Flask                                   |
| Backend        | Python                                  |
| Frontend       | HTML, CSS, JavaScript                   |
| HTTP           | Requests                                |
| XML            | lxml, ElementTree                       |
| Encoding       | base64, hashlib                         |
| Configuration  | JSON                                    |
| Distribution   | Waitress, PyInstaller                   |

## Install

```sh
git clone https://github.com/JEHR037/INTEGRACION-SUNAT-GRE-PYTHON-ERIVAX.git
cd INTEGRACION-SUNAT-GRE-PYTHON-ERIVAX
pip install -r requirements.txt
```

Set the required environment variables, including the SUNAT API credentials, then start the
server:

```sh
python app.py
```

To produce a distributable build:

```sh
pyinstaller app.py
```

## Usage

1. Sign in with your user credentials.
2. Open the XML generation view and fill in the fields for the document.
3. Submit the XML to SUNAT from the interface.
4. Check the submission status and read the CDR returned inside the response zip.

## Layout

| Path         | Responsibility                                          |
| ------------ | ------------------------------------------------------- |
| `app.py`     | Flask entry point and routes                            |
| `acceso.py`  | Authentication token management and refresh             |
| `templates/` | HTML templates for the interface                        |
| `static/`    | CSS, JavaScript and images                              |

## Contributing

Open an issue to discuss a change, or send a pull request.

## License

MIT.

## Author

Javier Hernandez — [LinkedIn](https://www.linkedin.com/in/javier-hernandezjh/)
