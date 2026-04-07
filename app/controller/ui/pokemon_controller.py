#ESTO LO HAGO PERO ESTA MAL, HABRA QUE CAMBIAR
from flask import Blueprint, render_template
from app.controller.model.pokemon_model import PokemonModel

def pokemon_blueprint(db):
    bp = Blueprint("pokemon", __name__)
    model = PokemonModel(db)

    @bp.route("/pokemon")
    def listar_pokemon():
        pokemon = model.get_all()
        return render_template("pokemon.html", pokemon=pokemon)

    return bp
