import logging
import os
from rest_framework.response import Response

message_code_map = {
    200: {
        'http_status_code': 200,
        'message': "Request Process Successfully"
    },
    400: {
        'http_status_code': 400,
        'message': "Invalid value for {field_name}"
    },
    500: {
        'http_status_code': 500,
        'message': "Internal Server Error"
    }

}

logger = logging.getLogger('django')


def log_and_respond(message_code, field_name=None,
                    response_data=None, exception=None):

    if exception:
        logging.info('*' * 100)
        logger.error({
            "exception": exception
        })
        logging.info('*' * 100)

    message_metadata = message_code_map[message_code]
    http_status_code = message_metadata['http_status_code']
    message = message_metadata["message"]

    if field_name:
        try:
            message = message.format(field_name=field_name)
        except:
            message = "Something went wrong"

    response_body = {
        "message_code": message_code,
        "message": message,
        "response_data": response_data
    }

    return Response(response_body, http_status_code)
