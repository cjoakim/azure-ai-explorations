# python-core readme

## Links

- [azure-cosmos lib on PyPi](https://pypi.org/project/azure-cosmos/)
- [GitHub azure-sdk-for-python](https://github.com/Azure/azure-sdk-for-python)
- See the https://cosmos.azure.com/ Portal for ad-hoc queries

## Cosmos DB NoSQL API Queries

### Count the Documents in a Container

```
SELECT count(1) FROM c
```

### Vector Search

```
SELECT TOP 12 c.id, c.pk, c.name, VectorDistance(
    c.embedding, [-0.00011316168092889711, ... -0.054162509739398956]) AS SimilarityScore
 FROM c
 ORDER BY VectorDistance(
    c.embedding, [-0.00011316168092889711, ... -0.054162509739398956])
```