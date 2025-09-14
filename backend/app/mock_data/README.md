# How to fill the data on S3 and sqlite3

- Clear the S3 bucket "remind-me-image-storage"
- Remove the dev.sqlite3 under folder backend/app/
- run "generate_sqlite3_tables.py" to generate tables.
- run "generate_insertion_data_from_S3.py" <br>
  copy the generated records from the terminal window into "generate_sqlite3_data.py".
- run "generate_sqlite3_data.py" to fill the dev.sqlite3.
- run "generate_sqlite3_LLM_summary.py" to fill the LLM summary into dev.sqlite3.

<br>

# How to fill the data on S3 and postgresql

- Clear the S3 bucket "remind-me-image-storage"
- Clear the postgresql database.
- Run the scripts in postgresql admin to create tables.
- run "generate_insertion_data_from_S3.py" <br>
- copy the generated records from the terminal window to the postgresql admin and **execute**.<br>
- run "LLM_generate_summary.py" to fill the LLM summary into postgresql.
