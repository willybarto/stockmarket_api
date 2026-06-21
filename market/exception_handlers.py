from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            "error": True,
            "status_code": response.status_code,
        }

        if isinstance(response.data, dict) and "detail" in response.data:
            custom_data["detail"] = str(response.data["detail"])
        elif isinstance(response.data, list):
            custom_data["detail"] = response.data[0] if response.data else "Errore sconosciuto."
        elif isinstance(response.data, dict):
            custom_data["detail"] = "Errore di validazione."
            custom_data["errors"] = response.data
        else:
            custom_data["detail"] = str(response.data)

        status_messages = {
            400: "Richiesta non valida.",
            401: "Autenticazione richiesta.",
            403: "Permesso negato.",
            404: "Risorsa non trovata.",
            405: "Metodo HTTP non consentito.",
            429: "Troppe richieste. Riprova più tardi.",
        }

        if "detail" not in custom_data or not custom_data["detail"]:
            custom_data["detail"] = status_messages.get(
                response.status_code, "Errore del server."
            )

        response.data = custom_data

    return response
