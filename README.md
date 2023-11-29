# inspire-aanmerkingsregister-csv

Repository containing [Python script](./crawler.py) to crawl [inspireaanmerking.nl](https://www.inspireaanmerking.nl/aanmerkingsregister) to generate CSV file of all INSPIRE assigned (Dutch: aangemerkte) datasets. 

Repository also contains a [Github Action workflow](./.github/workflows/crawl-inspireaanmerking-nl.yaml), that will run on 00:00 every Sunday to automatically update [`inspireaanmerking.nl.csv`](./inspireaanmerking.nl.csv). 

After running the workflow a commit with the message `update inspireaanmerking.nl.csv` will be done on this repository. When the file remains unchanged this will be an empty commit (containing no changes). This makes it easy to check the recency of the [`inspireaanmerking.nl.csv`](./inspireaanmerking.nl.csv) file.
