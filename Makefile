install:
	curl -LsSf https://astral.sh/uv/install.sh | sh
	uv sync
	brew install poppler

fetch_data:
	mkdir -p data/raw_data/sentencias_data
	mkdir -p data/raw_data/tesis_data
	curl -fL -o data/raw_data/sentencias_data/Sentencia.csv https://github.com/mafermunoz94/project_accountable_justice_lab_data/releases/download/v1.0.0/Sentencia.csv
	curl -fL -o data/raw_data/tesis_data/Tesis.csv https://github.com/mafermunoz94/project_accountable_justice_lab_data/releases/download/v1.0.0/Tesis.csv

data_extraction:
	uv run -m src.extraction
	uv run src/cleaning_and_processing/declaraciones/compiled_dataset.py
	uv run src/extraction/declaraciones/pdf_download_and_layout.py
	uv run src/cleaning_and_processing/declaraciones/final_variables.py
	uv run src/extraction/declaraciones/pdf_download_and_layout.py
	uv run src/cleaning_and_processing/declaraciones/json_inmuebles_to_excel.py

clean_data:
	uv run -m src.cleaning_and_processing

analysis:
	uv run src/analysis/solicitudes/indices_solicitudes.py

app:
	uv run streamlit run src/app/app.py