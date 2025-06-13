# python-core readme

## General Links

- [GitHub azure-sdk-for-python](https://github.com/Azure/azure-sdk-for-python)
  - A monorepo for all Azure Python SDKs
  - Subdirectories by Azure product SDK:
    - [cosmos](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos)
    - [cognitiveservices](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitiveservices)
    - [documentintelligence](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/documentintelligence)
    - [openai (samples)](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/openai)

---

## Azure Document Intelligence

### Links

- [azure-ai-documentintelligence lib @ PyPi](https://pypi.org/project/azure-ai-documentintelligence/)
- https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/documentintelligence
- [Document Intelligence Studio](https://documentintelligence.ai.azure.com/studio/document )

### Sample Documents

- [FIDE Laws Of Chess](https://www.fide.com/FIDE/handbook/LawsOfChess.pdf)
- [NFL Rulebook 2022](https://operations.nfl.com/media/5kvgzyss/2022-nfl-rulebook-final.pdf)
- [NFL Rulebook 2020](https://operations.nfl.com/media/4693/2020-nfl-rulebook.pdf)
- [Rules of Basketball, w/Naismith](http://fs.ncaa.org/Docs/stats/m_basketball_RB/2017/Rules.pdf)
- [Rules of Baseball](https://img.mlbstatic.com/mlb-images/image/upload/mlb/atcjzj9j7wrgvsm8wnjq.pdf)
- [Simplified Pickleball Rules](https://www.wittbirn.k12.wi.us/faculty/tbacon/Studyguides/Pickleball.pdf)
- [Simplified Soccer Rules](https://cdn1.sportngin.com/attachments/document/bb8a-2479018/FOSC_Laws_of_the_Game__simplified_.pdf)
- [Introductory Rules of Checkers](https://www.hasbro.com/common/instruct/Checkers.PDF)
- [Davidson College Academic Regulations](https://www.davidson.edu/media/12179/download)


---

## Cosmos DB NoSQL API Queries

- [azure-cosmos lib @ PyPi](https://pypi.org/project/azure-cosmos/)
- https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cosmos
- See the https://cosmos.azure.com/ Portal for ad-hoc queries

### Count the Documents in a Container

```
SELECT count(1) FROM c
```

### DiskANN Vector Index

[cosmosdb_nosql_libraries_index_policy_diskann.json](python-core/cosmos/cosmosdb_nosql_libraries_index_policy_diskann.json)

```
    "vectorIndexes": [
        {
            "path": "/embedding",
            "type": "diskANN",
            "quantizationByteSize": 96,
            "indexingSearchListSize": 100
        }
    ]
```

### Vector Search

```
SELECT TOP 12 c.id, c.pk, c.name, VectorDistance(
    c.embedding, [-0.00011316168092889711, ... -0.054162509739398956]) AS SimilarityScore
 FROM c
 ORDER BY VectorDistance(
    c.embedding, [-0.00011316168092889711, ... -0.054162509739398956])
```