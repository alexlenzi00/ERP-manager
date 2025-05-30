
import os, json, io, datetime
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session, Response
from db import DB
from models import *
from models.campo import Campo, FormCampi
from models.tabella import Tabella, FormTabelle
from models.macro import Macro, FormMacro
from models.gruppo import Gruppo, FormGruppi
from models.profilo import Profilo, FormProfili
import time
app = Flask(__name__)

app.config["WTF_CSRF_ENABLED"] = False
app.config["SECRET_KEY"] = os.environ.get("ERP_SECRET", "dev-" + os.urandom(16).hex())

OUTPUT_SQL = 'output.sql'

db = DB()
db.init_from_file("config.json")

ENTITY_MAP = {
	"campo": {
		"form": FormCampi,
		"title": "Campo",
		"query": """SELECT I_PK_CAMPO AS ID, A_DESC_CAMPO AS CAMPO, A_NOME_CAMPO AS CAMPO_DB, A_TIPO_CAMPO AS TIPO, A_ALIAS AS ALIAS, A_FLAG_GROUP AS GROUP_BY,
				A_DESC_MACRO AS MACRO, A_DESC_GRUPPI AS GRUPPO, A_DESC_TABELLA AS TABELLA, EC.I_ORDINE AS ORDINE
				FROM ER_CAMPI EC LEFT JOIN ER_MACRO EM ON EC.I_FK_MACROSHOW = EM.I_PK_MACRO
				LEFT JOIN ER_GRUPPI EG ON EG.I_PK_GRUPPI = EC.I_FK_GRUPPO
				LEFT JOIN ER_TABELLE ET ON ET.I_PK_TABELLA = EC.I_FK_TABELLA
				ORDER BY EM.I_ORDINE, EG.I_ORDINE_GRUPPI, EC.I_ORDINE"""
	},
	"tabella": {
		"form": FormTabelle,
		"title": "Tabella",
		"query": "SELECT I_PK_TABELLA AS ID, A_NOME_TABELLA AS TABELLA, A_DESC_TABELLA AS DESCRIZIONE FROM ER_TABELLE ORDER BY I_PK_TABELLA"
	},
	"macro": {
		"form": FormMacro,
		"title": "Macro",
		"query": "SELECT I_PK_MACRO AS ID, A_DESC_MACRO AS MACRO, I_ORDINE AS ORDINE FROM ER_MACRO ORDER BY I_ORDINE"
	},
	"gruppo": {
		"form": FormGruppi,
		"title": "Gruppo",
		"query": "SELECT I_PK_GRUPPI AS ID, A_DESC_GRUPPI AS GRUPPO, I_ORDINE_GRUPPI AS ORDINE FROM ER_GRUPPI ORDER BY 3"
	},
	"profilo": {
		"form": FormProfili,
		"title": "Profilo",
		"query": """SELECT A_NOME AS PROFILO, A_DESC_MACRO AS MACRO FROM ER_MACRO_PROFILI EMP INNER JOIN PROFILO P ON EMP.I_FK_PROFILO = P.I_ID
				INNER JOIN ER_MACRO EM ON EMP.I_FK_MACRO = EM.I_PK_MACRO ORDER BY 1, 2"""
	},
}

# INDEX
@app.route("/")
def index():
	return render_template("index.html", queue_len=len(session.get("queue", [])))

# FAVICON
@app.route("/favicon.ico")
def favicon():
	return send_file("static/favicon.ico", mimetype="image/x-icon")


# CAMPI
@app.route("/campo/add", methods=["GET"])
def campo_get():
	return render_template("aggiungi_campo.html", form=FormCampi(db), queue_len=len(session.get("queue", [])))

@app.route("/campo/add", methods=["POST"])
def campo_post():
	form = FormCampi(db)
	if form.validate_on_submit():
		campo = Campo.daForm(form)
		session.setdefault("queue", []).extend(campo.to_sql(db))
		return redirect(url_for("index"))
	else:
		flash("Errore nella validazione del form", "danger")
		return render_template("aggiungi_campo.html", form=form, queue_len=len(session.get("queue", [])))


# TABELLE
@app.route("/tabella/add", methods=["GET"])
def tabella_get():
	return render_template("aggiungi_tabella.html", form=FormTabelle(db), queue_len=len(session.get("queue", [])))

