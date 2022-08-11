FROM python:3.8

run mkdir ./reports/
COPY finops_report_automation ./finops_report_automation
COPY pyproject.toml ./
COPY config/ ./config/
ENV PYTHONPATH=${PYTHONPATH}:${PWD} 
RUN pip3 install poetry && poetry config virtualenvs.create false && poetry install --no-dev


ENTRYPOINT ["python", "-m", "finops_report_automation.main"]