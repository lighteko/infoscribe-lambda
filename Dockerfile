FROM public.ecr.aws/lambda/python:3.12

RUN apt-get update && apt-get install -y --no-install-recommends \
  gcc \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /var/task

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["main.lambda_handler"]
