FROM amazonlinux:2023

RUN yum install -y \
    gcc \
    git \
    python3 \
    python3-pip \
    zip \
    && yum clean all

RUN python3 -m pip install --upgrade --ignore-installed pip

WORKDIR /var/task

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "-m", "awslambdaric", "main.lambda_handler"]
