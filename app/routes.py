from flask import Blueprint, render_template, request, redirect, url_for
from app.models import db, Atleta, Entrenamiento
from datetime import datetime, timedelta
import calendar

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return redirect(url_for('main.dashboard'))

@main.route('/dashboard')
def dashboard():
    atletas = Atleta.query.all()
    entrenamientos = Entrenamiento.query.all()
    hoy = datetime.today()
    year = hoy.year
    month = hoy.month
    semanas = calendar.Calendar().monthdayscalendar(year, month)

    atleta_seleccionado = request.args.get('atleta')
    return render_template(
        'dashboard.html',
        atletas=atletas,
        entrenamientos=entrenamientos,
        calendario_mensual=semanas,
        mes=month,
        anio=year,
        atleta_seleccionado=atleta_seleccionado
    )

@main.route('/nuevo_entrenamiento', methods=['POST'])
def nuevo_entrenamiento():
    nombre_atleta = request.form['atleta']
    atleta = Atleta.query.filter_by(nombre=nombre_atleta).first()
    if atleta:
        nuevo = Entrenamiento(
            atleta=atleta,
            fecha=datetime.strptime(request.form['fecha'], '%Y-%m-%d').date(),
            tipo=request.form['tipo'],
            detalle=request.form['detalle']
        )
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('main.dashboard', atleta=nombre_atleta))
    return "Atleta no encontrado", 404

@main.route('/borrar_entrenamiento/<int:id>', methods=['POST'])
def borrar_entrenamiento(id):
    entrenamiento = Entrenamiento.query.get(id)
    if entrenamiento:
        nombre = entrenamiento.atleta.nombre
        db.session.delete(entrenamiento)
        db.session.commit()
        return redirect(url_for('main.dashboard', atleta=nombre))
    return "Entrenamiento no encontrado", 404

@main.route('/perfil/<int:id>')
def perfil(id):
    atleta = Atleta.query.get_or_404(id)
    hoy = datetime.today().date()
    hace_7_dias = hoy - timedelta(days=7)

    # Entrenamientos en la última semana
    entrenos_semana = Entrenamiento.query.filter(
        Entrenamiento.atleta_id == atleta.id,
        Entrenamiento.fecha >= hace_7_dias,
        Entrenamiento.fecha <= hoy
    ).all()

    total = len(entrenos_semana)
    realizados = len([e for e in entrenos_semana if e.fecha < hoy])
    progreso = int((realizados / total) * 100) if total > 0 else 0

    return render_template(
        'perfil.html',
        atleta=atleta,
        hoy=hoy,
        progreso_semana=progreso
    )

@main.route('/actualizar_tiempos/<int:id>', methods=['POST'])
def actualizar_tiempos(id):
    atleta = Atleta.query.get_or_404(id)
    atleta.pr_1000m = request.form.get('pr_1000m')
    atleta.pr_10k = request.form.get('pr_10k')
    atleta.pr_21k = request.form.get('pr_21k')
    atleta.pr_42k = request.form.get('pr_42k')
    db.session.commit()
    return redirect(url_for('main.perfil', id=id))