@app.route("/tabella/add", methods=["POST"])
def tabella_post():
	form = FormTabelle(db)
	if form.validate_on_submit():
		tabella = Tabella.daForm(form)
		session.setdefault("queue", []).extend(tabella.to_sql(db))
		return redirect(url_for("index"))
	else:
		flash("Errore nella validazione del form", "danger")
		return render_template("aggiungi_tabella.html", form=form, queue_len=len(session.get("queue", [])))


# MACRO
@app.route("/macro/add", methods=["GET"])
def macro_get():
	return render_template("aggiungi_macro.html", form=FormMacro(db), queue_len=len(session.get("queue", [])))

@app.route("/macro/add", methods=["POST"])
def macro_post():
	form = FormMacro(db)
	if form.validate_on_submit():
		macro = Macro.daForm(form)
		session.setdefault("queue", []).extend(macro.to_sql(db))
		return redirect(url_for("index"))
	else:
		flash("Errore nella validazione del form", "danger")
		return render_template("aggiungi_macro.html", form=form, queue_len=len(session.get("queue", [])))


# GRUPPI
@app.route("/gruppo/add", methods=["GET"])
def gruppo_get():
	return render_template("aggiungi_gruppo.html", form=FormGruppi(db), queue_len=len(session.get("queue", [])))

@app.route("/gruppo/add", methods=["POST"])
def gruppo_post():
	form = FormGruppi(db)
	if form.validate_on_submit():
		gruppo = Gruppo.daForm(form)
		session.setdefault("queue", []).extend(gruppo.to_sql(db))
		return redirect(url_for("index"))
	else:
		flash("Errore nella validazione del form", "danger")
		return render_template("aggiungi_gruppo.html", form=form, queue_len=len(session.get("queue", [])))


# PROFILI
@app.route("/profilo/add", methods=["GET"])
def profilo_get():
	return render_template("aggiungi_profilo.html", form=FormProfili(db, selected_id=request.args.get("p", type=int)), queue_len=len(session.get("queue", [])))

@app.route("/profilo/add", methods=["POST"])
def profilo_post():
	sel = request.args.get("p", type=int)
	form = FormProfili(db, selected_id=sel)
	if form.validate_on_submit():
		prof = Profilo.daForm(form)
		session.setdefault("queue", []).extend(prof.to_sql(db))
		return redirect(url_for("index"))
	else:
		flash("Errore nella validazione del form", "danger")
		return render_template("aggiungi_profilo.html", form=form, queue_len=len(session.get("queue", [])))


# ENTITY LIST
@app.route("/<entity>/list", methods=["GET"])
def list_entity(entity: str):
	if entity not in ENTITY_MAP:
		flash("Entità sconosciuta", "danger")
		return redirect(url_for("index"))

	qry = ENTITY_MAP[entity]["query"]

	print(f"Executing query for {entity}: {qry}")

	rows = db.fetchall(qry)
	cols = rows[0].keys() if rows else []
	return render_template("table.html", table_name=ENTITY_MAP[entity]["title"], cols=cols, rows=rows)


# SQL QUEUE
def queue_sql(lines: list[str]) -> None:
	"""
	Accoda le query SQL sia in sessione sia nel file OUTPUT_SQL
	(append in coda, creando il file se non esiste).
	"""
	if lines:
		session.setdefault("queue", []).extend(lines)

		with open(OUTPUT_SQL, "a", encoding="utf-8") as fh:
			fh.write("\n".join(lines) + "\n")

@app.route("/download.sql")
def download_sql():
	queue = session.pop("queue", [])

	with open(OUTPUT_SQL, "w", encoding="utf-8") as fh:
		fh.write("\n".join(queue) + "\n")

	return send_file(
		OUTPUT_SQL,
		mimetype="text/sql",
		as_attachment=True,
		download_name=f'update_{time.time()}.sql',
	)

@app.route("/reset")
def reset():
	session.pop("queue", None)
	if os.path.exists(OUTPUT_SQL):
		open(OUTPUT_SQL, "w").close()
	flash("Coda e file SQL azzerati.", "info")
	return redirect(url_for("index"))

if __name__ == "__main__":
	app.run(debug=True)
