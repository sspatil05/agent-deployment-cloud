FROM python:3.12-slim
WORKDIR /app
COPY app.py .
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin appuser
USER 10001
ENV PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["python", "app.py"]