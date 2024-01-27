```bash
uvicorn main:app --env-file environment.txt --port 8001
```

```bash
pytest --cov-report term-missing --cov=src --log-cli-level=INFO -x
```

```bash
pytest -k "test_FillDataViaGQL" --cov-report term-missing --cov=src --log-cli-level=INFO -x
```