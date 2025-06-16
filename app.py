
import os, json, io, datetime
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session, Response
from db import DB
from models import *
from models.campo import Campo, FormCampi
from models.tabella import Tabella, FormTabelle
from models.macro import Macro, FormMacro
from models.gruppo import Gruppo, FormGruppi
from models.profilo import Profilo, FormProfili
from types import SimpleNamespace
import time
app = Flask(__name__)

app.config['WTF_CSRF_ENABLED'] = False
app.config['SECRET_KEY'] = os.environ.get('ERP_SECRET', 'dev-' + os.urandom(16).hex())

OUTPUT_SQL = 'output.sql'
QUERY_IN_CODA = 0

db = DB()
db.init_from_file('config.json')

ENTITY_MAP = {
	'campo': {
		'form': FormCampi,
		'title': 'Campo',
		'query': '''SELECT I_PK_CAMPO AS ID, A_DESC_CAMPO AS CAMPO, A_NOME_CAMPO AS CAMPO_DB, A_TIPO_CAMPO AS TIPO, A_ALIAS AS ALIAS, A_FLAG_GROUP AS GROUP_BY,
				A_DESC_MACRO AS MACRO, A_DESC_GRUPPI AS GRUPPO, A_DESC_TABELLA AS TABELLA, EC.I_ORDINE AS ORDINE
				FROM ER_CAMPI EC LEFT JOIN ER_MACRO EM ON EC.I_FK_MACROSHOW = EM.I_PK_MACRO
				LEFT JOIN ER_GRUPPI EG ON EG.I_PK_GRUPPI = EC.I_FK_GRUPPO
				LEFT JOIN ER_TABELLE ET ON ET.I_PK_TABELLA = EC.I_FK_TABELLA
				ORDER BY EM.I_ORDINE, EG.I_ORDINE_GRUPPI, EC.I_ORDINE''',
		'js': '''<script> $(function(){ visualizza('#a_strquery', $('#a_tipo_campo').val() === 'combofil'); $('#a_tipo_campo').on('change', function(){ visualizza('#a_strquery', this.value === 'combofil'); }); }); </script>'''
	},
	'tabella': {
		'form': FormTabelle,
		'title': 'Tabella',
		'query': 'SELECT I_PK_TABELLA AS ID, A_NOME_TABELLA AS TABELLA, A_DESC_TABELLA AS DESCRIZIONE FROM ER_TABELLE ORDER BY I_PK_TABELLA',
		'js': ''
	},
	'macro': {
		'form': FormMacro,
		'title': 'Macro',
		'query': 'SELECT I_PK_MACRO AS ID, A_DESC_MACRO AS MACRO, I_ORDINE AS ORDINE FROM ER_MACRO ORDER BY I_ORDINE',
		'js': ''
	},
	'gruppo': {
		'form': FormGruppi,
		'title': 'Gruppo',
		'query': 'SELECT I_PK_GRUPPI AS ID, A_DESC_GRUPPI AS GRUPPO, I_ORDINE_GRUPPI AS ORDINE FROM ER_GRUPPI ORDER BY 3',
		'js': ''
	},
	'profilo': {
		'form': FormProfili,
		'title': 'Profilo',
		'query': '''SELECT P.I_ID AS ID, P.A_NOME AS PROFILO,
				/* MACRO DISTINCTE per profilo */
				COALESCE(
				(
					SELECT STRING_AGG(m.A_DESC_MACRO, ', ') WITHIN GROUP (ORDER BY m.A_DESC_MACRO)
					FROM (
					SELECT DISTINCT EM.A_DESC_MACRO
					FROM ER_MACRO_PROFILI EMP
					JOIN ER_MACRO EM
						ON EM.I_PK_MACRO = EMP.I_FK_MACRO
					WHERE EMP.I_FK_PROFILO = P.I_ID
					) AS m
				),
				''
				) AS MACRO,

				/* CAMPI DISTINCTI per profilo */
				COALESCE(
				(
					SELECT STRING_AGG(c.A_DESC_CAMPO, ', ') WITHIN GROUP (ORDER BY c.A_DESC_CAMPO)
					FROM (
					SELECT DISTINCT EC.A_DESC_CAMPO
					FROM ER_CAMPI_PROFILI ECP
					JOIN ER_CAMPI EC
						ON EC.I_PK_CAMPO = ECP.I_FK_CAMPO
					WHERE ECP.I_FK_PROFILO = P.I_ID
					) AS c
				),
				''
				) AS CAMPI

			FROM PROFILO P
			ORDER BY P.I_ID
		''',
		'js': ''
	}
}

