# Usually requried in order to have Python find your package
PYTHONPATH=.:$PYTHONPATH

GML_FILES=input
# GML_FILES=/Users/just/project/stetl/contrib/astun/osdata/58116-SX9192-2c1.gml

stetl -c stetl.cfg  -a "database=ordsurvey host=localhost port=5432 user=postgres password=postgres schema=osmm temp_dir=temp max_features=5000 gml_files=$GML_FILES"