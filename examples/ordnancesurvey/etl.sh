# Usually requried in order to have Python find your package
PYTHONPATH=.:$PYTHONPATH

stetl -c stetl.cfg  -a "database=ordsurvey host=localhost port=5432 user=postgres password=postgres schema=osmm temp_dir=temp max_features=30 gml_files=input"