# INDEX
@app.route('/')
def index():
	return render_template('index.html', queue_len=QUERY_IN_CODA)

# FAVICON
@app.route('/favicon.ico')
def favicon():
	return send_file('static/favicon.ico', mimetype='image/x-icon')


# CAMPI
@app.route('/campo/add', methods=['GET'])
def campo_add_get():
	return render_template('add_entity.html', form=FormCampi(db), title='Aggiungi Campo', js=ENTITY_MAP['campo']['js'], queue_len=QUERY_IN_CODA)

@app.route('/campo/add', methods=['POST'])
def campo_add_post():
	form = FormCampi(db)
	if form.validate_on_submit():
		campo = Campo.daForm(form)
		# eseguo update
		for q in campo.to_sql(db):
			aggiungi_sql(q)
		return redirect(url_for('index'))
	flash('Errore nella validazione del form', 'danger')
	return render_template('add_entity.html', form=form, title='Aggiungi Campo', js=ENTITY_MAP['campo']['js'], queue_len=QUERY_IN_CODA)

@app.route('/campo/edit/<int:id>', methods=['GET'])
def campo_edit_get(id: int):
	data = db.fetchone('SELECT * FROM ER_CAMPI WHERE I_PK_CAMPO = ?', (id,))
	if not data:
		flash('Campo non trovato', 'danger')
		return redirect(url_for('index'))
	form = FormCampi(db, editing=True, tasto='Modifica Campo')
	form.process(data={k.lower(): v for k, v in data.items()})

	return render_template('edit_entity.html', form=form, title='Modifica Campo', entity='campo', js=ENTITY_MAP['campo']['js'], queue_len=QUERY_IN_CODA)

@app.route('/campo/edit/<int:id>', methods=['POST'])
def campo_edit_post(id: int):
	form = FormCampi(db, editing=True, tasto='Modifica Campo')
	if form.validate_on_submit():
		# eseguo update
		for q in Campo.daForm(form).to_sql(db):
			aggiungi_sql(q)
		return redirect(url_for('index'))
	else:
		flash('Errore nella validazione del form', 'danger')
		return render_template('edit_entity.html', form=form, title='Modifica Campo', entity='campo', js=ENTITY_MAP['campo']['js'], queue_len=QUERY_IN_CODA)


# TABELLE
@app.route('/tabella/add', methods=['GET'])
def tabella_get():
	return render_template('add_entity.html', form=FormTabelle(db), title='Aggiungi Tabella', js=ENTITY_MAP['tabella']['js'], queue_len=QUERY_IN_CODA)

@app.route('/tabella/add', methods=['POST'])
def tabella_post():
	form = FormTabelle(db)
	if form.validate_on_submit():
		tabella = Tabella.daForm(form)
		# eseguo update
		for q in tabella.to_sql(db):
			aggiungi_sql(q)
		return redirect(url_for('index'))
	else:
		flash('Errore nella validazione del form', 'danger')
		return render_template('add_entity.html', form=form, title='Aggiungi Tabella', js=ENTITY_MAP['tabella']['js'], queue_len=QUERY_IN_CODA)

@app.route('/tabella/edit/<int:id>', methods=['GET'])
def tabella_edit_get(id: int):
	data = db.fetchone('SELECT * FROM ER_TABELLE WHERE I_PK_TABELLA = ?', (id,))
	if not data:
		flash('Tabella non trovata', 'danger')
		return redirect(url_for('index'))
	form = FormTabelle(db, editing=True, tasto='Modifica Tabella')
	form.process(data={k.lower(): v for k, v in data.items()})

	return render_template('edit_entity.html', form=form, title='Modifica Tabella', entity='tabella', js=ENTITY_MAP['tabella']['js'], queue_len=QUERY_IN_CODA)

