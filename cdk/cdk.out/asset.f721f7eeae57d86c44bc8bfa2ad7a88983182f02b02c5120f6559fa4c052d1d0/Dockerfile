FROM public.ecr.aws/lambda/python:3.12

# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}

# Install dependencies if needed
COPY requirements.txt .
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Command to run the Lambda function
CMD ["app.lambda_handler"]
