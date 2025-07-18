Develop a Management Control Platform (MCP) server for Azure Databricks, utilising the following REST API endpoints:

**1. Cluster Management:**

- **Create Cluster:** `POST /api/2.0/clusters/create`
- **Terminate Cluster:** `POST /api/2.0/clusters/delete`
- **List Clusters:** `GET /api/2.0/clusters/list`

**2. Job Management:**

- **Create Job:** `POST /api/2.0/jobs/create`
- **Run Job:** `POST /api/2.0/jobs/run-now`
- **List Jobs:** `GET /api/2.0/jobs/list`

**3. Notebook Operations:**

- **Import Notebook:** `POST /api/2.0/workspace/import`
- **Export Notebook:** `GET /api/2.0/workspace/export`
- **List Notebooks:** `GET /api/2.0/workspace/list`

**4. Databricks File System (DBFS):**

- **Upload File:** `POST /api/2.0/dbfs/put`
- **List Files:** `GET /api/2.0/dbfs/list`
- **Delete File:** `POST /api/2.0/dbfs/delete`

**5. SQL Statement Execution:**

- **Execute SQL Statement:** `POST /api/2.0/sql/statements/execute`

**6. Unity Catalog Management:**

- **Catalog Operations:**
  - **Create Catalog:** `POST /api/2.0/unity-catalog/catalogs`
  - **List Catalogs:** `GET /api/2.0/unity-catalog/catalogs`
  - **Delete Catalog:** `DELETE /api/2.0/unity-catalog/catalogs/{name}`

- **Schema Operations:**
  - **Create Schema:** `POST /api/2.0/unity-catalog/schemas`
  - **List Schemas:** `GET /api/2.0/unity-catalog/schemas`
  - **Delete Schema:** `DELETE /api/2.0/unity-catalog/schemas/{full_name}`

- **Table Operations:**
  - **Create Table:** `POST /api/2.0/unity-catalog/tables`
  - **List Tables:** `GET /api/2.0/unity-catalog/tables`
  - **Delete Table:** `DELETE /api/2.0/unity-catalog/tables/{full_name}`

- **Data Lineage:**
  - **Get Table Lineage:** `GET /api/2.0/unity-catalog/lineage-tracking/table-lineage/{table_name}`
  - **Get Column Lineage:** `GET /api/2.0/unity-catalog/lineage-tracking/column-lineage/{column_name}`

**7. Delta Live Tables Pipelines:**

- **Pipeline Management:**
  - **Create Pipeline:** `POST /api/2.0/pipelines`
  - **List Pipelines:** `GET /api/2.0/pipelines`
  - **Get Pipeline:** `GET /api/2.0/pipelines/{pipeline_id}`
  - **Update Pipeline:** `PUT /api/2.0/pipelines/{pipeline_id}`
  - **Delete Pipeline:** `DELETE /api/2.0/pipelines/{pipeline_id}`

- **Pipeline Execution:**
  - **Start Update:** `POST /api/2.0/pipelines/{pipeline_id}/updates`
  - **List Updates:** `GET /api/2.0/pipelines/{pipeline_id}/updates`
  - **Get Update:** `GET /api/2.0/pipelines/{pipeline_id}/updates/{update_id}`

**8. Databricks SQL Queries:**

- **Query Management:**
  - **Create Query:** `POST /api/2.0/preview/sql/queries`
  - **List Queries:** `GET /api/2.0/preview/sql/queries`
  - **Get Query:** `GET /api/2.0/preview/sql/queries/{query_id}`
  - **Update Query:** `POST /api/2.0/preview/sql/queries/{query_id}`
  - **Delete Query:** `DELETE /api/2.0/preview/sql/queries/{query_id}`

**9. Model Serving Endpoints:**

- **Serving Endpoint Management:**
  - **Create Serving Endpoint:** `POST /api/2.0/serving-endpoints`
  - **Get Serving Endpoint:** `GET /api/2.0/serving-endpoints/{name}`
  - **Update Serving Endpoint Config:** `PUT /api/2.0/serving-endpoints/{name}/config`
  - **Delete Serving Endpoint:** `DELETE /api/2.0/serving-endpoints/{name}`

- **Querying Serving Endpoints:**
  - **Query Serving Endpoint:** `POST /serving-endpoints/{name}/invocations`

Integrating these API endpoints into our MCP server will enable comprehensive management of our Azure Databricks environment, covering clusters, jobs, notebooks, file systems, SQL execution, Unity Catalog, Delta Live Tables, SQL queries, and model serving. This will also provide a platform that we can add new features when needed.