@app.route('/tabella/edit/<int:id>', methods=['POST'])
def tabella_edit_post(id: int):
	form = FormTabelle(db, editing=True, tasto='Modifica Tabella')
	if form.validate_on_submit():
		# eseguo update
		for q in Tabella.daForm(form).to_sql(db):
			aggiungi_sql(q)
		return redirect(url_for('index'))
	flash('Errore nella validazione del form', 'danger')
	return render_template('edit_entity.html', form=form, title='Modifica Tabella', entity='tabella', js=ENTITY_MAP['tabella']['js'], queue_len=QUERY_IN_CODA)


# MACRO
@app.route('/macro/add', methods=['GET'])
def macro_get():
	return render_template('add_entity.html', form=FormMacro(db), title='Aggiungi Macro', js=ENTITY_MAP['macro']['js'], queue_len=QUERY_IN_CODA)

@app.route('/macro/add', methods=['POST'])
def macro_post():
	form = FormMacro(db)
	if form.validate_on_submit():
		macro = Macro.daForm(form)
		# eseguo update
		for q in macro.to_sql(db):
			aggiungi_sql(q)
		return redirect(url_for('index'))
	flash('Errore nella validazione del form', 'danger')
	return render_template('add_entity.html', form=form, title='Aggiungi Macro', js=ENTITY_MAP['macro']['js'], queue_len=QUERY_IN_CODA)

@app.route('/macro/edit/<int:id>', methods=['GET'])
def macro_edit_get(id: int):
	data = db.fetchone('SELECT * FROM ER_MACRO WHERE I_PK_MACRO = ?', (id,))
	if not data:
		flash('Macro non trovata', 'danger')
		return redirect(url_for('index'))
	form = FormMacro(db, editing=True, tasto='Modifica Macro')
	form.process(data={k.lower(): v for k, v in data.items()})

	return render_template('edit_entity.html', form=form, title='Modifica Macro', entity='macro', js=ENTITY_MAP['macro']['js'], queue_len=QUERY_IN_CODA)

@app.route('/macro/edit/<int:id>', methods=['POST'])
def macro_edit_post(id: int):
	form = FormMacro(db, editing=True, tasto='Modifica Macro')
	if form.validate_on_submit():
		# eseguo update
		for q in Macro.daForm(form).to_sql(db):
			aggiungi_sql(q)
		return redirect(url_for('index'))
	flash('Errore nella validazione del form', 'danger')
	return render_template('edit_entity.html', form=form, title='Modifica Macro', entity='macro', js=ENTITY_MAP['macro']['js'], queue_len=QUERY_IN_CODA)


# GRUPPI
@app.route('/gruppo/add', methods=['GET'])
def gruppo_get():
	return render_template('add_entity.html', form=FormGruppi(db), title='Aggiungi Gruppo', js=ENTITY_MAP['gruppo']['js'], queue_len=QUERY_IN_CODA)

@app.route('/gruppo/add', methods=['POST'])
def gruppo_post():
	form = FormGruppi(db)
	if form.validate_on_submit():
		gruppo = Gruppo.daForm(form)
		# eseguo update
		for q in gruppo.to_sql(db):
			aggiungi_sql(q)
		return redirect(url_for('index'))
	flash('Errore nella validazione del form', 'danger')
	return render_template('add_entity.html', form=form, title='Aggiungi Gruppo', js=ENTITY_MAP['gruppo']['js'], queue_len=QUERY_IN_CODA)

@app.route('/gruppo/edit/<int:id>', methods=['GET'])
def gruppo_edit_get(id: int):
	data = db.fetchone('SELECT * FROM ER_GRUPPI WHERE I_PK_GRUPPI = ?', (id,))
	if not data:
		flash('Gruppo non trovato', 'danger')
		return redirect(url_for('index'))
	form = FormGruppi(db, editing=True, tasto='Modifica Gruppo')
	form.process(data={k.lower(): v for k, v in data.items()})
	form.submit.label.text = 'Modifica Gruppo'

	return render_template('edit_entity.html', form=form, title='Modifica Gruppo', entity='gruppo', js=ENTITY_MAP['gruppo']['js'], queue_len=QUERY_IN_CODA)

