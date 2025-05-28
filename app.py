
import os, json, io, datetime
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session, Response
from db import DB
from sql_generator import SQLGenerator
from models import *
from models.campo import Campo, FormCampi
from models.tabella import Tabella, FormTabelle
from models.macro import Macro, FormMacro
from models.gruppo import Gruppo, FormGruppi
from models.profilo import Profilo, FormProfili

app = Flask(__name__)

app.config["WTF_CSRF_ENABLED"] = False
app.config["SECRET_KEY"] = os.environ.get("ERP_SECRET", "dev-" + os.urandom(16).hex())

OUTPUT_SQL = 'output.sql'

db = DB()
db.init_from_file("config.json")

gen = SQLGenerator()

ENTITY_MAP = {
	"campo": {"form": FormCampi, "title": "Campo", "table": "ER_CAMPI"},
	"tabella": {"form": FormTabelle, "title": "Tabella", "table": "ER_TABELLE"},
	"macro": {"form": FormMacro, "title": "Macro", "table": "ER_MACRO"},
	"gruppo": {"form": FormGruppi, "title": "Gruppo", "table": "ER_GRUPPI"},
	"profilo": {"form": FormProfili, "title": "Profilo", "table": "PROFILO"},
}

# INDEX
@app.route("/")
def index():
	return render_template("index.html", queue_len=len(session.get("queue", [])))


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
		macro = Macro.from_form(form)
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
		gruppo = Gruppo.from_form(form)
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
		prof = Profilo.from_form(form)
		session.setdefault("queue", []).extend(prof.to_sql(db))
		return redirect(url_for("index"))
	else:
		flash("Errore nella validazione del form", "danger")
		return render_template("aggiungi_profilo.html", form=form, queue_len=len(session.get("queue", [])))


def queue_sql(lines: list[str]) -> None:
	"""
	Accoda le query SQL sia in sessione sia nel file OUTPUT_SQL
	(append in coda, creando il file se non esiste).
	"""
	if lines:
		session.setdefault("queue", []).extend(lines)

		with open(OUTPUT_SQL, "a", encoding="utf-8") as fh:
			fh.write("\n".join(lines) + "\n")


@app.route("/<entity>/add", methods=["GET", "POST"])
def add_entity(entity):
	if entity not in ENTITY_MAP:
		flash("Entità sconosciuta", "danger")
		return redirect(url_for("index"))

	FormClass = ENTITY_MAP[entity]["form"]
	form = FormClass(db)  # passiamo il db per select dinamiche

	if form.validate_on_submit():
		data = form.to_dict()
		pending = session.setdefault("pending", {})
		pending.setdefault(entity, []).append(data)
		session.modified = True
		flash(f"{ENTITY_MAP[entity]['title']} aggiunto alla coda", "success")
		return redirect(url_for("index"))

	return render_template("add_entity.html", form=form, entity=entity, cfg=ENTITY_MAP[entity])

@app.route("/download.sql")
def download_sql():
	queue = session.pop("queue", [])

	if not queue:
		flash("Nessuna query da esportare", "warning")
		return redirect(url_for("index"))

	with open(OUTPUT_SQL, "a", encoding="utf-8") as fh:
		fh.write("\n".join(queue) + "\n")

	return send_file(
		OUTPUT_SQL,
		mimetype="text/sql",
		as_attachment=True,
		download_name="pendings.sql",
	)

@app.route("/reset")
def reset():
	session.pop("queue", None)
	if os.path.exists(OUTPUT_SQL):
		open(OUTPUT_SQL, "w").close()
	flash("Coda e file SQL azzerati.", "info")
	return redirect(url_for("index"))

# ----------------------------------------------------------------------------
if __name__ == "__main__":
	app.run(debug=True)
