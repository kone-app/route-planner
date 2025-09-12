FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt .
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY src/journey_service ${LAMBDA_TASK_ROOT}/journey_service

CMD ["journey_service.handler.lambda_handler"]