@app.route('/gruppo/edit/<int:id>', methods=['POST'])
def gruppo_edit_post(id: int):
	form = FormGruppi(db, editing=True, tasto='Modifica Gruppo')
	if form.validate_on_submit():
		# eseguo update
		for q in Gruppo.daForm(form).to_sql(db):
			aggiungi_sql(q)
		return redirect(url_for('index'))
	flash('Errore nella validazione del form', 'danger')
	return render_template('edit_entity.html', form=form, title='Modifica Gruppo', entity='gruppo', js=ENTITY_MAP['gruppo']['js'], queue_len=QUERY_IN_CODA)


# PROFILI
@app.route('/profilo/add', methods=['GET'])
def profilo_get():
	return render_template('add_entity.html', form=FormProfili(db), title='Gestisci Profilo', js=ENTITY_MAP['profilo']['js'], queue_len=QUERY_IN_CODA)

@app.route('/profilo/add', methods=['POST'])
def profilo_post():
	form = FormProfili(db)
	if form.validate_on_submit():
		prof = Profilo.daForm(form)
		# eseguo update
		for q in prof.to_sql(db):
			aggiungi_sql(q)
		return redirect(url_for('index'))
	else:
		flash('Errore nella validazione del form', 'danger')
		return render_template('add_entity.html', form=form, title='Gestisci Profilo', js=ENTITY_MAP['profilo']['js'], queue_len=QUERY_IN_CODA)

@app.route('/profilo/edit/<int:id>', methods=['GET'])
def profilo_edit_get(id: int):
	data = db.fetchone('SELECT * FROM PROFILO WHERE I_ID = ?', (id,))
	if not data:
		flash('Profilo non trovato', 'danger')
		return redirect(url_for('index'))
	form = FormProfili(db, editing=True, tasto='Modifica Profilo')
	form.process(data={k.lower(): v for k, v in data.items()})

	return render_template('edit_entity.html', form=form, title='Modifica Profilo', entity='profilo', js=ENTITY_MAP['profilo']['js'], queue_len=QUERY_IN_CODA)

@app.route('/profilo/edit/<int:id>', methods=['POST'])
def profilo_edit_post(id: int):
	form = FormProfili(db, editing=True, tasto='Modifica Profilo')
	if form.validate_on_submit():
		# eseguo update
		for q in Profilo.daForm(form).to_sql(db):
			aggiungi_sql(q)
		return redirect(url_for('index'))
	flash('Errore nella validazione del form', 'danger')
	return render_template('edit_entity.html', form=form, title='Modifica Profilo', entity='profilo', js=ENTITY_MAP['profilo']['js'], queue_len=QUERY_IN_CODA)


@app.route('/<entity>/edit/<int:id>', methods=['GET'])
def edit_entity(entity: str, id: int, js : str = ''):
	return render_template('edit_entity.html', entity=entity, id=id, form=ENTITY_MAP[entity]['form'](db, id), title=f'Edit {ENTITY_MAP[entity]["title"]}', js=js, queue_len=QUERY_IN_CODA)


# ENTITY LIST
@app.route('/<entity>/list', methods=['GET'])
def list_entity(entity: str):
	if entity not in ENTITY_MAP:
		flash('Entità sconosciuta', 'danger')
		return redirect(url_for('index'))

	qry = ENTITY_MAP[entity]['query']

	rows = db.fetchall(qry)
	cols = rows[0].keys() if rows else []
	return render_template('table.html', table_name=ENTITY_MAP[entity]['title'], js=ENTITY_MAP[entity]['js'], cols=cols, rows=rows)


@app.route('/download.sql', methods=['GET'])
def download_sql():
	return send_file(
		OUTPUT_SQL,
		mimetype='text/sql',
		as_attachment=True,
		download_name=f'update_{time.time()}.sql',
	)

@app.route('/reset')
def reset():
	global QUERY_IN_CODA
	QUERY_IN_CODA = 0
	if os.path.exists(OUTPUT_SQL):
		open(OUTPUT_SQL, 'w').close()
	flash('File SQL azzerato.', 'info')
	return redirect(url_for('index'))

def aggiungi_sql(sql: str) -> None:
	'''
	Aggiunge una query SQL nel file OUTPUT_SQL e la esegue.
	'''
	global QUERY_IN_CODA
	if sql:
		with open(OUTPUT_SQL, 'a', encoding='utf-8') as fh:
			fh.write(sql + '\n')
		QUERY_IN_CODA += 1
		db.upsert(sql)

if __name__ == '__main__':
	app.run(debug=True)
