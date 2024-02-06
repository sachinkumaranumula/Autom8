# References
- https://python-poetry.org/docs/cli/
- https://docs.conda.io/projects/conda/en/stable/commands/index.html
- https://www.pythoncheatsheet.org/blog/python-projects-with-poetry-and-vscode-part-1
- https://stackoverflow.com/questions/70851048/does-it-make-sense-to-use-conda-poetry
- https://github.com/conda-incubator/conda-tree

# Setup
- `source tools/conda_import.sh`
- `source tools/conda_update.sh`
- Ensure VS Code to select the right Python Interpreter i.e. *'arch-crawler-exporter': conda* in the status bar
  
# Run
```bash
python crawler-exporter.py -cf config.json
```

# Future
[Hexagonal Architecture](https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/structure-a-python-project-in-hexagonal-architecture-using-aws-lambda.html?did=pg_card&trk=pg_card)
