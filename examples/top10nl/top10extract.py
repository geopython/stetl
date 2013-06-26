#!/usr/bin/env python
#
# Auteur: Frank Steggink, bewerkt door Just van den Broecke tbv voorbeeld Stetl embedding
# Doel: overzetten van een Top10NL GML-bestand naar een door OGR ondersteund formaat (bijv.
# PostGIS).

# Stappen:
# * SQL Scripts vooraf
# * Droppen tabellen
# * Validatie GML (optioneel)
# * Opsplitsen en transformeren GML
# * Laden data met OGR
# * Verwijderen duplicate data
# * SQL Scripts achteraf

# Dependencies:
# * Settings: etl-top10nl.cfg
# * GFS template: top10-v1.1.1.gfs
# * Opsplits-stylesheet (XSLT): top10-split_v1.1.1.xsl
# sql files in ./sql/

# Aanroepen:
# * met 1 GML-bestand
# * met bestandslijst(en) met GML-bestanden
# * met meerdere GML-bestanden via wildcard
# * met directory
# NB: ook als er meerdere bestanden via de command line aangegeven kunnen worden, kunnen deze
# wildcards bevatten. Een bestand wordt als GML-bestand beschouwd, indien deze de extensie GML of
# XML heeft, anders wordt het als een GML-bestandslijst gezien.

# Toepassen settings:
# * Definitie in settings-file
# * Mogelijk om settings te overriden via command-line parameters (alleen voor wachtwoorden)
# * Mogelijk om settings file mee te geven via command-line

# TODO:
# * Locale settings Windows
# * XSLT-transformatie versnellen. De huidige versie is veel minder snel dan transformatie met XML
#   Starlet (die op Windows niet de grootste bladen aankan).
import argparse
import os
import sys
from time import localtime, strftime

# Importeren submodule Stetl, maar moet netter kunnen
sys.path.insert(0, '../../stetl')
from stetl.etl import ETL

# Constanten
DEFAULT_STETL_INI = 'etl-top10nl.cfg'
MAX_SPLIT_FEATURES = 30000
MULTI_OPTS = {'eerste': '-splitlistfields -maxsubfields 1', 'meerdere': '-splitlistfields', 'stringlist': '-fieldTypeToString StringList', 'array': ' ' }

def elaborate_args(args):
	### Controle argumenten

	# Check geldigheid dir
	if not os.path.isdir(args.temp_dir):
		print 'De opgegeven lokatie `%s` is geen geldige directory' % args.temp_dir
		sys.exit(1)

# 	args.gml_files = str(args.gml_files)
	# Converteer string array naar comma-separated string
	# http://stackoverflow.com/questions/438684/how-to-convert-a-list-of-longs-into-a-comma-separated-string-in-python
	args.gml_files  = str(args.gml_files)[1:-1].replace("\'","")

	# Evt via commandline met default
	args.max_features = MAX_SPLIT_FEATURES
	args.multi_opts = MULTI_OPTS[args.multi_opts]
	return vars(args)


# Verwerkt de data via Stetl
def process(args):
	etl = ETL(args, args)
	etl.run()

def main():
	# Samenstellen command line parameters
	argparser = argparse.ArgumentParser(description='Verwerk een of meerdere GML-bestanden')
	argparser.add_argument('gml_files', type=str, help='het GML-bestand of de lijst met GML-bestanden', metavar='gml_files',
		nargs='+')
	argparser.add_argument('--dir', type=str, help='lokatie getransformeerde bestanden', dest='temp_dir', required=True)
	argparser.add_argument('--ini', type=str, help='het Stetl config-bestand (default: %s)' % DEFAULT_STETL_INI, dest='config_file',
		default=DEFAULT_STETL_INI)
	#    argparser.add_argument('--pre',   type=str,   help='SQL-script vooraf', dest='pre_sql')
	#    argparser.add_argument('--post',  type=str,   help='SQL-script achteraf', dest='post_sql')
#	argparser.add_argument('--spat', type=float, help='spatial filter', dest='spat', nargs=4, metavar=('xmin', 'ymin', 'xmax', 'ymax'))
	argparser.add_argument('--multi', type=str, help='multi-attributen (default: eerste)',
		choices=['eerste', 'meerdere', 'stringlist', 'array'], dest='multi_opts', default='eerste')
	#    argparser.add_argument('--gfs',   type=str,   help='GFS template-bestand (default: %s)' % GFS_TEMPLATE, dest='gfs_template', default=DEFAULT_GFS_TEMPLATE)

	# Database parameters
	argparser.add_argument('--pg_host', type=str, help='PostgreSQL server host', dest='host', default='localhost')
	argparser.add_argument('--pg_port', type=int, help='PostgreSQL server poort', dest='port', default=5432)
	argparser.add_argument('--pg_db', type=str, help='PostgreSQL database', dest='database', default='top10nl')
	argparser.add_argument('--pg_schema', type=str, help='PostgreSQL schema', dest='schema', default='test')
	argparser.add_argument('--pg_user', type=str, help='PostgreSQL gebruikersnaam', dest='user', default='top10nl')
	argparser.add_argument('--pg_password', type=str, help='PostgreSQL wachtwoord', dest='password', default='top10nl')
	args = argparser.parse_args()

	print 'Begintijd top10-extract:', strftime('%a, %d %b %Y %H:%M:%S', localtime())

	# Argumenten checken/bewerken
	args = elaborate_args(args)

	### Verwerken data
	process(args)

	print 'Eindtijd top10-extract:', strftime('%a, %d %b %Y %H:%M:%S', localtime())

if __name__ == "__main__":
	main()
